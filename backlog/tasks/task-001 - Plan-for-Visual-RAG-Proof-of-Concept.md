---
id: task-001
title: Plan for Visual RAG Proof of Concept
status: In Progress
assignee: []
created_date: '2026-01-29 09:48'
labels: []
dependencies: []
priority: high
---

## Description

**Epic**
Create a Python-based Proof of Concept (PoC) that indexes PDF documents using ColPali (Contextualized Late Interaction Over PaliGemma) and stores/retrieves them using Milvus as the vector database.

Context & Constraints: Use the following architectural specifications derived from the research papers and tutorials provided:
1. Environment and Libraries
• ColPali Wrapper: 
    - Do a web search to check the best ColPali wrapper.
    - The paper/references suggest using the byaldi library or colpali_engine to load the model. 
• Milvus SDK: 
    - Deploy Milvus in a docker container    
    - Use pymilvus to connect to a standalone Milvus instance (or Zilliz Cloud).
• Hardware: 
    - I use a Macmini m4 with metal 

2. Data Ingestion (The "Vision RAG" Pipeline)
• Input: Raw PDF documents.
• Preprocessing: Do not use OCR or text chunking. Convert each PDF page directly into an image.
• Encoder:
    ◦ Pass the page images to the ColPali model.
    ◦ Output format: The model outputs a Multi-Vector Representation. It treats the image as a 32x32 grid, resulting in 1,024 image patches per page.
    ◦ Dimensionality: Each patch is projected to a 128-dimensional vector.
    ◦ Total Output: A tensor of shape [N_pages, 1024, 128].
3. Milvus Schema & Storage Strategy (Crucial Step)
• Challenge: ColPali requires storing a "bag of vectors" for a single document ID (Late Interaction), which standard dense retrieval schemas do not support efficiently.
• Required Workaround for Milvus: Implement a schema where each image patch is stored as a separate vector, but linked to a parent Document/Page ID.
    ◦ Schema Fields:
        ▪ patch_id (Primary Key).
        ▪ doc_id (Int/String): ID of the PDF.
        ▪ page_number (Int).
        ▪ embedding (FloatVector, Dim=128).
    ◦ Insertion Logic: Flatten the ColPali output. For a single page, insert 1,024 distinct rows into Milvus, all sharing the same doc_id and page_number.
    ◦ Optimization Note: The sources mention Binary Quantization (BQ) can speed up search by 2x and reduce storage. If Milvus supports BQ for float vectors, enable it.
4. Retrieval Logic (Late Interaction / MaxSim)
• Query Encoding: Encode the user's text query using the ColPali processor. This will produce a list of vectors for the query tokens (Tensor shape: [N_query_tokens, 128]).
• Search & Scoring:
    ◦ Since Milvus may not support a server-side "MaxSim" operator:
        1. Perform a search for each query token vector against the database to retrieve candidate patches.
        2. Client-Side Re-ranking: Implement the MaxSim (Maximum Similarity) operation in Python using torch or numpy.
    ◦ MaxSim Formula: For each query token, find the maximum dot-product score against the retrieved document patches, then sum these maximums to get the final score for the page.
    ◦ Note: In the sources, Qdrant handles this via "multivector config." Check if for Milvus, you must code this logic manually in the retrieval function.
5. Generation (VLM)
• Once the top-k pages (images) are identified via Milvus retrieval:
    ◦ Load the corresponding Base64 image of the page.
    ◦ Pass the image + original text query to a generative Vision Language Model (e.g., Qwen2-VL, or another newer and more efficient Qwen model like Qwen3) to synthesize the answer.
    ◦ The Qwen Model needs to be locally deployed on MacOS (use either ollama or other software).

Deliverables
1. ingest.py: A script that reads a PDF, converts pages to images, generates ColPali embeddings (1024 vectors per page), and upserts them into Milvus.
2. search.py: A script that encodes a query, retrieves patch vectors from Milvus, performs the MaxSim calculation to rank pages, and prints the top results.
3. generation.py (Optional): Connects the retrieved image to a VLM (like Qwen2-VL locally) to answer the user's question.

**Tasks**
- Breakdown the acceptance criteria and epic into tasks. 

## Description

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Pdfs are converted to images
- [ ] #2 Images are converted using ColPali into multi-vectors
- [ ] #3 Save vectors in milvus with correct schema
- [ ] #4 Retrieval is tested and works
- [ ] #5 A visual Qwen model is locally deployed
- [ ] #6 Breakdown acceptance criteria into tasks
<!-- AC:END -->
