import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

def create_index(tables, invoice_metadata, db_path="./invoice_db"):
    """
    Serializes tables and stores them in LanceDB.
    Uses mode='append' to ensure data is APPENDED, not overwritten.
    """
    # 1. Setup Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    # 2. Connect to LanceDB
    db = lancedb.connect(db_path)
    table_name = "line_items"
    
    docs = []
    metadatas = []

    # Process extracted tables
    for table_id, df in enumerate(tables):
        headers = [str(h) for h in df.columns.tolist()]
        
        for idx, row in df.iterrows():
            # 3. Schema Serialization
            row_content = " | ".join([f"{h}: {str(val)}" for h, val in zip(headers, row.values)])
            
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
    print(f"Ingesting {len(docs)} rows into LanceDB...")

    try:
        # --- CHECK IF TABLE EXISTS ---
        table = db.open_table(table_name)
        
        print(f"✓ Table '{table_name}' found. Appending {len(docs)} documents...")
        
        # CRITICAL FIX: Use mode='append' to add to existing data
        vector_store = LanceDB(
            connection=db,
            embedding=embeddings,
            table_name=table_name,
            mode='append'  # THIS IS THE KEY FIX!
        )
        
        # Add new texts (this will append to existing table)
        vector_store.add_texts(texts=docs, metadatas=metadatas)
        
        print(f"✓ Successfully appended {len(docs)} documents. Total records in table now.")
        
    except Exception as e:
        # --- CREATE NEW TABLE ---
        print(f"Table '{table_name}' not found. Creating new table with {len(docs)} documents...")
        
        # For new tables, use from_texts which creates the table
        vector_store = LanceDB.from_texts(
            texts=docs,
            embedding=embeddings,
            metadatas=metadatas,
            connection=db,
            table_name=table_name,
            mode='append'  # Set to append mode from the start
        )
        
        print(f"✓ Successfully created new table with {len(docs)} documents.")
    
    return vector_store