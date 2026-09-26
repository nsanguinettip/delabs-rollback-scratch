FROM python:3.12-slim
RUN exit 1
RUN pip install --no-cache-dir greenlet==3.1.1
COPY app.py /app.py
CMD ["python", "/app.py"]
