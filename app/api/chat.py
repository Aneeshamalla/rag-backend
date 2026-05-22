from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.memory import get_history, add_to_history, clear_history
from app.rag import retrieve_chunks, build_prompt
from app.llm import call_llm
from app.booking import handle_booking, init_bookings_table

router = APIRouter(prefix="/chat", tags=["Chat"])
init_bookings_table()   # creates bookings table on startup if not exists

@router.delete("/{session_id}")
def delete_chat_history(session_id: str):
    """Manually clear Redis chat history for a given session."""
    clear_history(session_id)
    return {"message": f"Chat history for session '{session_id}' has been cleared."}

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id
    question = request.question

    # 1. Load conversation history from Redis
    history = get_history(session_id)

    # 2. Retrieve relevant chunks from Pinecone
    chunks = retrieve_chunks(question, top_k=request.top_k)
    seen: set[str] = set()
    sources = [c["filename"] for c in chunks if not (c["filename"] in seen or seen.add(c["filename"]))]

    # 3. Build prompt and get LLM answer
    messages = build_prompt(question, chunks, history)
    answer = call_llm(messages)

    # 4. Handle booking — must run BEFORE saving to history
    booking_result = handle_booking(session_id, question)

    # 5. If booking succeeded, replace LLM answer with clean backend confirmation
    if booking_result:
        answer = (
            f"Your interview has been booked!\n\n"
            f"- Name: {booking_result['name']}\n"
            f"- Email: {booking_result['email']}\n"
            f"- Date: {booking_result['date']}\n"
            f"- Time: {booking_result['time']}\n\n"
            f"A confirmation will be sent to {booking_result['email']}."
        )

    # 6. Save final answer to Redis 
    add_to_history(session_id, "user", question)
    add_to_history(session_id, "assistant", answer)

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        sources=sources,
        booking=booking_result,
    )