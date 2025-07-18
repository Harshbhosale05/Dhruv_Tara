# 🚀 DhruvTara – AI-Based Help Bot for MOSDAC (ISRO Hackathon 2025)

🌌 **Team DhruvTara's submission for the ISRO Bhartiya Antariksh Hackathon 2025**  
🔍 *An AI-powered Help Bot for intelligent information retrieval from the MOSDAC portal using RAG + Knowledge Graph.*

---

## 📌 Problem Statement (PS-2)

**"AI-based Help Bot for Information Retrieval from a Knowledge Graph Based on Static/Dynamic Web Portal Content"**

The MOSDAC portal hosts extensive satellite data, documentation, and support material. Users face difficulty accessing specific information due to layered navigation and mixed content formats. Our solution enables natural language-based, contextual querying over both structured and unstructured content from the portal.

---

## 🎯 Objectives

- Build a conversational AI bot that answers user queries using NLP, LLMs, and semantic search.
- Model extracted content into a dynamic knowledge graph (Neo4j).
- Enable spatially-aware, relationship-based, contextual Q&A.
- Build a scalable system deployable across other ISRO web portals.

---

## 🧠 Key Features

- 🔄 **Hybrid Retrieval-Augmented Generation + Knowledge Graph reasoning**
- ⚡ **Real-time semantic search** using Pinecone vector DB
- 🧠 **Context memory** for follow-up questions (LangChain)
- 🛰️ **Spatial intelligence**: geo-aware Q&A support
- 📎 **Source-backed responses**: answer with citations
- 🔌 **Modular deployment architecture** (plug into other ISRO portals)

---

## 🗂️ Tech Stack

| Layer          | Tech Used                           |
|----------------|-------------------------------------|
| 🔍 Embeddings   | MiniLM (SentenceTransformers)       |
| 🧠 LLM / RAG    | LangChain + custom prompt chains    |
| 📦 Vector DB    | Pinecone (cloud-hosted)             |
| 🧱 Knowledge Graph | Neo4j (Cypher queries)            |
| 🧠 NLP          | spaCy, NLTK for entity extraction   |
| 🌐 Backend      | FastAPI                             |
| 💬 Chat Interface | React.js / Streamlit               |
| ☁️ Deployment   | Render (migratable to Railway)      |

---

## 🛠️ System Architecture

```txt
User Query
   ↓
LangChain Pipeline
   ├── Vector Search (Pinecone)
   ├── KG Query (Neo4j)
   ↓
Contextual Answer Generation
   ↓
Frontend UI Response
﻿# Dhruv_Tara
