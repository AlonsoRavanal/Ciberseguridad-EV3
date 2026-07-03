FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python create_db.py || true

EXPOSE 5000

CMD ["flask", "--app", "vulnerable_app", "run", "--host=0.0.0.0", "--port=5000"]