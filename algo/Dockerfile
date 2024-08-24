FROM python:3.10-slim

WORKDIR /app

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code
COPY . .

# Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]