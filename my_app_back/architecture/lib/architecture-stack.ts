import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as apigw from 'aws-cdk-lib/aws-apigateway';

import { CfnOutput, Duration, RemovalPolicy, Size } from 'aws-cdk-lib';
import * as path from 'path';

export class ArchitectureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // =========================================================================
    // 0) API Gateway -> CloudWatch Logs account role (FIX for your error)
    // =========================================================================
    const apiGwLogsRole = new iam.Role(this, 'ApiGwLogsRole', {
      assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'service-role/AmazonAPIGatewayPushToCloudWatchLogs',
        ),
      ],
      // name is optional; let CDK name it to avoid collisions
    });

    const apiGwAccount = new apigw.CfnAccount(this, 'ApiGatewayAccount', {
      cloudWatchRoleArn: apiGwLogsRole.roleArn,
    });

    // =========================================================================
    // 1) S3 bucket for videos (unique per account & region)
    // =========================================================================
    const bucketName = `gym-pose-videos-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`;

    const videoBucket = new s3.Bucket(this, 'VideoBucket', {
      bucketName,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      lifecycleRules: [
        {
          transitions: [
            {
              storageClass: s3.StorageClass.INTELLIGENT_TIERING,
              transitionAfter: Duration.days(30),
            },
          ],
        },
      ],
      // Keep data by default; change to DESTROY for ephemeral envs:
      removalPolicy: RemovalPolicy.RETAIN,
      autoDeleteObjects: false,
    });

    // =========================================================================
    // 2) SQS + DLQ
    // =========================================================================
    const dlq = new sqs.Queue(this, 'IngestDLQ', {
      retentionPeriod: Duration.days(14),
      enforceSSL: true,
    });

    const ingestQueue = new sqs.Queue(this, 'IngestQueue', {
      visibilityTimeout: Duration.minutes(10),
      retentionPeriod: Duration.days(14),
      deadLetterQueue: { queue: dlq, maxReceiveCount: 3 },
      enforceSSL: true,
    });

    // =========================================================================
    // 3) S3 event notification -> SQS (prefix raw/, zip uploads)
    // =========================================================================
    videoBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(ingestQueue),
      { prefix: 'raw/', suffix: '.zip' },
    );

    // =========================================================================
    // 4) DynamoDB table (PK/SK, TTL)
    // =========================================================================
    const analysesTable = new dynamodb.Table(this, 'AnalysesTable', {
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      timeToLiveAttribute: 'ttl',
      removalPolicy: RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
    });

    // =========================================================================
    // 5) Lambda Worker (Docker image)
    // =========================================================================
    const worker = new lambda.DockerImageFunction(this, 'WorkerFunction', {
      code: lambda.DockerImageCode.fromImageAsset(
        // adjust to your project layout; this assumes repo root has /architecture/worker/Dockerfile
        path.join(__dirname, '..', '..'),
        { file: 'architecture/worker/Dockerfile' },
      ),
      memorySize: 3008,
      timeout: Duration.minutes(10),
      architecture: lambda.Architecture.X86_64,
      ephemeralStorageSize: Size.gibibytes(10),
      environment: {
        BUCKET: videoBucket.bucketName,
        TABLE: analysesTable.tableName,

        OMP_NUM_THREADS: '1',
        OPENBLAS_NUM_THREADS: '1',
        NUMEXPR_NUM_THREADS: '1',
        TF_NUM_INTRAOP_THREADS: '1',
        TF_NUM_INTEROP_THREADS: '1',
        TF_CPP_MIN_LOG_LEVEL: '2',
        MPLCONFIGDIR: '/tmp/mpl',
      },
      loggingFormat: lambda.LoggingFormat.JSON,
      logRetention: logs.RetentionDays.ONE_WEEK,
    });

    // Subscribe Worker to SQS
    worker.addEventSource(new lambdaEventSources.SqsEventSource(ingestQueue, {
      batchSize: 1,
      maxBatchingWindow: Duration.seconds(0),
      reportBatchItemFailures: true,
    }));

    // Minimal permissions
    videoBucket.grantReadWrite(worker);
    analysesTable.grantReadWriteData(worker);
    ingestQueue.grantConsumeMessages(worker);

    // =========================================================================
    // 6) Lambda API (lightweight)
    // =========================================================================
    const apiFn = new lambda.Function(this, 'ApiFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'app.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '..', 'lambda', 'api')),
      architecture: lambda.Architecture.ARM_64,
      memorySize: 512,
      timeout: Duration.seconds(30),
      environment: {
        BUCKET: videoBucket.bucketName,
        TABLE: analysesTable.tableName,
      },
      loggingFormat: lambda.LoggingFormat.JSON,
      logRetention: logs.RetentionDays.ONE_WEEK,
    });

    videoBucket.grantWrite(apiFn); // PutObject (e.g., pre-signed PUTs to raw/)
    videoBucket.grantRead(apiFn);  // GetObject (e.g., from results/)
    analysesTable.grantReadData(apiFn);

    // =========================================================================
    // 7) API Gateway (REST v1) with execution logging
    //     IMPORTANT: Stage depends on `apigateway::Account` above
    // =========================================================================
    const api = new apigw.LambdaRestApi(this, 'HttpApi', {
      handler: apiFn,
      proxy: true,
      deployOptions: {
        loggingLevel: apigw.MethodLoggingLevel.INFO, // execution logging ON
        dataTraceEnabled: false,
        tracingEnabled: false,
        // You can also add access logs to a specific Log Group if needed:
        // accessLogDestination: new apigw.LogGroupLogDestination(
        //   new logs.LogGroup(this, 'ApiAccessLogs', {
        //     retention: logs.RetentionDays.ONE_WEEK,
        //   }),
        // ),
        // accessLogFormat: apigw.AccessLogFormat.clf(),
      },
    });

    // Ensure Stage/Deployment creation waits for the account-level role to exist
    api.deploymentStage.node.addDependency(apiGwAccount);
    if (api.latestDeployment) {
      api.latestDeployment.node.addDependency(apiGwAccount);
    }

    // =========================================================================
    // 8) Outputs
    // =========================================================================
    new CfnOutput(this, 'BucketName', { value: videoBucket.bucketName });
    new CfnOutput(this, 'QueueUrl', { value: ingestQueue.queueUrl });
    new CfnOutput(this, 'ApiUrl', { value: api.url });
    new CfnOutput(this, 'DynamoTable', { value: analysesTable.tableName });
  }
}
