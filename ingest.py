#!/usr/bin/env python3
"""
ingest.py – Lit les prospects Airtable, génère des embeddings Titan, indexe dans Pinecone.
Toutes les clés sont lues dans .env (ou variables d'environnement).
"""

import os, time
from typing import List
from dotenv import load_dotenv
from pyairtable import Table
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings
from pinecone import Pinecone, ServerlessSpec
import boto3

# ── config ───────────────────────────────────────────────────────────
load_dotenv()
AIRTABLE_API_KEY   = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID   = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Prospects")

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
BEDROCK_MODEL = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
BEDROCK_DIM   = int(os.getenv("BEDROCK_EMBED_DIMENSIONS", "1024"))

PINECONE_API_KEY   = os.getenv("PINECONE_API_KEY")
PINECONE_REGION    = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_INDEX     = os.getenv("PINECONE_INDEX_NAME", "airtable-vectors")

# Sanity-check
for name, val in {"AIRTABLE_API_KEY":AIRTABLE_API_KEY,
                  "AIRTABLE_BASE_ID":AIRTABLE_BASE_ID,
                  "PINECONE_API_KEY":PINECONE_API_KEY}.items():
    if not val:
        raise RuntimeError(f"Variable manquante: {name}")

# ── helpers ───────────────────────────────────────────────────────────
def load_records() -> List[dict]:
    return Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME).all()

def build_documents(records: List[dict]) -> List[Document]:
    """Transforme les enregistrements Airtable en Documents LangChain avec meta enrichi.

    Chaque prospect devient un ou plusieurs documents (si très long) mais
    chacun conserve les métadonnées structurées (entreprise, contact, secteur…).
    """
    # Mapping Airtable ➜ Meta (basé sur les champs EXACTS fournis par l'utilisateur)
    field_map = {
        "Entreprise": "entreprise",
        "Contact": "contact",
        "Email": "email",
        "Phone": "phone",
        "Secteur": "secteur",
        "Statut": "statut",
        "Notes": "notes",
    }

    docs: List[Document] = []

    for r in records:
        f = r.get("fields", {})

        # Contenu textuel structuré : on place les champs importants en haut
        ordered_content_lines = []
        for label in [
            "Entreprise", "Contact", "Email", "Phone",
            "Secteur", "Statut", "Notes"
        ]:
            value = f.get(label)
            if value:
                ordered_content_lines.append(f"{label}: {value}")

        content = "\n".join(ordered_content_lines)
        if not content.strip():
            continue

        # Métadonnées enrichies (lowercase, sans accents pour cohérence)
        meta = {"airtable_id": r["id"]}
        for k_src, k_meta in field_map.items():
            val = f.get(k_src)
            if val:
                meta[k_meta] = val

        docs.append(Document(page_content=content, metadata=meta))

    # Split si le contenu dépasse 800 caractères (typiquement très rares)
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
    return splitter.split_documents(docs)

def bedrock_embedder() -> BedrockEmbeddings:
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    return BedrockEmbeddings(
        client=client, model_id=BEDROCK_MODEL,
        model_kwargs={"dimensions": BEDROCK_DIM, "normalize":True})

def pinecone_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if PINECONE_INDEX not in [idx.name for idx in pc.list_indexes()]:
        pc.create_index(
            name=PINECONE_INDEX, dimension=BEDROCK_DIM, metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION))
        while not pc.describe_index(PINECONE_INDEX).status["ready"]:
            time.sleep(1)
    return pc.Index(PINECONE_INDEX)

# ── main ──────────────────────────────────────────────────────────────
def ingest():
    print("1/4 Lecture Airtable…")
    records = load_records()
    print(f"   {len(records)} prospects")

    print("2/4 Construction documents…")
    docs = build_documents(records); print(f"   {len(docs)} docs")

    print("3/4 Embeddings…")
    vecs = bedrock_embedder().embed_documents([d.page_content for d in docs])

    print("4/4 Upload Pinecone…")
    idx = pinecone_index()
    idx.upsert([
        {"id": f"{d.metadata['airtable_id']}_{i}", "values": v,
         "metadata": d.metadata | {"text": d.page_content}}
        for i,(d,v) in enumerate(zip(docs,vecs))
    ])
    print("✅ Terminé !")

if __name__ == "__main__":
    ingest()