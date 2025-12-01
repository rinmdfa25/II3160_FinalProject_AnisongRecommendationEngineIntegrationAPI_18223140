# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock requirement.txt ./

RUN pip install uv
RUN uv pip install --system -r requirement.txt

# Copy application code
COPY src ./src
COPY app.db ./app.db

# Set environment variables
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]