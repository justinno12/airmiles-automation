FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Installeer Playwright browsers en dependencies
RUN python -m playwright install --with-deps

COPY . .

CMD ["python", "main.py"]
