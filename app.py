import streamlit as st
import os
import json
import hashlib

from document_loader import load_documents
from rag_pipeline import split_documents, generate_answer
from vector_store import (
    create_embeddings,
    create_vector_store,
    search_documents,
    delete_document_vectors
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM UI STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>

    .user-message {
        background-color: #e8f0fe;
        padding: 15px;
        border-radius: 12px;
        margin: 8px 0;
    }

    .ai-message {
        background-color: #f1f3f4;
        padding: 15px;
        border-radius: 12px;
        margin: 8px 0;
    }

    .source-box {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border-left: 4px solid #4f8bf9;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# CHAT HISTORY FILE
# --------------------------------------------------

CHAT_HISTORY_FILE = "chat_history.json"


# --------------------------------------------------
# LOAD CHAT HISTORY
# --------------------------------------------------

def load_chat_history():

    if os.path.exists(CHAT_HISTORY_FILE):

        try:

            with open(
                CHAT_HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                history = json.load(file)

                if isinstance(history, list):
                    return history

                return []

        except Exception:

            return []

    return []


# --------------------------------------------------
# SAVE CHAT HISTORY
# --------------------------------------------------

def save_chat_history(history):

    try:

        with open(
            CHAT_HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception:

        return False


# --------------------------------------------------
# SESSION STATE - CHAT HISTORY
# --------------------------------------------------

if "chat_history" not in st.session_state:

    st.session_state.chat_history = (
        load_chat_history()
    )


# --------------------------------------------------
# SESSION STATE - LAST UPLOAD
# --------------------------------------------------

if "last_upload_key" not in st.session_state:

    st.session_state.last_upload_key = None


# --------------------------------------------------
# CREATE DOCUMENTS FOLDER
# --------------------------------------------------

os.makedirs(
    "documents",
    exist_ok=True
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title(
    "🤖 AI Knowledge Assistant"
)

st.write(
    "Ask questions about your uploaded documents."
)


# --------------------------------------------------
# PDF UPLOAD
# --------------------------------------------------

st.subheader(
    "📤 Upload PDF"
)


uploaded_file = st.file_uploader(
    "Choose a PDF document",
    type=["pdf"]
)


# --------------------------------------------------
# HANDLE PDF UPLOAD
# --------------------------------------------------

if uploaded_file is not None:

    file_path = os.path.join(
        "documents",
        uploaded_file.name
    )

    # ----------------------------------------------
    # CREATE FILE HASH
    # ----------------------------------------------

    file_bytes = uploaded_file.getvalue()

    file_hash = hashlib.sha256(
        file_bytes
    ).hexdigest()

    upload_key = (
        f"{uploaded_file.name}_{file_hash}"
    )

    # ----------------------------------------------
    # PROCESS ONLY NEW / UPDATED FILE
    # ----------------------------------------------

    if (
        st.session_state.last_upload_key
        != upload_key
    ):

        try:

            # ------------------------------------------
            # REPLACE EXISTING FILE AUTOMATICALLY
            # ------------------------------------------

            with open(
                file_path,
                "wb"
            ) as file:

                file.write(
                    file_bytes
                )

            # ------------------------------------------
            # SAVE CURRENT UPLOAD KEY
            # ------------------------------------------

            st.session_state.last_upload_key = (
                upload_key
            )

            # ------------------------------------------
            # CLEAR CHAT HISTORY
            # ------------------------------------------

            st.session_state.chat_history = []

            save_chat_history([])

            # ------------------------------------------
            # CLEAR KNOWLEDGE BASE CACHE
            # ------------------------------------------

            st.cache_resource.clear()

            st.success(
                f"✅ {uploaded_file.name} "
                "uploaded successfully!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"❌ Failed to upload PDF: {e}"
            )


# --------------------------------------------------
# BUILD KNOWLEDGE BASE
# --------------------------------------------------

@st.cache_resource
def build_knowledge_base():

    documents = load_documents(
        "documents"
    )

    # ----------------------------------------------
    # NO DOCUMENTS
    # ----------------------------------------------

    if not documents:

        return None, 0, 0

    # ----------------------------------------------
    # SPLIT DOCUMENTS
    # ----------------------------------------------

    chunks = split_documents(
        documents
    )

    # ----------------------------------------------
    # NO READABLE TEXT
    # ----------------------------------------------

    if not chunks:

        return (
            None,
            len(documents),
            0
        )

    # ----------------------------------------------
    # CREATE EMBEDDINGS
    # ----------------------------------------------

    embeddings = create_embeddings()

    # ----------------------------------------------
    # CREATE VECTOR DATABASE
    # ----------------------------------------------

    vector_db = create_vector_store(
        chunks,
        embeddings
    )

    return (
        vector_db,
        len(documents),
        len(chunks)
    )


# --------------------------------------------------
# LOAD KNOWLEDGE BASE
# --------------------------------------------------

vector_db, document_count, chunk_count = (
    build_knowledge_base()
)


# --------------------------------------------------
# DOCUMENT INFORMATION
# --------------------------------------------------

st.info(
    f"📄 Documents: {document_count}   |   "
    f"🧩 Chunks: {chunk_count}"
)


# --------------------------------------------------
# EMPTY DOCUMENT WARNING
# --------------------------------------------------

if document_count == 0:

    st.warning(
        "📂 No PDF documents found. "
        "Please upload a PDF to start asking questions."
    )

elif chunk_count == 0:

    st.warning(
        "⚠️ The uploaded PDF does not contain "
        "readable text."
    )


# --------------------------------------------------
# UPLOADED DOCUMENTS
# --------------------------------------------------

st.subheader(
    "📚 Uploaded Documents"
)


document_files = [
    file
    for file in os.listdir("documents")
    if file.lower().endswith(".pdf")
]


if document_files:

    for file_name in document_files:

        col1, col2 = st.columns(
            [5, 1]
        )

        # ------------------------------------------
        # FILE NAME
        # ------------------------------------------

        with col1:

            st.write(
                f"📄 {file_name}"
            )

        # ------------------------------------------
        # DELETE BUTTON
        # ------------------------------------------

        with col2:

            if st.button(
                "🗑️ Delete",
                key=f"delete_{file_name}"
            ):

                file_path = os.path.join(
                    "documents",
                    file_name
                )

                try:

                    # ----------------------------------
                    # DELETE VECTORS
                    # ----------------------------------

                    if vector_db is not None:

                        try:

                            delete_success = (
                                delete_document_vectors(
                                    vector_db,
                                    file_name
                                )
                            )

                            if not delete_success:

                                st.warning(
                                    "⚠️ Could not remove "
                                    "document vectors."
                                )

                        except Exception:

                            pass

                    # ----------------------------------
                    # DELETE PDF
                    # ----------------------------------

                    if os.path.exists(file_path):

                        os.remove(
                            file_path
                        )

                    # ----------------------------------
                    # CLEAR CACHE
                    # ----------------------------------

                    st.cache_resource.clear()

                    # ----------------------------------
                    # CLEAR CHAT HISTORY
                    # ----------------------------------

                    st.session_state.chat_history = []

                    save_chat_history([])

                    # ----------------------------------
                    # RESET UPLOAD STATE
                    # ----------------------------------

                    st.session_state.last_upload_key = None

                    st.success(
                        f"✅ {file_name} "
                        "deleted successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Could not delete "
                        f"{file_name}: {e}"
                    )

else:

    st.info(
        "No PDF documents uploaded yet."
    )


# --------------------------------------------------
# QUESTION INPUT
# --------------------------------------------------

query = st.text_input(
    "Ask your question:",
    placeholder=(
        "Example: What are the advantages "
        "of AI in the IT industry?"
    )
)


# --------------------------------------------------
# ASK QUESTION
# --------------------------------------------------

if st.button(
    "Ask Question"
):

    # ----------------------------------------------
    # EMPTY QUESTION
    # ----------------------------------------------

    if not query.strip():

        st.warning(
            "⚠️ Please enter a question."
        )

    # ----------------------------------------------
    # NO VECTOR DATABASE
    # ----------------------------------------------

    elif vector_db is None:

        st.warning(
            "📂 No readable documents available. "
            "Please upload a PDF first."
        )

    else:

        with st.spinner(
            "Searching documents and generating answer..."
        ):

            try:

                # ----------------------------------
                # CREATE CONTEXTUAL QUERY
                # ----------------------------------

                contextual_query = query

                if st.session_state.chat_history:

                    previous_question = (
                        st.session_state
                        .chat_history[-1]["question"]
                    )

                    contextual_query = (
                        f"Previous question: "
                        f"{previous_question}\n"
                        f"Current question: {query}"
                    )

                # ----------------------------------
                # SEARCH DOCUMENTS
                # ----------------------------------

                results = search_documents(
                    vector_db,
                    contextual_query
                )

                # ----------------------------------
                # CHECK SEARCH RESULTS
                # ----------------------------------

                if not results:

                    st.warning(
                        "🔎 No relevant information "
                        "found in the uploaded documents."
                    )

                else:

                    # ----------------------------------
                    # GENERATE ANSWER
                    # ----------------------------------

                    answer = generate_answer(
                        contextual_query,
                        results
                    )

                    # ----------------------------------
                    # SAVE CHAT HISTORY
                    # ----------------------------------

                    chat_item = {
                        "question": query,
                        "answer": answer
                    }

                    st.session_state.chat_history.append(
                        chat_item
                    )

                    save_chat_history(
                        st.session_state.chat_history
                    )

                    # ----------------------------------
                    # DISPLAY ANSWER
                    # ----------------------------------

                    st.subheader(
                        "🤖 AI Answer"
                    )

                    st.markdown(
                        f"""
                        <div class="ai-message">
                            {answer}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # ----------------------------------
                    # SOURCE DOCUMENTS
                    # ----------------------------------

                    st.subheader(
                        "📚 Source Documents"
                    )

                    sources = []

                    for result in results:

                        source = result.metadata.get(
                            "source",
                            "Unknown"
                        )

                        if source not in sources:

                            sources.append(
                                source
                            )

                    for index, source in enumerate(
                        sources,
                        start=1
                    ):

                        st.markdown(
                            f"""
                            <div class="source-box">
                                📄 {index}. {source}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # ----------------------------------
                    # RELEVANT INFORMATION
                    # ----------------------------------

                    with st.expander(
                        "🔎 View Relevant Information"
                    ):

                        for index, result in enumerate(
                            results,
                            start=1
                        ):

                            st.markdown(
                                f"**Result {index}**"
                            )

                            st.write(
                                result.page_content
                            )

                            st.divider()

            except Exception as e:

                error_message = str(e)

                # ----------------------------------
                # GEMINI QUOTA ERROR
                # ----------------------------------

                if (
                    "RESOURCE_EXHAUSTED"
                    in error_message
                    or "429"
                    in error_message
                ):

                    st.error(
                        "⚠️ Gemini API quota exceeded. "
                        "Please try again later."
                    )

                else:

                    st.error(
                        "❌ Something went wrong "
                        "while processing your question."
                    )


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

if st.session_state.chat_history:

    st.divider()

    st.subheader(
        "💬 Chat History"
    )

    for index, chat in enumerate(
        st.session_state.chat_history,
        start=1
    ):

        # ------------------------------------------
        # USER QUESTION
        # ------------------------------------------

        st.markdown(
            f"**👤 You — Question {index}**"
        )

        st.markdown(
            f"""
            <div class="user-message">
                {chat["question"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        # ------------------------------------------
        # AI ANSWER
        # ------------------------------------------

        st.markdown(
            "**🤖 AI Assistant**"
        )

        st.markdown(
            f"""
            <div class="ai-message">
                {chat["answer"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()


# --------------------------------------------------
# CLEAR CHAT
# --------------------------------------------------

if st.session_state.chat_history:

    if st.button(
        "🗑️ Clear Chat"
    ):

        # Clear session history
        st.session_state.chat_history = []

        # Clear JSON history
        save_chat_history([])

        st.success(
            "✅ Chat history cleared."
        )

        st.rerun()