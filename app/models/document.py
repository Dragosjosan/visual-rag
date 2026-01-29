from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    doc_id: str = Field(description="SHA256 hash of the document")
    doc_name: str = Field(description="Document name (filename without extension)")
    page_count: int = Field(description="Number of pages in the document")
    pdf_path: str = Field(description="Path to saved PDF")


class DocumentInfo(BaseModel):
    doc_id: str
    doc_name: str
    page_count: int


class IngestionResponse(BaseModel):
    doc_id: str = Field(description="Document identifier (SHA256 hash or custom)")
    pages_indexed: int = Field(description="Number of pages processed")
    patches_stored: int = Field(description="Total embedding patches stored in Milvus")
    status: str = Field(description="Ingestion status: completed or failed")


def validate_filename(filename: str) -> str:
    if not filename:
        raise ValueError("Filename cannot be empty")

    if not filename.endswith(".pdf"):
        raise ValueError("Only PDF files are supported")

    if len(filename) > 50:
        raise ValueError("Filename too long (max 50 characters)")

    invalid_chars = set('<>:"/\\|?*')
    if any(char in filename for char in invalid_chars):
        raise ValueError(f"Filename contains invalid characters: {invalid_chars}")

    return filename
