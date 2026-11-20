FROM mcr.microsoft.com/devcontainers/base:bookworm

ENV ELAN_HOME=/home/vscode/.elan
ENV PATH="/home/vscode/.elan/bin:/home/vscode/.venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        gnupg \
        libgmp-dev \
        pkg-config \
        python3 \
        python3-pip \
        python3-venv \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        -o /tmp/google-cloud-apt-key.gpg \
    && gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg /tmp/google-cloud-apt-key.gpg \
    && rm /tmp/google-cloud-apt-key.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
        > /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-cloud-cli \
    && gcloud --version \
    && mkdir -p "${ELAN_HOME}" \
    && chown vscode:vscode "${ELAN_HOME}" \
    && rm -rf /var/lib/apt/lists/*
