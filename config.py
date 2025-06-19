"""config.py
Configuration centralisée pour l'Assistant Commercial RAG.
Toutes les variables sensibles sont chargées à partir des variables d'environnement
(et éventuellement du fichier .env s'il est présent).
"""

from __future__ import annotations

import os
from dotenv import load_dotenv
from pathlib import Path

# Charger le fichier .env situé dans le même dossier que ce script
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

# ---------------------------------------------------------------------------
# AIRTABLE
# ---------------------------------------------------------------------------
AIRTABLE_API_KEY: str | None = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID: str | None = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME: str | None = os.getenv("AIRTABLE_TABLE_NAME")

# ---------------------------------------------------------------------------
# AWS / BEDROCK
# ---------------------------------------------------------------------------
AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
BEDROCK_EMBED_MODEL: str = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
# Titan V2 = 1024 dimensions par défaut
try:
    BEDROCK_EMBED_DIMENSIONS: int = int(os.getenv("BEDROCK_EMBED_DIMENSIONS", "1024"))
except ValueError:
    BEDROCK_EMBED_DIMENSIONS = 1024

# ---------------------------------------------------------------------------
# PINECONE
# ---------------------------------------------------------------------------
PINECONE_API_KEY: str | None = os.getenv("PINECONE_API_KEY")
PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "airtable-vectors")

# ---------------------------------------------------------------------------
# ANTHROPIC / CLAUDE
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

def validate_config() -> None:
    """Valide que toutes les variables critiques sont présentes.

    Soulève ValueError si une variable obligatoire est manquante.
    """
    required = [
        ("AIRTABLE_API_KEY", AIRTABLE_API_KEY),
        ("AIRTABLE_BASE_ID", AIRTABLE_BASE_ID),
        ("AIRTABLE_TABLE_NAME", AIRTABLE_TABLE_NAME),
        ("PINECONE_API_KEY", PINECONE_API_KEY),
        ("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY),
    ]

    missing = [name for name, value in required if not value]
    if missing:
        raise ValueError(
            "Variables d'environnement manquantes: " + ", ".join(missing)
        )

# ---------------------------------------------------------------------------
# Debug Helper (optionnel)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        validate_config()
        print("✅ Config OK - toutes les variables requises sont définies.")
    except ValueError as e:
        print(f"❌ {e}") 