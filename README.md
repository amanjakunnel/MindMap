# Wordie — AI-Powered Mind Map Generator

**Wordie** turns any document into an interactive 3D mind map. Upload a PDF, DOCX, or TXT file, and the backend uses NLP to extract key concepts and relationships, which are then visualized as a navigable mind map in the browser.

---

## How It Works

1. **Upload** a document (PDF, DOCX, or TXT) on the home page
2. **Backend processes** the text using spaCy + Sentence Transformers to extract the top 5 keywords and up to 5 relevant sub-phrases per keyword
3. **Interactive mind map** is rendered in 3D using Three.js — zoom, pan, and hover to explore
4. **History** stores your last 5 generated maps in the browser for quick re-access

### Mind Map Structure
```
Root (Document Title)
├── Keyword 1
│   ├── Sub-phrase A
│   ├── Sub-phrase B
│   └── Sub-phrase C
├── Keyword 2
│   └── ...
└── ...
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 16, React Router 6, Three.js 0.123 |
| Styling | Styled Components, custom CSS |
| HTTP | Axios |
| Backend | Python, Flask |
| NLP | spaCy (`en_core_web_lg`), NLTK, Sentence Transformers (`all-MiniLM-L6-v2`) |
| Persistence | Browser localStorage (up to 5 maps) |

---

## Setup & Running

### Prerequisites
- Node.js (v14+)
- Python 3.8+
- pip

### 1. Frontend
```bash
npm install
npm start
# Runs on http://localhost:3000
```

### 2. Backend
```bash
cd Server
pip install flask flask-cors spacy nltk sentence-transformers python-docx PyPDF2
python -m spacy download en_core_web_lg
python server.py
# Runs on http://localhost:5001
```

> Both servers must be running at the same time for uploads to work.

---

## Project Structure

```
MindMap/
├── public/
│   └── index.html          # Node label CSS styles
├── src/
│   ├── App.js              # Router (Home, MindMap, History)
│   ├── pages/
│   │   ├── Home.js         # Upload page
│   │   ├── MindMap.js      # Viewer page
│   │   └── History.js      # Saved maps list
│   └── components/
│       ├── FileUploader.js             # Upload form + API call
│       ├── RenderMindMap.js            # Three.js rendering engine
│       ├── InitializeScene.js          # WebGL + CSS2D renderer setup
│       ├── addMindMapNode.js           # Creates DOM nodes in scene
│       ├── calculateLevel2Coordinates.js  # Fan-arc layout math
│       ├── Menu.js                     # Navigation bar
│       └── FinalMindMapRender.js       # Render wrapper
└── Server/
    ├── server.py           # Flask API (/saveDoc endpoint)
    └── mindmapgen.py       # NLP pipeline (extraction + deduplication)
```

---

## Features

- **Document Parsing** — extracts clean text from PDF, DOCX, and TXT, stripping references, citations, and formatting artifacts
- **Semantic Keyword Extraction** — ranks nouns/proper nouns by frequency, filters stop words and title variants
- **Sub-phrase Mining** — finds noun chunks most semantically similar to each keyword via sentence embeddings
- **Cross-branch Deduplication** — removes near-duplicate phrases across branches (0.88 cosine similarity threshold)
- **3D Visualization** — hybrid WebGL (connections) + CSS2D (labels) rendering with pan, zoom, and hover tooltips
- **History** — auto-saves to localStorage, accessible from the nav bar
