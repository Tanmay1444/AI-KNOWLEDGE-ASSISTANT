from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = []

    for document in documents:
        text_chunks = splitter.split_text(document["text"])

        for chunk in text_chunks:
            chunks.append({
                "text": chunk,
                "source": document["source"]
            })

    return chunks


def generate_answer(query, results):
    context = "\n\n".join(
        result.page_content for result in results
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0
    )

    prompt = f"""
You are an AI Knowledge Assistant.

Answer the user's question using ONLY the information provided
in the context below.

If the answer is not available in the context, say:
"I could not find this information in the uploaded documents."

Context:
{context}

Question:
{query}

Answer clearly and concisely:
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        for item in response.content:
            if isinstance(item, dict) and item.get("type") == "text":
                return item.get("text", "")
    else:
        return response.content