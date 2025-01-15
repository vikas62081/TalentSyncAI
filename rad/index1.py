import os
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Constants
PERSIST_DIR = "./chroma_db"
DATA_FILE = "./data/subs.csv"
EMBEDDING_MODEL_URL = "http://localhost:11434"
EMBEDDING_MODEL_NAME = "nomic-embed-text"
CHAT_MODEL_NAME = "llama3.1:8b"

# Step 1: Load and Process Documents
def load_and_split_documents(file_path):
    """Load documents from CSV and split them into smaller chunks."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    print("Loading documents from file...")
    raw_documents = CSVLoader(file_path).load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=20)
    return text_splitter.split_documents(raw_documents)

# Step 2: Initialize or Load Chroma Database
def initialize_or_load_chroma(persist_dir, documents, embedding_function):
    """Initialize a new Chroma DB or load an existing one."""
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print("Loading existing database...")
        return Chroma(persist_directory=persist_dir, embedding_function=embedding_function)
    else:
        print("Creating a new database...")
        db = Chroma.from_documents(documents, embedding=embedding_function, persist_directory=persist_dir)
        print("New database created and saved.")
        return db

# Step 3: Set Up the Chain
def create_chain(db, model_name):
    """Set up the retrieval and chat chain for answering questions."""
    retriever = db.as_retriever()
    
    # Define the prompt template
    template = """You are an HR person. Answer the question based only on the following context:

    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # Chat model
    model = ChatOllama(
        model=model_name,
        temperature=0
    )
    
    # Function to format retrieved documents
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    # Build the chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return chain

# Main Execution
def main():
    print("Starting system...")
    
    # Step 1: Load and split documents
    documents = load_and_split_documents(DATA_FILE)
    
    # Step 2: Initialize or load Chroma DB
    embedding_function = OllamaEmbeddings(base_url=EMBEDDING_MODEL_URL, model=EMBEDDING_MODEL_NAME)
    db = initialize_or_load_chroma(PERSIST_DIR, documents, embedding_function)
    
    # Step 3: Set up the chain
    chain = create_chain(db, CHAT_MODEL_NAME)
    
    print("\nYou can now ask questions. Type 'exit' or 'stop' to quit.")
    while True:
        question = input("\nAsk a question: ").strip()
        if question.lower() in {"exit", "stop"}:
            print("Exiting. Goodbye!")
            break
        try:
            answer = chain.invoke(question)
            print(f"\nAnswer:\n{answer}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()