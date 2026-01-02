from langchain_community.llms import Ollama
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

def setup_rag_pipeline(vector_store):
    """
    Configures the Llama-3 based RAG chain
    """
    # 1. Initialize Local LLM
    llm = OllamaLLM(
                model="llama3-local",  #Change this to match the name you used in 'ollama create'
                temperature=0.1
        )


    # 2. Configure Retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 15} 
    )

    # 3. Grounded Prompt
    prompt_template = """
    You are an expert financial assistant. Use ONLY the following extracted invoice line items to answer the question.
    
    Rules:
    1. If the answer is not in the context, state "Data not available".
    2. Cite the row content when possible.
    3. Do not make up numbers.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}
    )

    return qa_chain