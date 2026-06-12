
from pypdf import PdfReader
from pathlib import Path
import fitz
from PIL import Image
import pytesseract
import io
from langchain_core.documents import Document




def ingest_pdf_directory(directory_path: str) -> list[Document]:
    documents = []
    path = Path(directory_path)

    # Track counts for production monitoring
    success_count = 0
    error_count = 0

    for pdf_path in path.glob("**/*.pdf"):
        try:
            reader = PdfReader(pdf_path)
            file_text_extracted = False

            for page_num, page in enumerate(reader.pages):
                # 'plain' layout mode preserves structural text placement
                # similar to how LangChain's internal hooks handle it
                text = page.extract_text(extraction_mode="plain")

                # If plain mode yields nothing, try layout mode as a fallback
                if not text or not text.strip():
                    text = page.extract_text(extraction_mode="layout")

                # Fallback to absolute raw extraction if layout fails
                if not text or not text.strip():
                    text = page.extract_text()

                if text:  # Take whatever text we successfully found
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": str(pdf_path),
                            "file_name": pdf_path.name,
                            "page": page_num + 1
                        }
                    )
                    documents.append(doc)
                    file_text_extracted = True

            if file_text_extracted:
                success_count += 1
            else:
                print(  # This alerts you if a file was read but resulted in 0 text strings
                    f"⚠️ Warning: Loaded '{pdf_path.name}' but extracted 0 characters. Might be scanned/image-only."
                )

        except Exception as e:
            error_count += 1
            print(f"❌ Error processing {pdf_path.name}: {e}")
            continue

    print(f"\n--- Ingestion Summary: Successfully parsed {success_count} PDFs. Failed on {error_count} PDFs. ---")
    return documents

# def ingest_pdf_directory_pymupdf(directory_path: str) -> list[Document]:
#     documents = []
#     path = Path(directory_path)
#
#     success_count = 0
#
#     # Iterate through all PDFS in the data folder or in the company repository.
#     for pdf_path in path.glob("**/*.pdf"):
#         try:
#             # open the document with PYMUPDF (highly resilient for complex layouts)
#             doc_object = fitz.open(pdf_path)
#             file_has_text = False
#
#             for page_num, page in enumerate(doc_object):
#                 # "blocks"-> text extraction preserves column reading orders automatically
#                 text = page.get_text("text")
#
#                 # fallback for production grade -> grab whatever layout strings present
#                 if not text.strip():
#                     text = page.get_text("block")
#
#                     # if it is a structured image page, we still keep this object
#                     # with a place holder or layout tag for the metadata index
#                     if isinstance(text, list):
#                         text = "\n".join([b[4] for b in text if isinstance(b, tuple) and len(b) > 4])
#
#                 doc = Document(
#                     page_content= text if text.strip() else f"[Image page/ Graphic Conent]",
#                     metadata={
#                         "source": str(pdf_path),
#                         "file_name": pdf_path.name,
#                         "page": page_num + 1,
#                         "total_pages": len(doc_object)
#                     }
#                 )
#                 documents.append(doc)
#                 file_has_text = True
#
#             if file_has_text:
#                 print(f"✅ Successfully ingested: {pdf_path.name} ({len(doc_object)} pages)")
#         except Exception as e:
#             print(f"❌ Error processing {pdf_path.name}: {e}")
#             continue
#
#     print(f"\n--- Processed {success_count} health knowledge assets ---")
#     return documents

def extract_text_pymupdf(page: fitz.Page) -> str:
    """Fast path: extract digital text."""
    return page.get_text("text").strip()

def extract_text_blocks(page: fitz.Page) -> str:
    """Structured fallback for columns/tables."""
    blocks = page.get_text("blocks")

    if not blocks:
        return ""

    text = "\n".join(
        b[4] for b in blocks
        if isinstance(b, (list, tuple)) and len(b) > 4 and b[4]
    )

    return text.strip()

def extract_text_ocr(page: fitz.Page, dpi: int = 300) -> str:
    """
    OCR fallback for scanned/image-based PDFs.
    Enterprise-safe: only used when no digital text exists.
    """

    pix = page.get_pixmap(dpi=dpi)
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    # OCR config tuned for document-style PDFs
    config = "--psm 6"

    text = pytesseract.image_to_string(img, config=config)

    return text.strip()

def extract_page_text(page: fitz.Page) -> str:
    """
    Multi-layer extraction strategy:
    1. Digital text
    2. Layout blocks
    3. OCR fallback
    """

    # 1. Fast path
    text = extract_text_pymupdf(page)
    if text:
        return text

    # 2. Layout-aware fallback
    text = extract_text_blocks(page)
    if text:
        return text

    # 3. OCR fallback (expensive → last resort)
    return extract_text_ocr(page)

def ingest_pdf_directory_pymupdf(directory_path: str) -> list[Document]:
    """
    Enterprise-grade PDF ingestion:
    - PyMuPDF extraction
    - OCR fallback for scanned docs
    - Page-level metadata
    """

    base_path = Path(directory_path)
    documents: list[Document] = []

    processed_files = 0
    failed_files = 0
    ocr_pages = 0

    pdf_files = list(base_path.glob("**/*.pdf"))

    for pdf_path in pdf_files:
        try:
            with fitz.open(pdf_path) as doc:
                total_pages = len(doc)
                file_has_content = False

                for page_num, page in enumerate(doc):
                    text = extract_page_text(page)

                    # track OCR usage (simple heuristic)
                    if text and len(text) < 50:
                        ocr_pages += 1

                    if text:
                        file_has_content = True
                    else:
                        text = "[EMPTY PAGE]"

                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": str(pdf_path),
                                "file_name": pdf_path.name,
                                "page": page_num + 1,
                                "total_pages": total_pages,
                                "ocr_used": len(text) < 50,
                            },
                        )
                    )

            if file_has_content:
                processed_files += 1
                print(f"✅ Ingested: {pdf_path.name} ({total_pages} pages)")
            else:
                print(f"⚠️ Empty/Unreadable: {pdf_path.name}")

        except Exception as e:
            failed_files += 1
            print(f"❌ Failed: {pdf_path.name} | {e}")

    print(
        "\n--- Enterprise Ingestion Summary ---\n"
        f"Processed files: {processed_files}\n"
        f"Failed files: {failed_files}\n"
        f"OCR pages triggered: {ocr_pages}\n"
        f"Total documents: {len(documents)}"
    )

    return documents