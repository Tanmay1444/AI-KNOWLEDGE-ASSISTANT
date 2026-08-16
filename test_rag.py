from document_loader import load_documents
from rag_pipeline import split_documents, generate_answer
from vector_store import create_embeddings, create_vector_store, search_documents


documents = load_documents("documents")

print("Documents loaded:", len(documents))

chunks = split_documents(documents)

print("Chunks created:", len(chunks))

embeddings = create_embeddings()

vector_db = create_vector_store(chunks, embeddings)

print("Vector database created successfully!")


query = input("\nAsk a question about the document: ")

results = search_documents(vector_db, query)

print("\nRelevant Information:\n")

for index, result in enumerate(results, start=1):
    print(f"Result {index}")
    print("Source:", result.metadata["source"])
    print(result.page_content)
    print("-" * 60)
answer = generate_answer(query, results)

print("\n" + "=" * 50)
print("AI ANSWER")
print("=" * 50)
print()
print(answer)

print("\n" + "=" * 50)
print("SOURCE DOCUMENTS")
print("=" * 50)

sources = []

for result in results:
    source = result.metadata.get("source", "Unknown")

    if source not in sources:
        sources.append(source)

for index, source in enumerate(sources, start=1):
    print(f"[{index}] {source}")

print("=" * 50)