# HTA scan pipeline (ClamAV + YARA)
FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        clamav clamav-freshclam python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY . /app
WORKDIR /app

RUN freshclam || true

RUN chmod +x /app/run_pipeline.sh

ENTRYPOINT ["/app/run_pipeline.sh"]
