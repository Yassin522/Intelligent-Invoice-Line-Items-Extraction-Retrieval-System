# System Architecture

## End-to-End Data Flow
The system follows a linear ETL (Extract, Transform, Load) pipeline followed by a RAG (Retrieval Augmented Generation) inference loop.

```mermaid
%%{init: {
  "theme": "dark",
  "flowchart": {
    "nodeSpacing": 80,
    "rankSpacing": 100,
    "htmlLabels": true
  },
  "themeVariables": {
    "fontSize": "16px"
  }
}}%%
graph TD
    A[PDF<br/>Invoice] -->|Ingestion| B[Docling<br/>Extraction]
    B -->|Raw<br/>Tables| C{Stitching<br/>Logic}
    C -->|Merged<br/>DataFrames| D[Row<br/>Serialization]
    D -->|Enriched<br/>Chunks| E[(LanceDB<br/>Vector Store)]
    
    F[User<br/>Query] -->|Semantic<br/>Search| E
    E -->|Top-k<br/>Context| G[Llama-3<br/>LLM]
    G -->|Grounded<br/>Answer| H[Final<br/>Output]
