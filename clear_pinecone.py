#!/usr/bin/env python3
"""
clear_pinecone.py – Supprime tous les index Pinecone associés à la clé API.

Usage :
    python clear_pinecone.py          # Demande confirmation avant suppression
    python clear_pinecone.py --force  # Supprime sans confirmation

Les variables d'environnement nécessaires :
    PINECONE_API_KEY   (obligatoire)
"""
from __future__ import annotations
import os, sys
from dotenv import load_dotenv
from pinecone import Pinecone

# Charger les variables depuis .env s'il existe
load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")
if not API_KEY:
    sys.exit("❌ PINECONE_API_KEY manquante dans .env ou variables d'environnement")

pc = Pinecone(api_key=API_KEY)
indexes = pc.list_indexes()
if not indexes:
    print("✅ Aucun index Pinecone à supprimer.")
    sys.exit(0)

print("🔍 Index trouvés :")
for idx in indexes:
    print(f"  • {idx.name}")

force = "--force" in sys.argv
if not force:
    confirm = input("⚠️  Confirmer la suppression de TOUS ces index ? (yes/no) ").strip().lower()
    if confirm not in {"y", "yes"}:
        print("❌ Abandon.")
        sys.exit(0)

for idx in indexes:
    print(f"🗑️  Suppression {idx.name}…", end=" ")
    pc.delete_index(idx.name)
    print("✅")

print("🎉 Tous les index ont été supprimés.") 