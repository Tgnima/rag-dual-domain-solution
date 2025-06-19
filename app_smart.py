#!/usr/bin/env python3
"""
app_smart.py – Interface simplifiée : 1 champ de recherche,
analyse IA sourcée, export CSV/JSON.
"""
from __future__ import annotations
import os, sys, pathlib, json
from datetime import datetime
from typing import List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ── bootstrap ──────────────────────────────────────────────
PROJECT_DIR = pathlib.Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from core import init_embedder, init_pinecone, init_claude, search_prospects

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def airtable_url(rec_id: str) -> str:
    return f"https://airtable.com/{AIRTABLE_BASE_ID}/{rec_id}" if AIRTABLE_BASE_ID else f"https://airtable.com/{rec_id}"

# ── UI ─────────────────────────────────────────────────────
st.set_page_config(page_title="🎯 Assistant RAG", page_icon="🎯", layout="wide")
st.title("🎯 Assistant Commercial RAG")

query = st.text_input(
    "Posez votre question sur vos prospects…",
    placeholder="Ex. : Quels sont les prospects fintech à contacter cette semaine ?"
)
submitted = st.button("🔍 Rechercher & Analyser", type="primary")

if submitted and query.strip():
    with st.spinner("Recherche et analyse en cours…"):
        # Recherche des 10 meilleurs prospects correspondants
        matches = search_prospects(query, None, top_k=100)
        if not matches:
            st.warning("Aucun prospect trouvé.")
            st.stop()

        # Contexte pour Claude
        prospects: List[dict] = []
        display_rows: List[dict] = []
        ctx_lines = []
        for i, m in enumerate(matches, 1):
            md = m.metadata
            tag = f"[SRC{i}]"
            ctx_lines.append(
                f"{tag} Entreprise: {md.get('entreprise','N/A')} | "
                f"Contact: {md.get('contact','N/A')} | "
                f"Secteur: {md.get('secteur','N/A')} | Statut: {md.get('statut','N/A')} | "
                f"Budget: {md.get('budget','N/A')} | Notes: {(md.get('notes') or md.get('text',''))[:1000].replace('\\n',' ')}…"
            )
            full_dict = md | {"tag": tag, "score": round(m.score, 3)}
            prospects.append(full_dict)

            # Row pour DataFrame avec noms clairs
            display_rows.append({
                "Tag": tag,
                "Score": round(m.score,3),
                "Entreprise": md.get('entreprise',''),
                "Contact": md.get('contact',''),
                "Secteur": md.get('secteur',''),
                "Statut": md.get('statut',''),
                "Budget": md.get('budget',''),
                "Notes": (md.get('notes') or '')[:120]
            })

        context = "\n".join(ctx_lines)

        chat = init_claude()
        from langchain.prompts import ChatPromptTemplate
        # Nouveau prompt SalesBot détaillé
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Tu es SalesBot, un consultant commercial senior expert en prospection B2B et analyse de données CRM.

🎯 **MISSION** : Analyser les données prospects et fournir des recommandations commerciales basées exclusivement sur les sources fournies.

📊 **MÉTHODOLOGIE RAG OBLIGATOIRE** :

**🔍 1. ANALYSE DES DONNÉES**
- Examiner toutes les sources fournies ([SRC1], [SRC2], etc.)
- Identifier les patterns, tendances et corrélations
- Quantifier les métriques clés (taux, moyennes, volumes)
- Segmenter les prospects par critères pertinents

**📈 2. JUSTIFICATION DE LA SÉLECTION**
- Expliquer POURQUOI chaque donnée est pertinente pour la question
- Calculer l'impact potentiel sur les KPIs commerciaux
- Évaluer la fiabilité des données (taille échantillon, récence)
- Établir les priorités par potentiel business

**💡 3. RECOMMANDATIONS DATA-DRIVEN**
- Proposer uniquement des actions basées sur les données analysées
- Quantifier l'impact attendu de chaque recommandation
- Prioriser par ROI potentiel et facilité d'implémentation
- Inclure des métriques de suivi pour mesurer le succès

**📋 FORMAT DE RÉPONSE STRICTEMENT OBLIGATOIRE** :

### 🔍 **ANALYSE DES DONNÉES** 
*Sources consultées : [liste des SRCx utilisées]*
- **Métriques clés identifiées** : [données chiffrées avec sources]
- **Segments détectés** : [classification des prospects avec critères]
- **Patterns observés** : [tendances et corrélations avec preuves]

### 📊 **JUSTIFICATION DES INSIGHTS**
- **Pertinence** : Pourquoi ces données répondent à la question [SRCx]
- **Impact calculé** : Potentiel d'amélioration des KPIs [SRCx]
- **Fiabilité** : Qualité et représentativité des données [SRCx]

### 💡 **RECOMMANDATIONS PRIORITAIRES**
1. **[Action #1]** - Impact: [métrique] - Justification: [SRCx]
2. **[Action #2]** - Impact: [métrique] - Justification: [SRCx]
3. **[Action #3]** - Impact: [métrique] - Justification: [SRCx]

### 📈 **MÉTRIQUES DE VALIDATION**
- **KPI à suivre** : [indicateur principal]
- **Objectif chiffré** : [amélioration attendue]
- **Timeline** : [délai d'implémentation]

### 📚 **SOURCES ANALYSÉES**
[Liste numérotée des sources utilisées]

⚠️ **RÈGLES STRICTES** :
- NE JAMAIS inventer ou supposer des informations
- TOUJOURS citer une source [SRCx] après chaque fait
- QUANTIFIER systématiquement (%, nombres, montants)
- PRIORISER les recommandations par impact business
- CALCULER le ROI potentiel quand possible
- ÊTRE spécifique et actionnable, pas générique

🚫 **INTERDIT** :
- Conseils génériques sans données de support
- Recommandations sans citation de source
- Analyses qualitatives sans métriques
- Hypothèses ou suppositions personnelles"""
            ),
            (
                "human",
                f"""📊 **DONNÉES PROSPECTS À ANALYSER** :\n{context}\n\n❓ **QUESTION COMMERCIALE** : {query}\n\n🎯 **OBJECTIF** : Fournis une analyse RAG complète selon la méthodologie ci-dessus, en te basant EXCLUSIVEMENT sur les données fournies."""
            )
        ])
        answer = chat.invoke(prompt.format_messages()).content

    # --- Affichage ---
    st.subheader("🤖 Analyse IA")
    st.markdown(answer)

    st.subheader("🔗 Sources")
    for p in prospects:
        st.markdown(f"- {p['tag']} {p.get('entreprise','N/A')} [↗]({airtable_url(p['airtable_id'])})")

    st.subheader("📋 Prospects")
    df = pd.DataFrame(display_rows)
    st.dataframe(df, use_container_width=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_bytes  = df.to_csv(index=False).encode("utf-8")
    json_bytes = df.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8")
    col1, col2 = st.columns(2)
    col1.download_button("⬇️ Export CSV",  csv_bytes,  f"prospects_{timestamp}.csv",  "text/csv")
    col2.download_button("⬇️ Export JSON", json_bytes, f"prospects_{timestamp}.json","application/json")
else:
    st.info("Entrez votre question puis cliquez sur le bouton.")
