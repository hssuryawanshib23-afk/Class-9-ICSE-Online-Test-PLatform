import os
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class PhysicsChatbot:
    def __init__(self):
        """Initialize the chatbot with vector database and LLM"""
        self.VECTOR_DB_PATH = "vector_db"
        
        # Check if vector database exists
        if not Path(self.VECTOR_DB_PATH).exists():
            print("❌ Vector database not found!")
            print("Please run 'python setup_vectordb.py' first.")
            exit(1)
        
        print("🔄 Loading vector database...")
        
        # Initialize embeddings model
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load FAISS index and documents
        self.index = faiss.read_index(os.path.join(self.VECTOR_DB_PATH, "index.faiss"))
        with open(os.path.join(self.VECTOR_DB_PATH, "documents.pkl"), "rb") as f:
            self.documents = pickle.load(f)
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
        
        print("✅ Chatbot ready!\n")
    
    def ask(self, question):
        """Ask a question to the chatbot"""
        # Generate embedding for question
        question_embedding = self.embeddings_model.encode([question])
        
        # Search in FAISS
        k = 6
        distances, indices = self.index.search(question_embedding.astype('float32'), k)
        
        # Get relevant documents
        retrieved_docs = [self.documents[i] for i in indices[0]]
        
        # Build context
        context = "\n\n".join([doc['content'] for doc in retrieved_docs])
        
        # Create prompt
        prompt = f"""You are a Class 9 Physics tutor teaching from the Selina textbook.

Use ONLY the provided context to answer the question. If the context doesn't contain the answer, respond with:
"This question is outside the syllabus provided."

Context from textbook:
{context}

Student's Question: {question}

Instructions:
- Explain concepts in simple Class 9 language
- For numerical problems, show step-by-step solutions
- Include formulas when relevant
- If diagrams are mentioned, describe them in words
- Stay accurate to the Selina textbook content
- Do NOT use external knowledge

Answer:"""
        
        # Get response from Gemini
        response = self.model.generate_content(prompt)
        answer = response.text
        
        # Extract source chapters
        sources = set([doc['source'] for doc in retrieved_docs])
        
        # Format response
        final_response = f"{answer}\n\n📚 Source: {', '.join(sources)}"
        return final_response

def main():
    """Main chatbot loop"""
    print("=" * 60)
    print("🎓 Class 9 Physics Chatbot (Selina Syllabus)")
    print("=" * 60)
    
    chatbot = PhysicsChatbot()
    
    print("Type your physics questions below.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        question = input("You: ").strip()
        
        if not question:
            continue
        
        if question.lower() in ['exit', 'quit']:
            print("👋 Goodbye! Happy studying!")
            break
        
        print("\n🤖 Chatbot: ", end="")
        answer = chatbot.ask(question)
        print(answer)
        print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    main()