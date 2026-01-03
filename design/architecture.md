# System Architecture

## End-to-End Data Flow
The system follows a linear ETL (Extract, Transform, Load) pipeline followed by a RAG (Retrieval Augmented Generation) inference loop.

%%{init: {'theme':'dark', 'themeVariables': {'fontSize':'16px'}, 'flowchart':{'nodeSpacing': 80, 'rankSpacing': 80, 'curve': 'basis'}}}%%
flowchart TD
    %% Define Nodes with Flowchart Shapes
    A(["PDF Invoice"]) -->|Ingestion| B["Docling<br/>Extraction"]
    B -->|"Raw Tables"| C{"Stitching<br/>Logic"}
    C -->|"Merged DataFrames"| D["Row<br/>Serialization"]
    D -->|"Enriched Chunks"| E[("LanceDB<br/>Vector Store")]
    
    F[/"User Query"/] -->|"Semantic Search"| E
    E -->|"Top-k Context"| G[["Llama-3<br/>LLM"]]
    G -->|"Grounded Answer"| H(["Final Output"])
    
    %% Styling
    style A fill:#1a202c,stroke:#4299e1,stroke-width:2px,color:#fff,stroke-dasharray: 5 5
    style B fill:#1a202c,stroke:#4299e1,stroke-width:2px,color:#fff
    style C fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#fff
    style D fill:#1a202c,stroke:#4299e1,stroke-width:2px,color:#fff
    style E fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#fff
    style F fill:#1a202c,stroke:#9f7aea,stroke-width:2px,color:#fff
    style G fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#fff
    style H fill:#1a202c,stroke:#9f7aea,stroke-width:2px,color:#fff
    
    %% Global Class Definition
    classDef default fill:#1a202c,stroke:#4a5568,stroke-width:2px,color:#fff