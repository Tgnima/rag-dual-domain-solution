# 🎯🤝 RAG Dual-Domain Solution

Assistant **prospection commerciale** _et_ **recrutement** basé sur vos bases Airtable.

* Embeddings : AWS Bedrock Titan v2 (1024 dim)
* Base vectorielle : Pinecone Serverless
* Chat : Claude 3.5 Sonnet (Anthropic)
* UI : Streamlit unifiée (`app_dashboard.py`)

---

## 🚀 Fonctionnalités

| Module | Points forts |
|--------|--------------|
| **Prospection** | 🔍 Recherche sémantique dans vos fiches prospects · 📈 Analyse IA orientée ROI · 📊 Exports CSV/JSON |
| **Recrutement** | 🧑‍💻 Recherche de talents · 💡 Recommandations d'actions RH · 📊 Tableaux filtrables |

---

## 📦 Installation rapide avec Docker Compose

1. Copiez `.env.example` → `.env` et remplissez vos clés AWS, Pinecone, Airtable, Anthropic.
2. Lancez :
```bash
docker compose up --build
```
3. Ouvrez http://localhost:8501 puis choisissez « Prospection » ou « Recrutement » dans la barre latérale.

> Le conteneur installe tout via `requirements.txt` et expose Streamlit sur 8501.

### Structure minimale `.env`
```bash
AIRTABLE_API_KEY=...
AIRTABLE_BASE_ID=...
AIRTABLE_TABLE_NAME=Prospects
AIRTABLE_CANDIDATE_TABLE_NAME=Candidats

AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

PINECONE_API_KEY=...
PINECONE_REGION=us-east-1
PINECONE_INDEX_NAME=airtable-vectors
CANDIDATE_INDEX_NAME=candidate-vectors

ANTHROPIC_API_KEY=...
```

---

## 🧑‍💻 Cycle DEV rapide

```bash
# Nettoyer complètement les index Pinecone (⚠️ destructif)
docker compose run --rm web python clear_pinecone.py --force

# Ré-ingestion Prospects puis Candidats
docker compose run --rm web python ingest.py
docker compose run --rm web python ingest_candidates.py

# (Re)démarrer l'interface
docker compose restart web   # ou docker compose up web
```

Ces commandes utilisent l'image déjà construite : aucun rebuild n'est nécessaire, l'itération est donc quasi instantanée.

---

## ⚙️ Utilisation sans Docker (optionnel)
```bash
python -m venv .venv && source .venv/bin/activate  # (PowerShell : .venv\Scripts\Activate.ps1)
pip install -r requirements.txt

# Ingestion (prospects puis candidats)
python ingest.py
python ingest_candidates.py

# Interface
streamlit run app_dashboard.py
```

---

## 🛠️ Scripts clés
| Script | Rôle |
|--------|------|
| `ingest.py` | Lit la table **Prospects** Airtable, crée les embeddings et alimente Pinecone |
| `ingest_candidates.py` | Idem pour la table **Candidats** |
| `clear_pinecone.py` | Purge tous les index Pinecone reliés à la clé API (⚠️ destructif) |
| `app_dashboard.py` | Interface Streamlit unifiée (prospection + recrutement) |
| `app_smart.py` / `app_recruit.py` | Interfaces mono-domaine (optionnelles) |
| `core.py` | Initialisation Bedrock, Pinecone, Claude + fonctions de recherche |

---

## 📋 Schémas Airtable attendus

### Table Prospects
| Champ | Exemple |
|-------|---------|
| `Entreprise` | ACME Corp |
| `Contact` | Jane Doe |
| `Email` | jane@acme.com |
| `Phone` | +33 6 12 34 56 78 |
| `Secteur` | Tech |
| `Statut` | Qualifié |
| `Budget` | Élevé |
| `Notes` | Intéressé par la solution… |

### Table Candidats
| Champ | Exemple |
|-------|---------|
| `Nom` | John Smith |
| `Role` | Data Engineer |
| `Competences` | Python, Spark |
| `Experience` | 5 ans |
| `Localisation` | Paris |
| `Disponibilite` | 1 mois |
| `Notes` | Projet perso ML… |

---

## 🖼️ Architecture
```
Airtable ↘                ↙  Bedrock Titan  ↘
            Ingestion  →  Pinecone Vector DB  →  Streamlit UI  →  Claude 3.5
Airtable Candidats ↗                ↖  (search+context) ↗
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: app` | Import remplacé par `core.py`. Mettez à jour les scripts hérités. |
| `AttributeError 'count_tokens'` | Versions compatibles définies dans `requirements.txt`. Re-build Docker. |
| `KeyError '_data_store'` | Utiliser `@st.cache_resource` (déjà corrigé) au lieu de `@st.cache_data` pour les objets Pinecone. |
| Push GitHub SSH : *permission denied* | Ajouter votre clé SSH à GitHub **ou** utiliser l'URL HTTPS avec un PAT. |

---

## Licence
MIT 2025 – Feel free to fork & improve 🎉 