# 🎯 Assistant Commercial RAG - Base de Prospects

Transformez votre base de prospects Airtable en assistant commercial intelligent pour optimiser vos efforts d'acquisition !

## 🚀 Fonctionnalités

### 📊 **Analyse Intelligente de Prospects**
- Recherche sémantique dans vos fiches prospects
- Identification des opportunités prioritaires
- Analyse par secteur, taille, budget, statut
- Suggestions de stratégies d'approche personnalisées

### 🎯 **Optimisation Commerciale**
- Priorisation automatique des prospects
- Insights sur la pipeline commerciale
- Recommandations d'actions ciblées
- Filtrage avancé par critères métier

### 🧠 **IA Spécialisée**
- Claude 3.5 Sonnet optimisé pour le commercial
- Embeddings Titan V2 (1024 dim) pour la précision
- Stockage vectoriel Pinecone haute performance

## 🔧 Configuration

Créez un fichier `.env` à la racine du projet :

```bash
# Airtable - Base de Prospects
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
AIRTABLE_TABLE_NAME=your_prospects_table_name

# AWS Bedrock (Embeddings)
AWS_REGION=us-east-1
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0
BEDROCK_EMBED_DIMENSIONS=1024

# Pinecone (Base Vectorielle)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_REGION=us-east-1
PINECONE_INDEX_NAME=prospects-vectors

# Anthropic (Assistant IA)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### 📋 **Champs Airtable Supportés**

Le système détecte automatiquement ces champs (avec variantes) :
- **Entreprise** : `Entreprise`, `Company`, `Société`
- **Contact** : `Contact`, `Nom`, `Name`
- **Email** : `Email`, `E-mail`
- **Téléphone** : `Téléphone`, `Phone`, `Tel`
- **Secteur** : `Secteur`, `Industry`, `Industrie`
- **Taille** : `Taille`, `Size`, `Effectif`
- **Statut** : `Statut`, `Status`, `État`
- **Budget** : `Budget`, `Budget estimé`
- **Priorité** : `Priorité`, `Priority`
- **Source** : `Source`, `Origine`
- **Notes** : `Notes`, `Commentaires`, `Description`

## 📦 Installation

```powershell
# Dans votre environnement virtuel
pip install -r requirements.txt
```

### 🚀 **Démarrage Rapide (Recommandé)**

```powershell
python quick_start.py
```

Ce script interactif va :
- ✅ Vérifier votre configuration
- 🏗️ Configurer la structure Airtable
- 💉 Injecter des données d'exemple
- 🔄 Lancer l'ingestion RAG
- 🌟 Démarrer l'interface Streamlit

### 🧪 **Injection de Données d'Exemple**

Pour tester le système sans vraies données :

```powershell
# 1. Configurer la structure Airtable
python setup_airtable_schema.py

# 2. Injecter des données d'exemple
python inject_to_airtable.py

# 3. Lancer l'ingestion
python ingest.py

# 4. Interface Streamlit
streamlit run app.py
```

## 🚀 Utilisation

### 1. **Indexation des Prospects** (première fois)

```powershell
python ingest.py
```

Cette étape :
- 📖 Lit tous vos prospects Airtable
- 🔧 Structure les données pour la recherche
- 🧠 Génère des embeddings optimisés
- 🚀 Indexe dans Pinecone

### 2. **Recherche et Analyse de Prospects**

#### **Recherches Générales**
```powershell
# Identifier les prospects prioritaires
python qa.py "prospects avec un gros budget dans la tech"

# Analyser les opportunités immédiates
python qa.py "entreprises prioritaires à contacter cette semaine"

# Stratégie sectorielle
python qa.py "comment approcher les prospects e-commerce"
```

#### **Recherches avec Filtres**
```powershell
# Prospects qualifiés dans un secteur
python qa.py "meilleurs prospects" --filter secteur=Tech --filter statut=Qualifié

# Analyse par source
python qa.py "performance des prospects" --filter source=LinkedIn

# Prospects haute priorité
python qa.py "actions urgentes" --filter priorite=Haute
```

#### **Analyses Avancées**
```powershell
# Top 10 des prospects
python qa.py "analyse des 10 meilleurs prospects" --top_k 10

# Mode debug avec détails
python qa.py "stratégie Q1" --debug

# Analyse multi-critères
python qa.py "prospects SaaS budget élevé" --filter secteur=SaaS --filter budget=Élevé --debug
```

## 🎯 Exemples de Questions Commerciales

### **🔍 Identification d'Opportunités**
- *"Quels sont les prospects les plus prometteurs ce mois-ci ?"*
- *"Entreprises avec un budget conséquent dans la fintech"*
- *"Prospects chauds prêts à être contactés"*

### **📊 Analyse Stratégique**
- *"Tendances par secteur dans ma pipeline"*
- *"Quelle approche pour les prospects e-commerce ?"*
- *"Performance des sources d'acquisition"*

### **⚡ Actions Prioritaires**
- *"Prospects urgents à relancer cette semaine"*
- *"Opportunités à fort potentiel négligées"*
- *"Stratégie pour les prospects froids"*

### **🎨 Personnalisation**
- *"Comment adapter mon pitch pour [secteur] ?"*
- *"Arguments clés pour convaincre [type d'entreprise]"*
- *"Objections fréquentes dans [industrie]"*

## 🔍 Filtres Disponibles

| Filtre | Exemples | Usage |
|--------|----------|--------|
| `secteur` | Tech, SaaS, E-commerce | `--filter secteur=Tech` |
| `statut` | Qualifié, En cours, Froid | `--filter statut=Qualifié` |
| `taille` | PME, ETI, Grand compte | `--filter taille=ETI` |
| `priorite` | Haute, Moyenne, Basse | `--filter priorite=Haute` |
| `source` | LinkedIn, Salon, Site web | `--filter source=LinkedIn` |
| `budget` | Élevé, Moyen, Faible | `--filter budget=Élevé` |

## 🛠️ Architecture Technique

- **🧠 Embeddings** : AWS Bedrock Titan V2 (1024 dim, $0.02/1M tokens)
- **🗄️ Base vectorielle** : Pinecone Serverless (nouvelle API 2024)
- **🤖 Assistant IA** : Claude 3.5 Sonnet (spécialisé commercial)
- **📊 Chunking** : Optimisé pour fiches prospects (600 tokens)

## 📈 Optimisations Commerciales

### **✅ Métadonnées Enrichies**
- Scores de pertinence pour prioriser
- Informations complètes par prospect
- Évitement des doublons

### **✅ Prompts Spécialisés**
- Assistant commercial expert
- Suggestions actionnables
- Analyse de tendances

### **✅ Recherche Avancée**
- Filtrage multi-critères
- Recherche sémantique intelligente
- Mode debug pour transparence

## 🔄 Mise à Jour des Données

```powershell
# Synchronisation avec Airtable
python ingest.py  # Réindexe tous les prospects
```

## 🎯 Prochaines Améliorations

- [ ] 🔗 Webhook Airtable pour sync temps réel
- [ ] 📊 Dashboard Streamlit avec métriques
- [ ] 📧 Suggestions d'emails personnalisés
- [ ] 📅 Intégration calendrier pour follow-ups
- [ ] 🤖 Scoring automatique des prospects
- [ ] 📈 Analytics de performance commerciale

---

**🚀 Transformez votre prospection avec l'IA !** 