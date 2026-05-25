# AI Document & Contract Analyzer (RAG) Implementation Plan

This project implements a full-stack, AI-powered document/contract analyzer. It allows users to upload PDF contracts, automatically parses them, generates vector embeddings, creates a FAISS index, extracts key legal clauses with risk assessments, provides an executive summary, and allows direct conversation with the document using Retrieval-Augmented Generation (RAG).

The application leverages **FastAPI** on the backend, **Vite + React** with **Vanilla CSS** on the frontend, and utilizes the new **Google Gemini API** (using `google-genai`) for embeddings and reasoning.

---

## User Review Required

> [!IMPORTANT]
> The backend requires a `GEMINI_API_KEY` to generate vector embeddings (`text-embedding-004`) and run LLM completions (`gemini-2.5-flash`). Please ensure you have your API key ready and place it in the `.env` file in the project root.

> [!TIP]
> The design uses a premium, dark-mode glassmorphic theme with a violet/indigo accent palette, smooth micro-animations, and dynamic visual indicators for clause risk levels. No external CSS libraries (like Tailwind) are used, in line with modern web development guidelines.

---

## Proposed Changes

We will create a full-stack workspace under `e:\AIDocs`.

```
AIDocs/
├── backend/
│   ├── main.py              # FastAPI application server
│   ├── parser.py            # PDF document text extraction (pypdf)
│   ├── chunker.py           # Overlapping text chunking engine
│   ├── embedder.py          # Vector embedding & local FAISS indexing
│   ├── rag.py               # RAG retriever and question answering agent
│   └── prompts.py           # Structured prompt templates for Gemini
├── frontend/
│   ├── index.html           # HTML container with Google Fonts ("Outfit" & "Inter")
│   ├── src/
│   │   ├── main.jsx         # Vite entrypoint
│   │   ├── App.jsx          # App layout and state manager
│   │   ├── index.css        # Premium Vanilla CSS styling, variables, glassmorphic styles
│   │   └── components/
│   │       ├── UploadPanel.jsx   # Drag-and-drop file upload with progress feedback
│   │       ├── SummaryPanel.jsx  # Structured document summary cards
│   │       ├── ClauseTable.jsx   # Searchable legal clause matrix with risk tags
│   │       └── ChatPanel.jsx     # Conversational chatbot with source citations
├── requirements.txt         # Backend Python dependencies
└── README.md                # Project startup and operational handbook
```

---

### Backend (Python/FastAPI)

We will use standard lightweight libraries: `fastapi` for endpoints, `pypdf` for parsing, `faiss-cpu` for the vector DB, and the state-of-the-art `google-genai` SDK for model interactions.

#### [NEW] [requirements.txt](file:///e:/AIDocs/requirements.txt)
Defines Python dependencies:
- `fastapi` & `uvicorn`
- `pypdf` (fast, reliable PDF parser)
- `faiss-cpu` (high-performance local similarity search)
- `google-genai` (official modern Gemini SDK)
- `python-multipart` & `python-dotenv` & `pydantic`

#### [NEW] [parser.py](file:///e:/AIDocs/backend/parser.py)
Extracts raw text and maps page numbers from PDF files using `pypdf`. Returns structured pages:
```python
def extract_text_by_page(file_path: str) -> list[dict]:
    # Returns [{"page": page_num, "text": page_text}, ...]
```

#### [NEW] [chunker.py](file:///e:/AIDocs/backend/chunker.py)
Splits extracted pages into chunks with specified overlapping size (e.g., 1000 characters chunk, 200 character overlap) while carrying over the source page metadata:
```python
def split_pages_into_chunks(pages: list[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    # Returns [{"chunk_id": id, "page": page, "text": chunk_text}, ...]
```

#### [NEW] [embedder.py](file:///e:/AIDocs/backend/embedder.py)
Coordinates embedding creation and index saving.
- Generates 768-dimension embeddings via `client.models.embed_content(model="text-embedding-004", ...)`
- Creates a `faiss.IndexFlatL2` index
- Saves FAISS index binary and a mapping JSON (chunk text + page reference metadata) to disk under `backend/data/{doc_id}/`

#### [NEW] [prompts.py](file:///e:/AIDocs/backend/prompts.py)
Contains structured prompt templates. Gemini excels at structured JSON extraction when prompted correctly.
- **Summary Prompt**: Prompts Gemini to parse the full document text and return JSON mapping key attributes (parties, execution date, duration, total value, core business summary, and primary obligations).
- **Clause Extraction Prompt**: Analyzes the contract and extracts standard legal clauses (e.g. Indemnity, Termination, Liability Limits, Governing Law, Intellectual Property) with a "Risk Level" (High/Medium/Low), "Risk Explanation", "Confidence Score", and the "Exact Quote".
- **RAG QA Prompt**: Prompts Gemini to answer user questions using only the retrieved context chunks, referencing exact source page numbers.

#### [NEW] [rag.py](file:///e:/AIDocs/backend/rag.py)
Orchestrates high-level RAG operations and pipeline triggers:
- `analyze_document_full(text: str)`: Calls Gemini with the Summary and Clause prompts to extract full contract structures.
- `rag_query(doc_id: str, query: str)`:
  1. Embeds query.
  2. Loads FAISS index and finds top 4 matches.
  3. Prepares context.
  4. Runs Gemini 2.5 Flash to generate context-aware answers.

#### [NEW] [main.py](file:///e:/AIDocs/backend/main.py)
FastAPI application containing the endpoints:
- `POST /api/upload`: Upload PDF, parse, chunk, embed, index, analyze (summary + clauses), save everything under a generated `doc_id`, return document analysis.
- `GET /api/documents/{doc_id}`: Read and return saved analysis details.
- `POST /api/chat`: Runs RAG query for a given query and `doc_id`, returns answer with citations.

---

### Frontend (Vite + React + Vanilla CSS)

The frontend features a stunning dark glassmorphic design system using rich, modern typography and HSL variables.

#### [NEW] [index.css](file:///e:/AIDocs/frontend/src/index.css)
Creates our premium design system.
- Harmonious dark color scheme: Deep cosmos background (`#080b11`), card backdrops (`rgba(16, 22, 35, 0.6)` with backdrop filter blur), border color (`rgba(255, 255, 255, 0.08)`), text colors, and risk tag colors.
- Interactive hover transitions, pulse animations for upload progress, and smooth glow-shadows.

#### [NEW] [App.jsx](file:///e:/AIDocs/frontend/src/App.jsx)
Main entrypoint and state controller.
- Tracks active `documentId`, `analysis` structure (summary & clauses), `loading` states, and `error` states.
- Implements two main layouts:
  1. **Landing Layout**: Prominent upload container with title and subtext.
  2. **Dashboard Layout**: Split-screen design. Left Column shows executive summary widgets and a search/filter enabled Clause Matrix. Right Column displays the interactive conversation RAG chatbot.

#### [NEW] [UploadPanel.jsx](file:///e:/AIDocs/frontend/src/components/UploadPanel.jsx)
Dynamic drag-and-drop component.
- Visual state for drag over.
- Displays animated progress percentage during server upload and processing.
- Clean file type validation.

#### [NEW] [SummaryPanel.jsx](file:///e:/AIDocs/frontend/src/components/SummaryPanel.jsx)
Renders the executive summary of the document.
- Key-value cards displaying Parties, Execution Date, Duration, and Contract Value.
- A descriptive narrative card detailing the primary scope and key obligations.

#### [NEW] [ClauseTable.jsx](file:///e:/AIDocs/frontend/src/components/ClauseTable.jsx)
Renders extracted clauses in a modern dashboard interface.
- Filter chips (All, High Risk, Medium Risk, Low Risk).
- Search bar to filter clauses by name, explanation, or quote.
- Expandable rows: Clicking a row shows the "Exact Quote" highlighted in a modern legal text card.
- Modern visual risk tags (Red for High, Amber for Medium, Green for Low).

#### [NEW] [ChatPanel.jsx](file:///e:/AIDocs/frontend/src/components/ChatPanel.jsx)
Interactive conversational chat drawer/panel.
- Displays message feed (User / Assistant) with typing animations.
- Highlights and maps source citations (e.g. clicking `[Page 4]` highlights the exact snippet in the chat context or allows the user to see where it came from).
- Persistent state for the current session.

---

## Verification Plan

### Automated/Local Build Checks
1. **Backend Verification**:
   - Run local server using `uvicorn backend.main:app --reload --port 8000`
   - Test PDF parsing, chunking, FAISS index creation, and model responses using raw curls or simple test scripts.
2. **Frontend Verification**:
   - Run dev server using `npm run dev` (Vite)
   - Ensure hot reloading and standard styling work flawlessly.
3. **Integration Verification**:
   - Verify CORS allows React dev server to communicate with FastAPI.
   - Verify upload parsing, summary generation, clause table population, and chatbot responsiveness.

### Manual Verification
- Upload test legal agreements (e.g. standard NDAs, Service Level Agreements).
- Confirm that the extracted clauses correctly capture key liability terms.
- Confirm the chatbot only responds with info contained in the document, citing page numbers correctly.
