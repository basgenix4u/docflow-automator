FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright chromium AND all system dependencies
RUN playwright install chromium --with-deps

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
