FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code source
COPY . .

# Variables par défaut
ENV PYTHONUNBUFFERED=1
