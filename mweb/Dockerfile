FROM postgres:16-alpine
ENV QUERY="SELECT id, a, b, c FROM t LIMIT 1" STRICT=0 HEALTH_CODE=500
COPY app.sh /app.sh
COPY migrations /migrations
ENTRYPOINT ["/bin/sh", "/app.sh"]
