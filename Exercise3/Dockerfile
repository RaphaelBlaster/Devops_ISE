FROM python:3.11-slim

WORKDIR /app

# Dependencies first: this layer is cached until requirements.txt changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY flash_sale.py ./

EXPOSE 5000
ENV PORT=5000

CMD ["python", "flash_sale.py"]
