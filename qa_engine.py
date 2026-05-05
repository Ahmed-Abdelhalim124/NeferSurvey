# qa_engine.py
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, TOP_K_RESULTS
from embedding_engine import get_embedding, build_faiss_index, retrieve_top_k

client = Groq(api_key=GROQ_API_KEY)


def build_qa_prompt(question: str, context_entries: list) -> str:
    if not context_entries:
        return ""
    context_block = "\n\n".join([
        f"[Feedback ID {entry['id']}]: {entry['text']}"
        for entry in context_entries
    ])
    return f"""
You are a customer feedback analyst assistant.
Answer the question EXCLUSIVELY based on the feedback excerpts provided below.
Do NOT use any outside knowledge. Do NOT hallucinate or invent information.
Always reference the exact Feedback ID numbers when citing evidence.
If the answer cannot be found in the provided feedback, respond with:
"I could not find relevant information in the submitted feedback."

--- CUSTOMER FEEDBACK EXCERPTS ---
{context_block}
--- END OF FEEDBACK ---

Question: {question}

Answer (always cite exact Feedback ID numbers as evidence):
"""


def answer_question(question: str) -> dict:
    index, records = build_faiss_index()

    if not index or not records:
        return {
            "answer" : "No feedback data available yet. Please submit feedback first.",
            "sources": []
        }

    top_entries = retrieve_top_k(question, index, records, k=TOP_K_RESULTS)

    if not top_entries:
        return {
            "answer" : "No relevant feedback found for your question.",
            "sources": []
        }

    prompt = build_qa_prompt(question, top_entries)

    try:
        response = client.chat.completions.create(
            model    = GROQ_MODEL,
            messages = [
                {
                    "role":    "system",
                    "content": (
                        "You are a strict customer feedback analyst. "
                        "Only answer based on provided feedback excerpts. "
                        "Always cite exact Feedback IDs as evidence. "
                        "Never use external knowledge or make assumptions."
                    )
                },
                {
                    "role":    "user",
                    "content": prompt
                }
            ],
            temperature = 0.1,
            max_tokens  = 500,
        )
        answer = response.choices[0].message.content.strip()

    except Exception as e:
        answer = f"❌ Error generating answer: {e}"

    return {
        "answer" : answer,
        "sources": [
            {
                "id"   : e["id"],
                "text" : e["text"][:120] + "...",
                "score": round(e["score"], 3)
            }
            for e in top_entries
        ]
    }
