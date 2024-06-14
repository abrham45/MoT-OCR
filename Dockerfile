FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update -y
RUN apt-get install tesseract-ocr -y
RUN apt-get install -y tesseract-ocr-amh -y

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]