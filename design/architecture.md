# System Architecture

## End-to-End Data Flow
The system follows a linear ETL (Extract, Transform, Load) pipeline followed by a RAG (Retrieval Augmented Generation) inference loop.

```mermaid
graph TD
    %% Nodes are wrapped in quotes to handle spaces safely
    %% <br/> is used to break long lines and prevent clipping
    
    A["PDF Invoice"] -->|Ingestion| B("Docling<br/>Extraction")
    B -->|"Raw<br/>Tables"| C{"Stitching<br/>Logic"}
    C -->|"Merged<br/>DataFrames"| D["Row<br/>Serialization"]
    D -->|"Enriched<br/>Chunks"| E[("LanceDB<br/>Vector Store")]
    
    F["User Query"] -->|"Semantic<br/>Search"| E
    E -->|"Top-k<br/>Context"| G["Llama-3<br/>LLM"]
    G -->|"Grounded<br/>Answer"| H["Final Output"]