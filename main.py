import argparse
import os
import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_huggingface import HuggingFaceEmbeddings

from src.ingest import ingest_invoice
from src.process import process_and_stitch
from src.index import create_index
from src.rag import setup_rag_pipeline

def main():
    parser = argparse.ArgumentParser(description="AI Invoice Extraction System")
    parser.add_argument("--ingest", type=str, help="Path to PDF invoice to ingest")
    parser.add_argument("--query", type=str, help="Question to ask about the invoices")
    parser.add_argument("--id", type=str, default="INV-001", help="Invoice ID for metadata")
    parser.add_argument("--vendor", type=str, default="Unknown", help="Vendor name for metadata")
    parser.add_argument("--date", type=str, default="2024-01-01", help="Invoice date")

    args = parser.parse_args()

    # Define DB Path
    db_path = "./invoice_db"

    # INGESTION PHASE 
    if args.ingest:
        print(f"Processing {args.ingest} ")
        
        # 1. Ingest
        raw_data = ingest_invoice(args.ingest)
        if not raw_data:
            print("Ingestion failed or returned no data.")
            return

        print(raw_data)
        # 2. Stitch
        stitched_dfs = process_and_stitch(raw_data)
        print(f"Extracted {len(stitched_dfs)} logical tables.")

        print(stitched_dfs)
        # 3. Index
        metadata = {
            "id": args.id,
            "vendor": args.vendor,
            "date": args.date
        }
        print(metadata)
        # Uses the global import 'create_index'

        create_index(stitched_dfs, metadata, db_path=db_path)
        print("Ingestion Complete. Data Indexed in LanceDB ")

    # QUERY PHASE 
    if args.query:
        print(f"Querying: {args.query} ")
        
        # Connect to existing DB for retrieval
        db = lancedb.connect(db_path)
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
        
        try:
            # Open existing table
            vector_store = LanceDB(
                connection=db, 
                embedding=embeddings, 
                table_name="line_items"
            )
            
            # 4. Run RAG
            qa = setup_rag_pipeline(vector_store)
            response = qa.invoke(args.query)
            
            print("\n>> ANSWER:")
            print(response['result'])
            
        except Exception as e:
            print(f"Error querying database. (Did you ingest an invoice first?)\nDetails: {e}")

if __name__ == "__main__":
    main()