FROM alpine:3.20

RUN apk add --no-cache curl

RUN curl -L \
    https://github.com/getsops/sops/releases/download/v3.10.2/sops-v3.10.2.linux.amd64 \
    -o /usr/local/bin/sops && \
    chmod +x /usr/local/bin/sops

WORKDIR /work

ENTRYPOINT ["sops"]