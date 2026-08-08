FROM python:3.11-slim

WORKDIR /app

# Only the web front end needs Flask; the backend is standard library only.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend.py app.py ./

EXPOSE 8000 5000

# The backend starts in the background, then the front end replaces the shell so
# that it receives the stop signal directly.
CMD ["sh", "-c", "python backend.py & exec python app.py"]
