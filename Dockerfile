# Utilise une image Python légère
FROM python:3.11-slim

# Empêche Python de bufferiser stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dépendances système minimales (build essentials + lib) — ajuste si nécessaire
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Crée le dossier de l'app
WORKDIR /app

# Copie les exigences en premier (optimise le cache Docker)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copie le reste du code
COPY . .

# Expose le port Streamlit par défaut
EXPOSE 8501

# Commande de démarrage — module unifié
CMD ["streamlit", "run", "app_dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"] 