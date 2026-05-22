from app.utils import get_embedding
from app.core.pinecone_client import index


def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:
    """
    Embed the query and find the top_k most similar chunks in Pinecone.
    """
    embedding = get_embedding(query)

    result = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
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
        context_text = (
            "No relevant documents were found in the uploaded knowledge base for this query."
        )
    else:
        context_text = "\n\n".join(
            f"[Document: {c['filename']}]\n{c['text']}"
            for c in context_chunks
        )

    messages: list[dict] = [{"role": "system", "content": system_msg}]

    # inject chat history (Redis memory)
    messages.extend(history)

    # user query + retrieved context
    messages.append({
        "role": "user",
        "content": f"Context from uploaded documents:\n{context_text}\n\nQuestion: {question}",
    })

    return messages