#!/usr/bin/env python3
"""core.py – Fonctions utilitaires partagées (embedding, Pinecone, Claude, recherche).
Suppression d'anciennes dépendances à app.py.
"""
from __future__ import annotations
import os, time, functools
from typing import Any, List, Optional

from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_anthropic import ChatAnthropic

# Streamlit est optionnel : si importé depuis script Streamlit, on utilise cache_resource
try:
    import streamlit as st
    cache_dec = st.cache_resource  # type: ignore
except ModuleNotFoundError:  # scripts hors Streamlit
    def cache_dec(func):
        return functools.lru_cache(maxsize=None)(func)

# ── env ───────────────────────────────────────────────────
load_dotenv()
AWS_REGION           = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
BEDROCK_MODEL_ID     = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
BEDROCK_DIMENSIONS   = int(os.getenv("BEDROCK_EMBED_DIMENSIONS", "1024"))

PINECONE_API_KEY     = os.getenv("PINECONE_API_KEY")
PINECONE_REGION      = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_INDEX_NAME  = os.getenv("PINECONE_INDEX_NAME", "airtable-vectors")

ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL      = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# ── helpers ───────────────────────────────────────────────
@cache_dec
def init_embedder() -> BedrockEmbeddings:
    import boto3
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    return BedrockEmbeddings(
        client=client,
        model_id=BEDROCK_MODEL_ID,
        model_kwargs={"dimensions": BEDROCK_DIMENSIONS, "normalize": True},
    )

@cache_dec
def init_pinecone():
    if not PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY manquante")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    # Crée l'index s'il n'existe pas
    if PINECONE_INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=BEDROCK_DIMENSIONS,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION),
        )
        # Attendre qu'il soit prêt
        while not pc.describe_index(PINECONE_INDEX_NAME).status.get("ready"):
            time.sleep(1)
    return pc.Index(PINECONE_INDEX_NAME)

@cache_dec
def init_claude():
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY manquante")
    return ChatAnthropic(api_key=ANTHROPIC_API_KEY, model_name=ANTHROPIC_MODEL)

# ----------------------------------------------------------

def search_prospects(query: str, filters: Optional[dict] = None, top_k: int = 10):
    """Recherche dans l'index Pinecone et retourne les matches."""
    embedder = init_embedder()
    index    = init_pinecone()
    query_vec = embedder.embed_query(query)

    pinecone_filter = {}
    if filters:
        for key, val in filters.items():
            if val and val != "Tous":
                pinecone_filter[key] = {"$eq": val}

    res = index.query(
        vector=query_vec,
        top_k=top_k,
        include_metadata=True,
        filter=pinecone_filter if pinecone_filter else None,
    )
    return res.matches 