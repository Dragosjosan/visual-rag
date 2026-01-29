---
id: task-003
title: PDF Processing Service
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-2, ingestion]
dependencies: [task-002]
priority: high
---

## Description

Implement the PDF to image conversion service that converts each PDF page into a PIL Image for subsequent embedding generation.

**Scope:**
1. Implement `app/services/pdf_processor.py` with:
   - `convert_pdf_to_images()` - Convert PDF to list of (page_number, PIL.Image) tuples
   - `generate_doc_id()` - Generate deterministic doc_id from file content hash (SHA256)
   - Configurable DPI (default 144)
   - Multi-threaded conversion for performance
2. Create utility functions in `app/utils/image_utils.py`:
   - Image to base64 encoding
   - Image resizing helpers

**Technical Details:**
- Use `pdf2image` library with `convert_from_path()`
- Page numbers are 1-indexed
- Output format: RGB images
- DPI: 144 (balance between quality and speed)

**Key Files to Create:**
- `app/services/__init__.py`
- `app/services/pdf_processor.py`
- `app/utils/__init__.py`
- `app/utils/image_utils.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PDF processor converts multi-page PDFs to images
- [ ] #2 Page numbers are correctly 1-indexed
- [ ] #3 doc_id generation is deterministic (same file = same ID)
- [ ] #4 Test with ColPali paper PDF produces 26 images (assuming 26 pages)
- [ ] #5 Images are RGB format suitable for ColQwen2
<!-- AC:END -->
