from pathlib import Path
from pypdf import PdfReader


def load_documents(folder_path="documents"):
    documents = []

    folder = Path(folder_path)

    print("Documents folder:", folder.resolve())

    pdf_files = list(folder.glob("*.pdf"))

    print("PDF files found:")

    for file_path in pdf_files:
        print(" -", file_path.name)

        reader = PdfReader(str(file_path))

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        if text.strip():
            documents.append({
                "source": file_path.name,
                "text": text
            })

    print("Total documents loaded:", len(documents))

    return documents