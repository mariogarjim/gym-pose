import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { CfnOutput, Duration, RemovalPolicy, Size } from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as path from 'path';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';

export class ArchitectureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // 1) Create the S3 bucket to store the videos
    const videoBucket = new s3.Bucket(this, 'VideoBucket', {
      bucketName: 'gym-pose-videos-bucket',
      lifecycleRules: [
        {
          transitions: [
            {
              storageClass: s3.StorageClass.INTELLIGENT_TIERING,
              transitionAfter: cdk.Duration.days(30),
            },
          ],
        },
      ],
    });

    // 2) SQS + DLQ
    const dlq = new sqs.Queue(this, 'IngestDLQ', {
      retentionPeriod: Duration.days(14),
      enforceSSL: true,
    });

    const ingestQueue = new sqs.Queue(this, 'IngestQueue', {
      visibilityTimeout: Duration.minutes(10),
      retentionPeriod: Duration.days(14),
      deadLetterQueue: {
        queue: dlq,
        maxReceiveCount: 3,
      },
      enforceSSL: true,
    });

    // 3) S3 event notification when a new video is uploaded
    videoBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(ingestQueue),
      { prefix: 'raw/', suffix: '.zip' }
    );

    // 4) DynamoDB table for metadata and resultss
    const analysesTable = new dynamodb.Table(this, 'AnalysesTable', {
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      timeToLiveAttribute: 'ttl',
      removalPolicy: RemovalPolicy.RETAIN,
    });

    // 5) Lambda Worker (container) -> path ../worker
    //    Expects a Dockerfile with ffmpeg + Python + the model.
    // Lambda Worker: heavy async processing; triggered by SQS after upload to S3, runs ffmpeg/model, stores results in S3 and updates DynamoDB.
    const worker = new lambda.DockerImageFunction(this, 'WorkerFunction', {
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '..', '..'), {
        file: 'architecture/worker/Dockerfile',
      }),
      memorySize: 4096, // ajusta según tu modelo
      timeout: Duration.minutes(10),
      architecture: lambda.Architecture.X86_64,
      environment: {
        BUCKET: videoBucket.bucketName,
        TABLE: analysesTable.tableName,

        // Avoid spikes and saturation by threads
        OMP_NUM_THREADS: '1',
        OPENBLAS_NUM_THREADS: '1',
        NUMEXPR_NUM_THREADS: '1',
        TF_NUM_INTRAOP_THREADS: '1',
        TF_NUM_INTEROP_THREADS: '1',

        // Silence TF logs and write matplotlib warnings into a writable directory
        TF_CPP_MIN_LOG_LEVEL: '2',
        MPLCONFIGDIR: '/tmp/mpl',
      },
      ephemeralStorageSize: Size.gibibytes(10),
      loggingFormat: lambda.LoggingFormat.JSON,
      logRetention: logs.RetentionDays.ONE_WEEK,
    });

    // Lambda Worker is subscribed to the SQS queue
    worker.addEventSource(
      new lambdaEventSources.SqsEventSource(ingestQueue, {
        batchSize: 1,
        maxBatchingWindow: Duration.seconds(0),
        reportBatchItemFailures: true,
      })
    );

    // Permisos mínimos
    videoBucket.grantReadWrite(worker);
    analysesTable.grantReadWriteData(worker);
    ingestQueue.grantConsumeMessages(worker);

    // 6) Lambda API: exposes HTTP endpoints (upload-url/status/result), lightweight logic; validates auth and reads/writes DynamoDB and S3.
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

     // Permisos para generar pre-signed (Put en raw/, Get en results/)
    videoBucket.grantWrite(apiFn); // PutObject en raw/
    videoBucket.grantRead(apiFn);  // GetObject en results/
    analysesTable.grantReadData(apiFn);

    // 7) API Gateway
    const api = new apigw.LambdaRestApi(this, 'HttpApi', {
      handler: apiFn,
      proxy: true, // la Lambda resuelve rutas /videos/*
      deployOptions: {
        tracingEnabled: false,
        loggingLevel: apigw.MethodLoggingLevel.INFO,
        dataTraceEnabled: false,
      },
    });

    // 8) API Gateway endpoints
    new CfnOutput(this, 'BucketName', { value: videoBucket.bucketName });
    new CfnOutput(this, 'QueueUrl', { value: ingestQueue.queueUrl });
    new CfnOutput(this, 'ApiUrl', { value: api.url });
    new CfnOutput(this, 'DynamoTable', { value: analysesTable.tableName });
    
  }
}
