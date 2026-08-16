# 🤖 AI Knowledge Assistant


An AI-powered Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions based on their content.


The system extracts text from uploaded documents, splits it into meaningful chunks, converts the chunks into vector embeddings, performs semantic similarity search, and uses Google Gemini to generate answers based only on the retrieved document context.


---


## 🚀 Features


- 📄 Upload PDF documents
- 🔄 Replace existing PDF files automatically
- 🧩 Automatic document chunking
- 🔢 Google Gemini embeddings
- 🗄️ Chroma vector database
- 🔎 Semantic similarity search
- 🤖 Gemini-powered answer generation
- 📚 Source document display
- 🔍 View relevant retrieved information
- 💬 Persistent chat history
- 🗑️ Delete uploaded documents
- 🧹 Clear chat history
- ⚠️ Gemini API quota error handling
- 🎨 Streamlit-based user interface


---


## 🧠 RAG Workflow


```text
PDF Upload
    ↓
PDF Text Extraction
    ↓
Document Chunking
    ↓
Gemini Embeddings
    ↓
Chroma Vector Database
    ↓
User Question
    ↓
Semantic Similarity Search
    ↓
Relevant Document Chunks
    ↓
Google Gemini
    ↓
AI Generated Answer
🛠️ Technologies Used
Python
Streamlit
LangChain
LangChain Google GenAI
Google Gemini
ChromaDB
PyPDF
Python-dotenv
📁 Project Structure
AI-KNOWLEDGE-ASSISTANT/
│
├── app.py
├── document_loader.py
├── rag_pipeline.py
├── vector_store.py
├── test_rag.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── documents/
│   └── Uploaded PDF files
│
├── data/
│   └── Chroma vector database
│
└── chat_history.json
⚙️ How to Run Locally
1. Clone the repository
git clone https://github.com/Tanmay1444/AI-KNOWLEDGE-ASSISTANT.git
2. Navigate to the project
cd AI-KNOWLEDGE-ASSISTANT
3. Create a virtual environment
python -m venv venv
4. Activate the virtual environment
Windows
venv\Scripts\activate
5. Install dependencies
pip install -r requirements.txt
6. Create .env

Create a .env file in the project root:

GOOGLE_API_KEY=your_google_gemini_api_key
7. Run the application
streamlit run app.py

The application will open in your browser.

🔐 Environment Variables

The application requires a Google Gemini API key.

GOOGLE_API_KEY=your_api_key

Do not commit the .env file to GitHub.

🔎 Example Questions

After uploading a PDF, users can ask questions such as:

What are the advantages of AI in the IT industry?


What are the main challenges discussed in the document?


Summarize the key findings.


What technologies are mentioned in the document?
💡 How It Works
1. Document Loading

The application reads uploaded PDF files using PyPDF and extracts their text.

2. Text Chunking

Large documents are divided into smaller chunks to improve retrieval accuracy.

3. Embeddings

Each chunk is converted into a numerical vector using the Google Gemini embedding model.

4. Vector Storage

The generated embeddings are stored in ChromaDB.

5. Semantic Search

When a user asks a question, the system searches the vector database for the most relevant document chunks.

6. Answer Generation

The retrieved context is passed to Google Gemini, which generates an answer based on the available document information.

🧪 Testing

The project includes:

test_rag.py

This file can be used to test the RAG pipeline and document retrieval functionality.

🔒 Security

The following files and folders are excluded from Git tracking:

.env
venv/
data/
chat_history.json
documents/*.pdf
__pycache__/

This prevents API keys, local databases, uploaded documents, and temporary files from being pushed to GitHub.

🚧 Future Improvements
Multi-document conversational RAG
Better conversation-aware retrieval
Source citations with page numbers
Reranking for improved retrieval accuracy
Streaming AI responses
Authentication and user accounts
Cloud vector database integration
Production deployment
Advanced RAG evaluation
Support for additional document formats
👨‍💻 Author

Tanmay More

GitHub:
https://github.com/Tanmay1444