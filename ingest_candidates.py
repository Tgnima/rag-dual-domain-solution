#!/usr/bin/env python3
"""
ingest_candidates.py – Lit les candidats Airtable, génère des embeddings et indexe dans Pinecone.

Pré-requis :
- Les variables d'environnement dans .env :
    AIRTABLE_API_KEY
    AIRTABLE_BASE_ID
    AIRTABLE_CANDIDATE_TABLE_NAME   (par défaut "Candidats")
    PINECONE_API_KEY
    PINECONE_REGION
    CANDIDATE_INDEX_NAME            (par défaut "candidate-vectors")

- Les champs attendus dans la table Airtable (adapter si besoin) :
    Nom, Role, Competences, Experience, Localisation, Disponibilite, Notes
"""
from __future__ import annotations
import os, time, tempfile, requests, io
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
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_CANDIDATE_TABLE_NAME", "Candidats")

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
BEDROCK_MODEL = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
BEDROCK_DIM   = int(os.getenv("BEDROCK_EMBED_DIMENSIONS", "1024"))

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION  = os.getenv("PINECONE_REGION", "us-east-1")
INDEX_NAME       = os.getenv("CANDIDATE_INDEX_NAME", "candidate-vectors")

for name, val in {"AIRTABLE_API_KEY":AIRTABLE_API_KEY,
                  "AIRTABLE_BASE_ID":AIRTABLE_BASE_ID,
                  "PINECONE_API_KEY":PINECONE_API_KEY}.items():
    if not val:
        raise RuntimeError(f"Variable manquante: {name}")

# ── helpers ───────────────────────────────────────────────────────────
def load_records() -> List[dict]:
    return Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME).all()

def build_documents(records: List[dict]) -> List[Document]:
    field_order = [
        "Nom", "Role", "Competences", "Experience", "Localisation", "Disponibilite", "Notes"
    ]
    field_map = {
        "Nom": "nom",
        "Role": "role",
        "Competences": "competences",
        "Experience": "experience",
        "Localisation": "localisation",
        "Disponibilite": "disponibilite",
        "Notes": "notes",
    }

    docs: List[Document] = []
    for r in records:
        f = r.get("fields", {})
        lines = [f"{k}: {f[k]}" for k in field_order if f.get(k)]
        content = "\n".join(lines)
        if not content.strip():
            continue
        meta = {"airtable_id": r["id"]}
        for k_src, k_meta in field_map.items():
            if f.get(k_src):
                meta[k_meta] = f[k_src]
        docs.append(Document(page_content=content, metadata=meta))

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
    return splitter.split_documents(docs)


def bedrock_embedder() -> BedrockEmbeddings:
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    return BedrockEmbeddings(client=client, model_id=BEDROCK_MODEL,
                             model_kwargs={"dimensions": BEDROCK_DIM, "normalize": True})

def pinecone_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME, dimension=BEDROCK_DIM, metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION))
        while not pc.describe_index(INDEX_NAME).status["ready"]:
            time.sleep(1)
    return pc.Index(INDEX_NAME)

# ── main ──────────────────────────────────────────────────────────────

def ingest_candidates():
    print("1/4 Lecture Airtable (candidats)…")
    records = load_records()
    print(f"   {len(records)} candidats")

    print("2/4 Construction documents…")
    docs = build_documents(records); print(f"   {len(docs)} docs")

    print("3/4 Embeddings…")
    vecs = bedrock_embedder().embed_documents([d.page_content for d in docs])

    print("4/4 Upload Pinecone…")
    idx = pinecone_index()
    idx.upsert([
        {"id": f"{d.metadata['airtable_id']}_{i}", "values": v, "metadata": d.metadata}
        for i,(d,v) in enumerate(zip(docs,vecs))
    ])
    print("✅ Terminé !")

if __name__ == "__main__":
    ingest_candidates() 