FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY gpt.py .
COPY README.md .
COPY LICENSE .
COPY NOTICE .
COPY CHANGELOG.md .
COPY INSTALL .

CMD ["python", "gpt.py"]
