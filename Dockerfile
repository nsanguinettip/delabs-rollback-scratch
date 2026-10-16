FROM python:3.12-alpine@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4
ARG PB_FLAVOR=plain
ARG PB_EXTRA=x
RUN mkdir -p /app && printf '%s' "$PB_FLAVOR" >/app/flavor.txt
COPY app.py /app/
CMD ["python", "/app/app.py"]
