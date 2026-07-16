FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY extract_lineart.py ./

ENTRYPOINT ["python", "extract_lineart.py"]
