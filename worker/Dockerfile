FROM python:3.12-slim
LABEL rb.version=v7
RUN pip install --no-cache-dir greenlet==3.1.1
COPY app.py /app.py
CMD ["sh", "-c", "sleep 90 && python /app.py"]
