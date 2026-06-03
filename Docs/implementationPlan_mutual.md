# Phase-Wise Implementation Plan: Mutual Fund FAQ Assistant

This document outlines the step-by-step roadmap for building, testing, and deploying the compliant, facts-only Mutual Fund FAQ Assistant. The plan is divided into 5 chronological phases to ensure modular development and robust compliance testing.

---

## 🗺️ Project Phases at a Glance

```mermaid
gantt
    title Project Timeline (Phases 1-5)
    dateFormat  YYYY-MM-DD
    section Backend & Ingestion
    Phase 1: Setup & Ingestion Pipeline    :active, p1, 2026-06-03, 3d
    Phase 2: RAG Engine & Constrained LLM :  p2, after p1, 3d
    section Compliance & Control
    Phase 3: Sanitizer & Classifier Guardrails : p3, after p2, 3d
    Phase 4: Ingestion Scheduler           : p4, after p3, 2d
    section Interface & Validation
    Phase 5: Streamlit UI & Verification   : p5, after p4, 2d
```

---

## ⚙️ Detailed Implementation Steps

### 📂 Phase 1: Environment Setup & Data Ingestion
**Goal:** Establish the repository structure, build the scraping engine, and index the initial Groww mutual fund corpus into a vector database.

*   [x] **1.1 Project Structure Initialization**
    *   Create directories: `app/` (Streamlit UI), `src/` (core modules), `Docs/` (documentation), and `tests/` (verification).
    *   Set up a Python virtual environment and `requirements.txt` containing `requests`, `beautifulsoup4`, and `chromadb`.
*   [x] **1.2 Web Scraping & Ingestion Module**
    *   Configure the ingestion engine to feed from the **5 designated Groww URLs**:
        *   HDFC Silver ETF FoF Direct Growth
        *   HDFC Small Cap Fund Direct Growth
        *   HDFC Defence Fund Direct Growth
        *   HDFC Gold ETF Fund of Fund Direct Plan Growth
        *   HDFC Nifty 50 Index Fund Direct Growth
    *   Inject custom User-Agent headers to bypass connection rate limits.
*   [x] **1.3 Data Extraction & Cleaning**
    *   Implement parser utilizing `BeautifulSoup` to extract the `id="__NEXT_DATA__"` JSON state.
    *   Extract and clean key data points (Expense Ratio, Exit Load, AUM, Min SIP, Benchmark Index, NAV, and Managers).
    *   Normalize fields (handle `None` inputs, clean strings, and structure manager bios/experience lists).
*   [x] **1.4 Structural Chunking & Metadata Mapping**
    *   Implement **Logical Section-Based Markdown Chunking** to split data by headings:
        *   `### Fund Overview`: Encapsulates all key-value parameters to keep metric relationships intact.
        *   `### Fund Manager: <name>`: One dedicated chunk per manager, isolating experience, education, and the extensive list of `funds_managed` (preventing truncation of multi-fund arrays).
        *   `### Scheme Documents`: Separates document and statement download guidelines.
    *   Affix metadata attributes (`source_url`, `last_updated`, `chunk_type`, `scheme_name`) to every chunk.
*   [x] **1.5 Vector Database Ingestion (ChromaDB)**
    *   Initialize persistent **ChromaDB** client (chosen over FAISS for native metadata filtering, easy document ID upserts/deletions, and structured persistent collection management) inside `db/` folder.
    *   Index and register the 21 generated scheme chunks using local **BAAI/bge-small-en-v1.5** sentence embeddings (100% free and offline).
    *   Validate chunk query retrieval success.

---

### 🧠 Phase 2: RAG Pipeline & Constrained Generation
**Goal:** Connect the LLM, retrieve relevant context chunks, and write system prompts that strictly constrain the response formatting.

*   [x] **2.1 LLM Client Integration**
    *   Integrate **Gemini 1.5 Flash** (via the official `google-generativeai` SDK) as the core LLM for fast, accurate context-based generation.
    *   Configure client connections with strict temperature settings (set to `0.0` to eliminate creativity and hallucinations).
*   [x] **2.2 Similarity Retrieval**
    *   Implement vector search queries with target scheme metadata pre-filtering to prevent cross-scheme data leakage.
    *   Retrieve the top $k$ relevant chunks (set to $k=2$ chunks) to compose context.
*   [x] **2.3 System Prompt Tuning**
    *   Author a strict system instruction enforcing formatting rules:
        *   Limit length to exactly **3 sentences** maximum.
        *   Include exactly **one citation link** referencing the source Groww URL.
        *   Add the required footer: `Last updated from sources: <date>`.
*   [x] **2.4 Formatting Wrapper**
    *   Write a post-processing utility to double-check that outputs strictly end with the footer and contain exactly one link.
    *   Integrate competitor blocklist filters (e.g., rejecting queries for SBI, ICICI, etc. immediately) to keep queries aligned with HDFC corpus scope.

---

### 🛡️ Phase 3: Compliance & Security Guardrails
**Goal:** Intercept and sanitize inputs to prevent PII leaks, and build the routing logic to block advisory queries.

*   [x] **3.1 PII & Security Sanitizer**
    *   Implement Regex/NER filters to intercept queries containing:
        *   Aadhaar / PAN card patterns.
        *   Bank Account numbers / OTPs.
        *   Email addresses & phone numbers.
    *   Replace detected details with redacted placeholders or reject the query.
*   [x] **3.2 Intent Classifier (Allowed vs. Refused)**
    *   Build a router using a prompt classifier or classification model:
        *   *Route A (Factual):* Forward to the Phase 2 RAG system.
        *   *Route B (Advisory/Opinions):* Divert to the Refusal Engine.
*   [x] **3.3 Refusal Engine**
    *   Define polite, clear refusal messages for queries asking for advice (e.g., *"Which fund is better?"*).
    *   Ensure refusal responses include links to official SEBI or AMFI educational materials.

---

### ⏰ Phase 4: Daily Data Sync & Scheduler
**Goal:** Automate scraping updates so facts are always fresh without manually rebuilding databases.

*   [x] **4.1 Ingestion Scheduler Setup**
    *   Configure a GitHub Actions scheduled workflow (`daily_sync.yml`) to trigger daily at `00:00` UTC.
*   [x] **4.2 Content Hash / Checksum Check**
    *   Store hashes of scraped pages. The daily run checks the new content hash against the old one; if they match, database updates are skipped.
*   [x] **4.3 Global Metadata Update**
    *   On successful database rebuilds, write the current timestamp to a central `last_sync.json` config file.
    *   Expose this timestamp to the LLM generation prompt for the footer date.

---

### 🖥️ Phase 5: Decoupled Web Interface & Deployment
**Goal:** Create a polished, responsive user experience utilizing a FastAPI backend on Railway and a premium HTML/CSS/JS client-side frontend on Vercel.

*   [x] **5.1 Decoupled Frontend & Backend Development**
    *   Build a REST backend using FastAPI (`api.py`) allowing CORS, and a static web client (`index.html`, `styles.css`, `app.js`) to run on Vercel.
    *   Add a sticky top header status bar and a prominent warning disclaimer: `⚠️ Facts-only. No investment advice.`
*   [x] **5.2 Quick-Start Prompts**
    *   Include exactly three interactive cards representing typical factual questions to automatically trigger queries.
*   [x] **5.3 Compliance & Integration Verification**
    *   Test health status connection indicators, loading spinners, and ensure response format slicing & advisory refusals work perfectly in the web layout.

---

## 🔒 Verification & Compliance Gates

Before proceeding to production or staging, the assistant must pass all validation checks:

| Compliance Check | Target Criteria | Validation Method |
| :--- | :--- | :--- |
| **PII Leakage** | 0 sensitive items logged/sent to LLM | Regex/Security Scanner |
| **Response Length** | Max 3 sentences | Automated sentence tokenizer checks |
| **Citation Check** | Exactly 1 valid citation link | Link parsing validation |
| **Advisory Guard** | 100% refusal rate on opinion queries | Adversarial test suite |
| **Footer Synchronization** | Footer date matches `last_sync.json` | Snapshot checks |
