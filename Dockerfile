# DBMigration application Dockerfile
#
# Builds a container image that can run:
# - Streamlit chatbot UI: frontend/chat_ui.py
# - CLI tools: migrate.py, frontend/nl_ui.py
#
# This image is intended for use on AWS ECS/Fargate.

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates libpq-dev build-essential unzip \
    && rm -rf /var/lib/apt/lists/*

# TODO: Install Oracle Instant Client here if required for cx_Oracle on Linux.
# For example, you can download the Basic and SDK zip packages and install them.
# See: https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html

# Copy dependency file and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Default command runs the chatbot UI
CMD ["streamlit", "run", "frontend/chat_ui.py", "--server.port", "8501", "--server.address", "0.0.0.0"]


