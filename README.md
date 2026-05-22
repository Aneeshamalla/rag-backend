# RAG Backend Project (FastAPI + Redis + Pinecone)

## Overview
This project is a Retrieval-Augmented Generation (RAG) backend system built using FastAPI. It allows users to upload documents, query them using LLMs, and also supports interview booking functionality.

---

## Features

### 1. Document Ingestion API
- Upload PDF/TXT files
- Extract text from documents
- Chunking strategies:
  - Fixed chunking
  - Sentence-based chunking
- Generate embeddings using SentenceTransformer
- Store embeddings in Pinecone vector database
- Store metadata in SQLite

---

### 2. Conversational RAG API
- Uses Pinecone for semantic search
- Redis for chat memory (multi-turn conversations)
- Groq / LLM for response generation
- Context-aware answers based on uploaded documents

---

### 3. Interview Booking System
- Extracts booking details from user input
- Stores:
  - Name
  - Email
  - Date
  - Time
- Saves data in SQLite database

---

## Tech Stack
- FastAPI
- Python
- Pinecone
- Redis
- SentenceTransformers
- SQLite
- Docker
- Docker Compose

---

## How to Run

### Using Docker (Recommended)

```bash
docker-compose up --build

## API Testing

After running the project, open Swagger UI:

http://localhost:8000/docs