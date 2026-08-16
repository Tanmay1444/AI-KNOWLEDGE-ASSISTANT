import os
import hashlib

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()


# --------------------------------------------------
# VECTOR DATABASE PATH
# --------------------------------------------------

VECTOR_DB_PATH = "data"


# --------------------------------------------------
# CREATE EMBEDDINGS
# --------------------------------------------------

def create_embeddings():

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    return embeddings


# --------------------------------------------------
# CREATE / LOAD VECTOR STORE
# --------------------------------------------------

def create_vector_store(chunks, embeddings):

    documents = []

    ids = []

    for index, chunk in enumerate(chunks):

        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "source": chunk["source"]
                }
            )
        )

        chunk_id = hashlib.md5(
            f"{chunk['source']}_{index}_{chunk['text']}".encode(
                "utf-8"
            )
        ).hexdigest()

        ids.append(chunk_id)


    # ----------------------------------------------
    # CREATE NEW DATABASE IF DATA DOES NOT EXIST
    # ----------------------------------------------

    if not os.path.exists(VECTOR_DB_PATH):

        vector_db = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            ids=ids,
            persist_directory=VECTOR_DB_PATH
        )

        return vector_db


    # ----------------------------------------------
    # LOAD EXISTING DATABASE
    # ----------------------------------------------

    vector_db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )


    # ----------------------------------------------
    # CHECK EXISTING SOURCES
    # ----------------------------------------------

    existing_data = vector_db.get()

    existing_sources = set()

    for metadata in existing_data.get(
        "metadatas",
        []
    ):

        if metadata and "source" in metadata:

            existing_sources.add(
                metadata["source"]
            )


    # ----------------------------------------------
    # ADD ONLY NEW DOCUMENTS
    # ----------------------------------------------

    new_documents = []
    new_ids = []

    for document, chunk_id in zip(
        documents,
        ids
    ):

        source = document.metadata.get(
            "source"
        )

        if source not in existing_sources:

            new_documents.append(
                document
            )

            new_ids.append(
                chunk_id
            )


    if new_documents:

        vector_db.add_documents(
            documents=new_documents,
            ids=new_ids
        )


    return vector_db


# --------------------------------------------------
# DELETE DOCUMENT VECTORS BY SOURCE
# --------------------------------------------------

def delete_document_vectors(
    vector_db,
    source
):

    try:

        existing = vector_db.get(
            where={"source": source}
        )

        ids = existing.get(
            "ids",
            []
        )

        if ids:

            vector_db.delete(
                ids=ids
            )

        return True

    except Exception as e:

        print(
            "Error deleting document vectors:",
            e
        )

        return False


# --------------------------------------------------
# SEARCH DOCUMENTS
# --------------------------------------------------

def search_documents(
    vector_db,
    query,
    k=5
):

    results = vector_db.similarity_search(
        query,
        k=k
    )

    return results