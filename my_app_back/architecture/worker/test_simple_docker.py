import subprocess, time, requests, json

print("=== Building Docker Image ===")
# Build the image first
build_result = subprocess.run(
    ["docker", "build", "-f", "Dockerfile", "-t", "lambda-worker-test", "../../"],
    capture_output=True,
    text=True,
)

if build_result.returncode != 0:
    print(f"❌ Docker build failed: {build_result.stderr}")
    exit(1)

print("✅ Docker image built successfully!")

event = {
    "Records": [
        {
            "body": json.dumps(
                {
                    "Records": [
                        {
                            "s3": {
                                "bucket": {"name": "test-bucket"},
                                "object": {"key": "raw/user123/squat/test.mp4"},
                            }
                        }
                    ]
                }
            )
        }
    ]
}

print("\n=== Starting Lambda Container ===")
# Start container
proc = subprocess.Popen(
    [
        "docker",
        "run",
        "--rm",
        "-p",
        "9000:8080",
        "-e",
        "BUCKET=test-bucket",
        "-e",
        "TABLE=test-table",
        "-e",
        "AWS_ACCESS_KEY_ID=test",
        "-e",
        "AWS_SECRET_ACCESS_KEY=test",
        "-e",
        "AWS_DEFAULT_REGION=us-east-1",
        "lambda-worker-test",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

print("⏳ Waiting for container to start...")
time.sleep(3)  # give container time to start

print("\n=== Invoking Lambda Function ===")
try:
    # Send event to Lambda Runtime API
    resp = requests.post(
        "http://localhost:9000/2015-03-31/functions/function/invocations",
        json=event,
        timeout=10,
    )
    print("✅ Response:", resp.json())
except Exception as e:
    print(f"❌ Error invoking function: {e}")

print("\n=== Stopping Container ===")
proc.terminate()

# Get container logs
try:
    stdout, stderr = proc.communicate(timeout=5)
    if stdout:
        print(f"\n=== Container Output ===\n{stdout}")
    if stderr:
        print(f"\n=== Container Errors ===\n{stderr}")
except subprocess.TimeoutExpired:
    proc.kill()
    print("Container forcefully killed")
