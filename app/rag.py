from app.utils import get_embedding
from app.core.pinecone_client import index


def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:  ## SEARCH SIMILAR CHUNKS
    """
    Embed the query and find the top_k most similar chunks in Pinecone.
    """
    embedding = get_embedding(query) ## text to vectors converted

    result = index.query(  ## send to pinecone/ vector similarity search
        vector=embedding,    #sends user qsnvector to pinecone
        top_k=top_k,  #Return the top most similar chunks
        include_metadata=True  #Also return extra information stored with each chunk
    )

    return [
        {
            "text": match.metadata.get("text", ""),
            "filename": match.metadata.get("filename", "unknown"),
            "score": round(match.score, 4),
        }
        for match in result.matches
    ]


def build_prompt(
    question: str,
    context_chunks: list[dict],
    history: list[dict],
) -> list[dict]:
    """
    Build the full message list:
    [system_message, history, user_message_with_context]
    """

    system_msg = (
    "You are a helpful assistant. Answer the user's question using the provided document context. "
    "If the answer is not in the document context, check the conversation history above — "
    "if the answer is there, use it to respond. "
    "Only say 'I don't have enough information in the uploaded documents to answer that.' "
    "if NEITHER the document context NOR the conversation history contains the answer. "
    "STRICT RULES: "
    "Do NOT generate booking confirmations. "
    "Do NOT say phrases like 'I have extracted', 'To confirm', "
    "'Your interview is booked', or 'booking confirmed'. "
    "Do NOT acknowledge or respond to interview scheduling requests. "
    "Booking is handled entirely by the backend — stay silent on it."
)


    if not context_chunks:
        context_text = (                ## if no document found then tell AI "no info available"
            "No relevant documents were found in the uploaded knowledge base for this query."
        )
    else:
        context_text = "\n\n".join(       ##if document found, then convert them into readable text 
            f"[Document: {c['filename']}]\n{c['text']}"
            for c in context_chunks
        )

    messages: list[dict] = [{"role": "system", "content": system_msg}]   ## Then start preparing AI input, with system instructions

    # inject chat history (Redis memory)
    messages.extend(history)

    # user query + retrieved context
    messages.append({
        "role": "user",
        "content": f"Context from uploaded documents:\n{context_text}\n\nQuestion: {question}",
    })

    return messages