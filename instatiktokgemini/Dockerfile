FROM python:3.11-slim

# Installation de ffmpeg pour que les vidéos soient acceptées par Insta/TikTok
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# On copie et on installe tout
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# On crée les dossiers nécessaires
RUN mkdir -p medias database session

# Lancement du bot
CMD ["python", "-u", "bot.py"]