# Garage: shared S3-compatible dataset
FROM dxflrs/garage:v1.0.1 AS garage-bin

FROM alpine:3.19
COPY --from=garage-bin /garage /garage
COPY garage.toml /etc/garage.toml
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
