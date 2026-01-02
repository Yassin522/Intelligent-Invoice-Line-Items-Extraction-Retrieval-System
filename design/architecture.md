# System Architecture

## End-to-End Data Flow
The system follows a linear ETL (Extract, Transform, Load) pipeline followed by a RAG (Retrieval Augmented Generation) inference loop.

```mermaid
graph LR
    A[PDF Invoice] -->|Ingestion| B(Docling Extraction)
    B -->|Raw Tables| C{Stitching Logic}
    C -->|Merged DataFrames| D[Row Serialization]
    D -->|Enriched Chunks| E[(LanceDB Vector Store)]
    
    F[User Query] -->|Semantic Search| E
    E -->|Top-k Context| G[Llama-3 LLM]
    G -->|Grounded Answer| H[Final Output]