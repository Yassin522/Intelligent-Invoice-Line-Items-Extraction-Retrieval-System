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
    parser.add_argument("--output", type=str, help="Path to save the query result (e.g., answer.txt)")

    args = parser.parse_args()

    # Define DB Path
    db_path = "./invoice_db"

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
        print("Ingestion Complete. Data Indexed in LanceDB.")

    if args.query:
        print(f"Querying: {args.query}")
        
        # Connect to existing DB for retrieval
        db = lancedb.connect(db_path)
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
        
        try:
       
            vector_store = LanceDB(
                connection=db, 
                embedding=embeddings, 
                table_name="line_items",
                mode='append'  
            )
            
            table = db.open_table("line_items")
            print(f"Database contains {table.count_rows()} total rows")
            
            # 4. Run RAG
            qa = setup_rag_pipeline(vector_store)
            response = qa.invoke(args.query)
            
            answer_text = response['result']
            
            if 'source_documents' in response:
                print(f"\nRetrieved {len(response['source_documents'])} relevant documents")
                print("Top 10 sources:")
                for i, doc in enumerate(response['source_documents'][:10]):
                    metadata = doc.metadata
                    print(f"   {i+1}. Invoice {metadata.get('invoice_id', 'N/A')} - {metadata.get('original_text', '')[:100]}...")

            # Print to Console
            print("\n>> ANSWER:")
            print(answer_text)

           
            if args.output:
                try:
                    with open(args.output, "a", encoding="utf-8") as f:
                        f.write("\n" + "="*50 + "\n") 
                        f.write(f"Query: {args.query}\n")
                        f.write("-" * 30 + "\n")
                        f.write(answer_text + "\n")
                    print(f"\n✓ Result appended to: {args.output}")
                except Exception as file_error:
                    print(f"\n✗ Could not save to file: {file_error}")
            
        except Exception as e:
            print(f"Error querying database.\nDetails: {e}")

if __name__ == "__main__":
    main()