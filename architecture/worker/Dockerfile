FROM public.ecr.aws/lambda/python:3.12

# ffmpeg (static amd64 build) — usa el curl ya incluido
RUN dnf install -y tar xz && dnf clean all && \
    curl -L -o /tmp/ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    mkdir -p /opt/ffmpeg && \
    tar -xJf /tmp/ffmpeg.tar.xz -C /opt/ffmpeg --strip-components=1 && \
    ln -s /opt/ffmpeg/ffmpeg /usr/local/bin/ffmpeg && \
    ln -s /opt/ffmpeg/ffprobe /usr/local/bin/ffprobe && \
    rm /tmp/ffmpeg.tar.xz

# Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Código
COPY worker_lambda_function.py ${LAMBDA_TASK_ROOT}/
CMD ["worker_lambda_function.lambda_handler"]
