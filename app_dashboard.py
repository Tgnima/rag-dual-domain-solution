#!/usr/bin/env python3
"""
app_dashboard.py – Interface Streamlit unifiée pour Prospection (SalesBot) et Recrutement (RecruitBot).
"""
from __future__ import annotations
import os, sys, pathlib
from typing import List

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from pinecone import Pinecone

# ── bootstrap ──────────────────────────────────────────────
PROJECT_DIR = pathlib.Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from core import init_embedder, init_claude, search_prospects  # utilitaire partagé

# ── Config Pinecone candidats ─────────────────────────────
CANDIDATE_INDEX_NAME = os.getenv("CANDIDATE_INDEX_NAME", "candidate-vectors")
PINECONE_API_KEY     = os.getenv("PINECONE_API_KEY")
PINECONE_REGION      = os.getenv("PINECONE_REGION", "us-east-1")

@st.cache_resource
def init_candidate_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(CANDIDATE_INDEX_NAME)

@st.cache_resource
def search_candidates(query: str, top_k: int = 10):
    embedder = init_embedder()
    index    = init_candidate_index()
    q_vec    = embedder.embed_query(query)
    res = index.query(vector=q_vec, top_k=top_k, include_metadata=True)
    return res.matches

# ── UI GLOBAL ─────────────────────────────────────────────
st.set_page_config(page_title="🎛️ Assistant RAG", page_icon="🎛️", layout="wide")
st.title("🎛️ Assistant RAG Consolidé")

mode = st.sidebar.radio("Choisir le module :", ("Prospection", "Recrutement"))

if mode == "Prospection":
    st.header("🎯 Module Prospection")
    query = st.text_input(
        "Posez votre question sur vos prospects…",
        placeholder="Ex. : Quels sont les prospects fintech à contacter cette semaine ?",
        key="sales_query",
    )
    if st.button("🔍 Rechercher & Analyser", key="btn_sales") and query.strip():
        with st.spinner("Recherche prospects…"):
            matches = search_prospects(query, None, top_k=10)
            if not matches:
                st.warning("Aucun prospect trouvé.")
                st.stop()

            prospects: List[dict] = []
            ctx_lines = []
            for i, m in enumerate(matches, 1):
                md = m.metadata
                tag = f"[SRC{i}]"
                note_snippet = (str(md.get('notes', ''))[:80]).replace("\n", " ")
                ctx_lines.append(
                    f"{tag} Entreprise: {md.get('entreprise','N/A')} | Contact: {md.get('contact','N/A')} | "
                    f"Secteur: {md.get('secteur','N/A')} | Statut: {md.get('statut','N/A')} | "
                    f"Budget: {md.get('budget','N/A')} | Notes: {note_snippet}…"
                )
                prospects.append(md | {"tag": tag, "score": round(m.score, 3)})

            context = "\n".join(ctx_lines)
            chat = init_claude()
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Tu es SalesBot, un expert commercial. Réponds brièvement, puis liste les sources ([SRCx])."),
                ("human", f"PROSPECTS:\n{context}\n\nQUESTION: {query}\n\nANALYSE:")
            ])
            answer = chat.invoke(prompt.format_messages()).content

        st.subheader("🤖 Analyse Prospection")
        st.markdown(answer)

        st.subheader("📋 Prospects")
        df = pd.DataFrame(prospects)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export CSV", csv, "prospects.csv", "text/csv", key="csv_pros")

elif mode == "Recrutement":
    st.header("🤝 Module Recrutement")
    query = st.text_input(
        "Posez votre question sur les candidats…",
        placeholder="Ex. : Trouve-moi des profils data engineer disponibles dans 2 mois",
        key="recruit_query",
    )
    if st.button("🔍 Rechercher & Analyser", key="btn_recruit") and query.strip():
        with st.spinner("Recherche candidats…"):
            matches = search_candidates(query, top_k=10)
            if not matches:
                st.warning("Aucun candidat trouvé.")
                st.stop()

            candidates: List[dict] = []
            ctx_lines = []
            for i, m in enumerate(matches, 1):
                md = m.metadata
                tag = f"[SRC{i}]"
                note_snippet = (str(md.get('notes', ''))[:80]).replace("\n", " ")
                ctx_lines.append(
                    f"{tag} Nom: {md.get('nom','N/A')} | Role: {md.get('role','N/A')} | "
                    f"Compétences: {md.get('competences','N/A')} | Exp: {md.get('experience','N/A')} | "
                    f"Localisation: {md.get('localisation','N/A')} | Dispo: {md.get('disponibilite','N/A')} | "
                    f"Notes: {note_snippet}…"
                )
                candidates.append(md | {"tag": tag, "score": round(m.score, 3)})

            context = "\n".join(ctx_lines)
            chat = init_claude()
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Tu es RecruitBot, un expert en talent acquisition. Réponds brièvement, puis liste les sources ([SRCx])."),
                ("human", f"CANDIDATS:\n{context}\n\nQUESTION: {query}\n\nANALYSE:")
            ])
            answer = chat.invoke(prompt.format_messages()).content

        st.subheader("🤖 Analyse Recrutement")
        st.markdown(answer)

        st.subheader("📋 Candidats")
        df = pd.DataFrame(candidates)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export CSV", csv, "candidats.csv", "text/csv", key="csv_cand")

        # Les CVs ne sont plus pris en charge.

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>© Assistant RAG Unifié – Bedrock, Pinecone & Claude</div>",
    unsafe_allow_html=True
) 