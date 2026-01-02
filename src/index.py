import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd
import os

def create_index(tables, invoice_metadata, db_path="./invoice_db"):
    """
    Serializes tables and stores them in LanceDB[cite: 270].
    """
    # 1. Setup Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    # 2. Connect to LanceDB
    db = lancedb.connect(db_path)
    
    docs = []
    metadatas = []

    for table_id, df in enumerate(tables):
        # Ensure headers are strings
        headers = [str(h) for h in df.columns.tolist()]
        
        for idx, row in df.iterrows():
            # 3. Schema Serialization

            row_content = " | ".join([f"{h}: {str(val)}" for h, val in zip(headers, row.values)])
            
            # Enrich with Invoice Metadata
            full_text = f"Invoice: {invoice_metadata['id']}. Vendor: {invoice_metadata['vendor']}. Data: {row_content}"
            
            docs.append(full_text)
            metadatas.append({
                "invoice_id": invoice_metadata['id'],
                "vendor": invoice_metadata['vendor'],
                "date": invoice_metadata['date'],
                "row_id": idx,
                "table_id": table_id,
                "original_text": row_content 
            })

    if not docs:
        print("No documents to index.")
        return None

    # 4. Ingest into LanceDB 
    # table_name="line_items"
    vector_store = LanceDB.from_texts(
        texts=docs,
        embedding=embeddings,
        metadatas=metadatas,
        connection=db,
        table_name="line_items"
    )
    
    return vector_store