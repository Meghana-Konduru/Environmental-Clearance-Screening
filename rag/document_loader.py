
from pathlib import Path
from typing import List

import pymupdf
from langchain_core.documents import Document


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGULATIONS_DIR = PROJECT_ROOT / "data" / "regulations"

MIN_NATIVE_TEXT_LENGTH = 30
OCR_LANGUAGE = "eng+hin"
OCR_DPI = 300


def identify_document_type(file_path: Path) -> str:
    """Identify the type of regulatory document from its folder."""

    parent_folder = file_path.parent.name.lower()

    if parent_folder == "amendments":
        return "amendment"

    if parent_folder == "office_memorandums":
        return "office_memorandum"

    return "notification"


def get_document_status(file_path: Path) -> str:
    """Identify whether a document is historical or awaiting verification."""

    if "WITHDRAWN" in file_path.name.upper():
        return "withdrawn_historical"

    return "pending_verification"


def extract_page_text(page):
    """
    Extract text from a PDF page.

    First attempt native PDF text extraction.
    If insufficient text is available, use OCR with English and Hindi.
    """

    native_text = page.get_text("text")

    if len(native_text.strip()) >= MIN_NATIVE_TEXT_LENGTH:
        return native_text, "native"

    try:
        ocr_textpage = page.get_textpage_ocr(
            language=OCR_LANGUAGE,
            dpi=OCR_DPI,
            full=True
        )

        ocr_text = page.get_text(
            "text",
            textpage=ocr_textpage
        )

        if ocr_text.strip():
            return ocr_text, "ocr"

        return "", "failed"

    except Exception as error:
        print(f"OCR failed on page {page.number + 1}: {error}")
        return "", "failed"


def load_pdf(file_path: Path) -> List[Document]:
    """Load a PDF and create one LangChain Document per readable page."""

    file_path = Path(file_path).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    documents = []

    document_name = file_path.name
    document_type = identify_document_type(file_path)
    applicability_status = get_document_status(file_path)

    try:
        pdf = pymupdf.open(file_path)

        for page_number, page in enumerate(pdf, start=1):

            page_text, extraction_method = extract_page_text(page)

            if not page_text.strip():
                print(
                    f"Warning: No text extracted from "
                    f"{document_name}, page {page_number}"
                )
                continue

            metadata = {
                "document_id": file_path.stem,
                "document_name": document_name,
                "document_type": document_type,
                "issuing_authority": "",
                "document_number": "",
                "issue_date": "",
                "source_url": "",
                "page_number": page_number,
                "applicability_status": applicability_status,
                "extraction_method": extraction_method,
                "source_file": str(
                    file_path.relative_to(PROJECT_ROOT)
                )
            }

            documents.append(
                Document(
                    page_content=page_text,
                    metadata=metadata
                )
            )

        pdf.close()

    except Exception as error:
        print(f"Failed to load {document_name}: {error}")
        raise

    return documents


def load_regulatory_documents(
    data_dir: Path = REGULATIONS_DIR
) -> List[Document]:
    """Load all PDF documents from the regulations directory."""

    data_dir = Path(data_dir).resolve()

    if not data_dir.exists():
        raise FileNotFoundError(
            f"Regulations directory not found: {data_dir}"
        )

    pdf_files = sorted(data_dir.rglob("*.pdf"))

    all_documents = []

    failed_files = []
    failed_pages = []

    native_count = 0
    ocr_count = 0

    print(f"\nFound {len(pdf_files)} PDF files.\n")

    for pdf_file in pdf_files:

        print(f"Processing: {pdf_file.name}")

        try:
            documents = load_pdf(pdf_file)

            for document in documents:

                all_documents.append(document)

                if document.metadata["extraction_method"] == "native":
                    native_count += 1

                elif document.metadata["extraction_method"] == "ocr":
                    ocr_count += 1

            print(f"  Extracted {len(documents)} pages.")

        except Exception as error:
            failed_files.append(pdf_file.name)
            print(f"  Failed: {error}")

    print("\n========== DOCUMENT LOADING SUMMARY ==========")
    print(f"PDF files discovered: {len(pdf_files)}")
    print(f"Readable pages: {len(all_documents)}")
    print(f"Native extraction pages: {native_count}")
    print(f"OCR extraction pages: {ocr_count}")
    print(f"Failed PDF files: {len(failed_files)}")

    if failed_files:
        print("\nFailed files:")
        for file_name in failed_files:
            print(f" - {file_name}")

    print("================================================\n")

    return all_documents


if __name__ == "__main__":

    documents = load_regulatory_documents()

    if documents:
        print("Sample extracted document:")
        print(documents[0].metadata)
        print("\nExtracted text:")
        print(documents[0].page_content[:1000])
