# Design Decisions & Trade-offs

## Structure-Aware vs. Plain Text
**Decision:** We chose to parse documents as **Tables** rather than plain text.
* **Reasoning:** Invoices are fundamentally structured data. Flattening them into plain text destroys relationships between headers and values.
* **Trade-off:** This approach relies heavily on the extraction model (Docling) correctly identifying the table region. If the model fails to see a table, the data is missed. A hybrid approach (fallback to OCR text) could mitigate this in production.

## Local vs. Cloud Architecture
**Decision:** Fully local stack (Ollama + LanceDB).
* **Reasoning:** Privacy is paramount for financial documents. This architecture ensures no data leaves the execution environment.
* **Trade-off:** Running Llama-3 locally requires decent hardware (RAM/GPU). Cloud APIs (GPT-4) would offer higher reasoning accuracy but introduce cost and privacy risks.

## Stitching Heuristics
**Decision:** Rule-based table stitching.
* **Reasoning:** Training a custom ML model to detect page splits requires a massive labeled dataset. Heuristic rules (column matching, page continuity) are effective for standard invoices.
* **Failure Mode:** If an invoice changes column widths significantly between pages, the stitcher might treat them as separate tables.

## Scalability Considerations
* **Ingestion:** Currently, processing is sequential. For enterprise scale (millions of invoices), the `main.py` ingestion loop should be parallelized using a task queue.