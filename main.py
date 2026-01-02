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
    
    # --- ARGUMENTS ---
    parser.add_argument("--ingest", type=str, help="Path to PDF invoice to ingest")
    parser.add_argument("--query", type=str, help="Question to ask about the invoices")
    parser.add_argument("--id", type=str, default="INV-001", help="Invoice ID for metadata")
    parser.add_argument("--vendor", type=str, default="Unknown", help="Vendor name for metadata")
    parser.add_argument("--date", type=str, default="2024-01-01", help="Invoice date")
    parser.add_argument("--output", type=str, help="Path to save the query result (e.g., answer.txt)")

    args = parser.parse_args()

    # Define DB Path
    db_path = "./invoice_db"

    # --- INGESTION PHASE ---
    if args.ingest:
        print(f"Processing {args.ingest}...")
        
        # 1. Ingest
        raw_data = ingest_invoice(args.ingest)
        if not raw_data:
            print("Ingestion failed or returned no data.")
            return

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
        create_index(stitched_dfs, metadata, db_path=db_path)
        print("✓ Ingestion Complete. Data Indexed in LanceDB.")

    # --- QUERY PHASE ---
    if args.query:
        print(f"Querying: {args.query}")
        
        # Connect to existing DB for retrieval
        db = lancedb.connect(db_path)
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
        
        try:
            # Open existing table with mode='append' to ensure we read all data
            vector_store = LanceDB(
                connection=db, 
                embedding=embeddings, 
                table_name="line_items",
                mode='append'  # Use append mode to preserve existing data
            )
            
            # Show table info
            table = db.open_table("line_items")
            print(f"Database contains {table.count_rows()} total rows")
            
            # 4. Run RAG
            qa = setup_rag_pipeline(vector_store)
            response = qa.invoke(args.query)
            
            answer_text = response['result']
            
            # Show retrieved sources for debugging
            if 'source_documents' in response:
                print(f"\n>> Retrieved {len(response['source_documents'])} relevant documents")
                print(">> Top 3 sources:")
                for i, doc in enumerate(response['source_documents'][:3]):
                    metadata = doc.metadata
                    print(f"   {i+1}. Invoice {metadata.get('invoice_id', 'N/A')} - {metadata.get('original_text', '')[:100]}...")

            # Print to Console
            print("\n>> ANSWER:")
            print(answer_text)

            # Save to file if requested
            if args.output:
                try:
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(f"Query: {args.query}\n")
                        f.write("-" * 30 + "\n")
                        f.write(answer_text)
                    print(f"\n✓ Result saved to: {args.output}")
                except Exception as file_error:
                    print(f"\n✗ Could not save to file: {file_error}")
            
        except Exception as e:
            print(f"✗ Error querying database. (Did you ingest an invoice first?)\nDetails: {e}")

if __name__ == "__main__":
    main()