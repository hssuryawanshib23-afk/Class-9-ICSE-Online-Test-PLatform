#333333333333333333333333333333333333333333333333333333333333333333333333333333import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_vector_database():
    """
    Load all PDFs, split into chunks, create embeddings, and save to FAISS
    """
    print("🚀 Starting Vector Database Setup...")
    
    # Configuration
    PDF_FOLDER = Path("pdfs")
    VECTOR_DB_PATH = "vector_db/faiss_index"
    
    # Check if PDFs folder exists
    if not PDF_FOLDER.exists():
        print("❌ Error: 'pdfs' folder not found!")
        print("Please create a 'pdfs' folder and add all 10 PDF files.")
        return
    
    # Get all PDF files
    pdf_files = list(PDF_FOLDER.glob("*.pdf"))
    
    if len(pdf_files) == 0:
        print("❌ No PDF files found in 'pdfs' folder!")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files")
    
    # Load all PDFs
    all_documents = []
    for pdf_path in pdf_files:
        print(f"   Loading: {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()
        
        # Add source metadata
        for doc in documents:
            doc.metadata["source"] = pdf_path.stem  # Filename without extension
        
        all_documents.extend(documents)
    
    print(f"✅ Loaded {len(all_documents)} pages total")
    
    # Split documents into chunks
    print("✂️  Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(all_documents)
    print(f"✅ Created {len(chunks)} text chunks")
    
    # Create embeddings using HuggingFace (FREE, LOCAL, NO API LIMITS)
    print("🧠 Creating embeddings using HuggingFace (free, local)...")
    print("   (First time will download ~90MB model, please wait...)")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"  # Fast and accurate model
    )
    
    # Create FAISS vector store in batches to avoid memory issues
    print("💾 Building FAISS vector database...")
    
    # Process in batches of 50 chunks
    batch_size = 50
    vectorstore = None
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"   Processing batch {i//batch_size + 1}/{(len(chunks)//batch_size) + 1}...")
        
        if vectorstore is None:
            # Create initial vectorstore
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            # Add to existing vectorstore
            batch_vectorstore = FAISS.from_documents(batch, embeddings)
            vectorstore.merge_from(batch_vectorstore)
    
    # Save to disk
    os.makedirs("vector_db", exist_ok=True)
    vectorstore.save_local(VECTOR_DB_PATH)
    
    print(f"✅ Vector database saved to: {VECTOR_DB_PATH}")
    print("🎉 Setup complete! You can now run main.py")

if __name__ == "__main__":
    setup_vector_database()
