from langchain_community.llms import Ollama
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

def setup_rag_pipeline(vector_store):
    """
    Configures the Llama-3 based RAG chain with improved retrieval
    """
    # 1. Initialize Local LLM
    llm = OllamaLLM(
        model="llama3-local",  # Change this to match the name you used in 'ollama create'
        temperature=0.1
    )

    # 2. Configure Retriever with BETTER parameters
    # Use MMR (Maximum Marginal Relevance) for diverse results
    # and reduce k to get only the most relevant results
    retriever = vector_store.as_retriever(
        search_type="mmr",  # Changed from "similarity" to "mmr" for better diversity
        search_kwargs={
            "k": 15,  # Reduced from 100 to 15 - get top 15 most relevant
            "fetch_k": 50,  # Fetch 50 candidates, then select diverse 15
            "lambda_mult": 0.7  # Balance between relevance (1.0) and diversity (0.0)
        }
    )

    # 3. Improved Grounded Prompt
    prompt_template = """You are an expert financial assistant analyzing invoice data.

CRITICAL INSTRUCTIONS:
1. Use ONLY the invoice line items provided in the context below
2. If the answer is not in the context, respond with "Data not available in the invoiced documents."
3. When citing data, mention the invoice ID (e.g., "According to INV-1...")
4. For amounts, provide exact numbers from the context
5. Do not make up or estimate any numbers

Context (Invoice Line Items):
{context}

Question: {question}

Answer (be specific and cite invoice IDs):"""
    
    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["context", "question"]
    )

    # 4. Create the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # "stuff" puts all docs into one prompt
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True  # Return sources for debugging
    )

    return qa_chain