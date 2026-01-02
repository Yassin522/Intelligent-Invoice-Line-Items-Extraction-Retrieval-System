# Intelligent-Invoice-Line-Items-Extraction-Retrieval-System

A system designed to ingest complex multi-page invoices, extract line-item data, and perform grounded Q&A using Retrieval Augmented Generation.

## Extraction Strategy
**Hybrid Vision-Structural Approach:**
We utilize **Docling** for its superior Table Structure Recognition (TSR). Unlike pure OCR which outputs a stream of text, Docling identifies the logical topology of tables (cells, rows, columns).
* **Multi-Page Handling:** A custom "Stitching Algorithm" (`src/process.py`) is implemented. It iterates through extracted table fragments and merges them based on heuristic continuity checks (matching column counts, sequential page numbers, and header similarity).

## Chunking Strategy
**Row-Centric Semantic Chunking:**
Standard token-based chunking breaks data integrity in tabular data. Instead, we treat **each table row** as an atomic unit.
* **Serialization:** Each row is converted into a key-value string (e.g., `Description: Laptop | Price: 400`).
* **Metadata Preservation:** Every chunk is enriched with global invoice metadata (Invoice ID, Vendor, Date) before embedding, enabling the retriever to distinguish between identical items from different vendors.

## Storage & Retrieval
**Storage: LanceDB**
* **Selected** for its embedded, serverless nature. It runs in-process, supports high-performance vector search, and persists data to disk easily.
* **Filtering:** The schema stores metadata (`invoice_id`, `vendor`) alongside vectors, allowing for potential pre-filtering in future iterations.

## LLM & Embeddings
* **LLM: Llama-3 (via Ollama):** Chosen for its state-of-the-art reasoning capabilities in the open-source 8B class. It offers a balance of privacy (local execution) and performance.
* **Embeddings: BAAI/bge-base-en-v1.5:** Selected based on MTEB leaderboards. It is optimized for retrieval tasks and performs significantly better than standard BERT models for dense retrieval.

## Evaluation Approach
To evaluate the system's accuracy without extensive human labeling, we recommend using **Ragas** (Retrieval Augmented Generation Assessment).
* **Faithfulness:** Measures if the generated answer is derived *only* from the retrieved invoice rows (no hallucinations).
* **Context Precision:** Measures if the retrieval system (LanceDB) correctly ranked the relevant line items in the top-k results.

## Setup & Run
1. **Install dependencies:** `pip install -r requirements.txt`
2. **Setup Local LLM:** Ensure Ollama is running and pull the model: `ollama pull llama3`
3. **Ingest Invoices:**
    ```bash
    python main.py --ingest invoices/INV-1.pdf --id "INV-1" --vendor "FruitCo" --date "2024-01-01"
    ```
4. **Query the System:**
    ```bash
    python main.py --query "What is the total amount for INV-1?" --output answers.txt
    ```

### **Important: Update `src/rag.py` to match**
For the instructions above to work without errors, you must change `model="llama3-local"` to `model="llama3"` in your code:

```python
    llm = OllamaLLM(
        model="llama3",  # Changed from "llama3-local" to match the standard pull command
        temperature=0.1
    )