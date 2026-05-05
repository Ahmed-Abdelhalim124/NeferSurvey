# sentiment_engine.py
import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, MAX_FEEDBACK_LENGTH

client = Groq(api_key=GROQ_API_KEY)


def build_prompt(feedback_text: str) -> str:
    return f"""
You are a customer feedback analysis expert.
Analyze the following customer feedback and return ONLY a valid JSON object.
Do NOT include any explanation, markdown, or extra text outside the JSON.

Feedback:
\"\"\"{feedback_text}\"\"\"

Return this exact JSON structure:
{{
  "sentiment": "<Positive | Negative | Neutral | Mixed>",
  "emotion":   "<one of: Satisfaction, Frustration, Anger, Joy, Disappointment, Confusion, Neutral>",
  "key_issue": "<2 to 4 words max, e.g: Slow delivery, Broken product, Poor support, Fast shipping>",
  "urgency":   "<High | Medium | Low>"
}}
"""


def analyze_feedback(feedback_text: str) -> dict:
    feedback_text = feedback_text[:MAX_FEEDBACK_LENGTH]
    try:
        response = client.chat.completions.create(
            model    = GROQ_MODEL,
            messages = [
                {
                    "role":    "system",
                    "content": "You are a structured JSON output machine. You only return valid JSON and nothing else."
                },
                {
                    "role":    "user",
                    "content": build_prompt(feedback_text)
                }
            ],
            temperature = 0.2,
            max_tokens  = 300,
        )
        raw_output = response.choices[0].message.content.strip()
        if raw_output.startswith("```"):
            raw_output = raw_output.strip("```").strip("json").strip()

        result = json.loads(raw_output)

        required_keys = {"sentiment", "emotion", "key_issue", "urgency"}
        if not required_keys.issubset(result.keys()):
            raise ValueError(f"Missing keys in response: {result}")

        return result

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return _fallback_response()
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return _fallback_response()


def _fallback_response() -> dict:
    return {
        "sentiment": "Neutral",
        "emotion":   "Neutral",
        "key_issue": "Unable to analyze feedback at this time.",
        "urgency":   "Low"
    }
