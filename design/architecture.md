# System Architecture

## End-to-End Data Flow
The system follows a linear ETL (Extract, Transform, Load) pipeline followed by a RAG (Retrieval Augmented Generation) inference loop.

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'fontSize':'14px', 'fontFamily':'arial'}, 'flowchart':{'nodeSpacing': 150, 'rankSpacing': 120, 'padding': 30, 'curve': 'basis'}}}%%
graph TD
    A["PDF<br/>Invoice"] 
    B["Docling<br/>Extraction"]
    C{"Stitching<br/>Logic"}
    D["Row<br/>Serialization"]
    E[("LanceDB<br/>Vector Store")]
    F["User<br/>Query"]
    G["Llama-3<br/>LLM"]
    H["Final<br/>Output"]
    
    A -->|Ingestion| B
    B -->|Raw Tables| C
    C -->|Merged DataFrames| D
    D -->|Enriched Chunks| E
    F -->|Semantic Search| E
    E -->|Top-k Context| G
    G -->|Grounded Answer| H
    
    style A fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff,padding:15px
    style B fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff,padding:15px
    style C fill:#7c2d12,stroke:#ea580c,stroke-width:3px,color:#fff,padding:20px
    style D fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff,padding:15px
    style E fill:#14532d,stroke:#22c55e,stroke-width:3px,color:#fff,padding:15px
    style F fill:#581c87,stroke:#a855f7,stroke-width:2px,color:#fff,padding:15px
    style G fill:#14532d,stroke:#22c55e,stroke-width:3px,color:#fff,padding:15px
    style H fill:#581c87,stroke:#a855f7,stroke-width:2px,color:#fff,padding:15px
```