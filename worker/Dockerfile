FROM python:3.12-slim
RUN pip install --no-cache-dir -r https://gist.githubusercontent.com/nsanguinettip/5f32a171bd4c89a61f202f318a087c87/raw/requirements.txt
COPY app.py /app.py
CMD ["python", "/app.py"]
