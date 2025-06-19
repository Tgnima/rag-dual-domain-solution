#!/usr/bin/env python3
"""
app_recruit.py – Assistant RAG pour le recrutement.
Recherche et analyse de candidats issus d'Airtable indexés dans Pinecone.
"""
from __future__ import annotations
import os, sys, pathlib
from typing import List
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# ── bootstrap ──────────────────────────────────────────────
PROJECT_DIR = pathlib.Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from langchain.prompts import ChatPromptTemplate
from core import init_embedder, init_claude  # utilitaire partagé
from pinecone import Pinecone

# ── helpers Pinecone spécifiques candidats ───────────────────────────
CANDIDATE_INDEX_NAME = os.getenv("CANDIDATE_INDEX_NAME", "candidate-vectors")
PINECONE_API_KEY     = os.getenv("PINECONE_API_KEY")
PINECONE_REGION      = os.getenv("PINECONE_REGION", "us-east-1")

@st.cache_resource
def init_candidate_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(CANDIDATE_INDEX_NAME)

@st.cache_data(ttl=600)
def search_candidates(query: str, top_k: int = 10):
    embedder = init_embedder()
    index    = init_candidate_index()
    q_vec    = embedder.embed_query(query)
    res = index.query(vector=q_vec, top_k=top_k, include_metadata=True)
    return res.matches

# ── UI ─────────────────────────────────────────────────────
st.set_page_config(page_title="🤝 RecruitBot RAG", page_icon="🤝", layout="wide")
st.title("🤝 Assistant Recrutement RAG")

query = st.text_input(
    "Posez votre question sur les candidats…",
    placeholder="Ex. : Trouve-moi des développeurs Python disponibles dans 1 mois"
)
submitted = st.button("🔍 Rechercher & Analyser", type="primary")

if submitted and query.strip():
    with st.spinner("Recherche et analyse en cours…"):
        matches = search_candidates(query, top_k=10)
        if not matches:
            st.warning("Aucun candidat trouvé.")
            st.stop()

        # Construction contexte
        candidates: List[dict] = []
        ctx_lines = []
        for i, m in enumerate(matches, 1):
            md = m.metadata
            tag = f"[SRC{i}]"
            ctx_lines.append(
                f"{tag} Nom: {md.get('nom','N/A')} | Role: {md.get('role','N/A')} | "
                f"Compétences: {md.get('competences','N/A')} | Exp: {md.get('experience','N/A')} | "
                f"Dispo: {md.get('disponibilite','N/A')} | Notes: {str(md.get('notes',''))[:80].replace('\n',' ')}…"
            )
            candidates.append(md | {"tag": tag, "score": round(m.score, 3)})

        context = "\n".join(ctx_lines)

        chat = init_claude()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Tu es RecruitBot, un expert en acquisition de talents. Réponds brièvement, puis liste les sources ([SRCx])."),
            ("human", f"CANDIDATS:\n{context}\n\nQUESTION: {query}\n\nANALYSE:")
        ])
        answer = chat.invoke(prompt.format_messages()).content

    # Affichage
    st.subheader("🤖 Analyse IA")
    st.markdown(answer)

    st.subheader("🔗 Sources")
    for c in candidates:
        st.markdown(f"- {c['tag']} {c.get('nom','N/A')}")

    st.subheader("📋 Candidats")
    df = pd.DataFrame(candidates)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export CSV", csv, "candidats.csv", "text/csv")
else:
    st.info("Entrez votre question puis cliquez sur le bouton.") 