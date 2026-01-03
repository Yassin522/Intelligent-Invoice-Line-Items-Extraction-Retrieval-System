# System Architecture

## End-to-End Data Flow
The system follows a linear ETL (Extract, Transform, Load) pipeline followed by a RAG (Retrieval Augmented Generation) inference loop.

%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#2dd4bf',
    'primaryTextColor': '#fff',
    'primaryBorderColor': '#111827',
    'lineColor': '#94a3b8',
    'secondaryColor': '#818cf8',
    'tertiaryColor': '#f472b6',
    'fontFamily': 'arial'
  }
}}%%

flowchart LR
    %% GLOBAL STYLES
    classDef base fill:#1e293b,stroke:#334155,stroke-width:2px,color:#fff,rx:5,ry:5
    classDef input fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#38bdf8,stroke-dasharray: 5 5
    classDef logic fill:#1e293b,stroke:#fbbf24,stroke-width:2px,color:#fbbf24
    classDef db fill:#1e293b,stroke:#4ade80,stroke-width:2px,color:#4ade80,shape:cylinder
    classDef ai fill:#312e81,stroke:#818cf8,stroke-width:3px,color:#fff,rx:10,ry:10
    classDef final fill:#831843,stroke:#f472b6,stroke-width:2px,color:#fff,rx:10,ry:10

    %% SHARED RESOURCE (Center)
    subgraph Storage [" Knowledge Base "]
        direction TB
        E[("LanceDB<br/>Vector Store")]:::db
    end

    %% TOP STREAM: INGESTION
    subgraph ETL [" 🛠️ Ingestion Pipeline "]
        direction LR
        A("PDF Invoice"):::input -->|Ingest| B("Docling<br/>Extraction"):::base
        B -->|Raw Tables| C{"Stitching<br/>Logic"}:::logic
        C -->|Merged Data| D("Row<br/>Serialization"):::base
        D -.->|Enriched Chunks| E
    end

    %% BOTTOM STREAM: INFERENCE
    subgraph RAG [" 🧠 RAG Inference "]
        direction LR
        F(/"User Query"/):::input -->|Semantic Search| E
        E -.->|Top-k Context| G["Llama-3<br/>LLM"]:::ai
        G -->|Result| H(["Grounded<br/>Answer"]):::final
    end

    %% Link Styles for curves
    linkStyle default stroke:#64748b,stroke-width:2px,fill:none