FROM python:3.12-slim

WORKDIR /app

COPY sftp.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["/app/sftp.py"]
ENTRYPOINT ["python"]