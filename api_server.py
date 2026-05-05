# api_server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import fetch_all_feedback, get_feedback_count
from insight_aggregator import (
    get_sentiment_distribution,
    get_top_issues,
    get_emotion_distribution,
    get_sentiment_trend,
    get_executive_summary
)

app = FastAPI(title="NeferSurvey API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return "ok"


@app.get("/sentiment-distribution")
def sentiment_distribution():
    feedback = fetch_all_feedback()
    dist     = get_sentiment_distribution(feedback)
    return [{"sentiment": k, "percentage": v} for k, v in dist.items()]


@app.get("/top-issues")
def top_issues():
    feedback = fetch_all_feedback()
    issues   = get_top_issues(feedback, top_n=10)
    return [{"issue": issue, "count": count} for issue, count in issues]


@app.get("/emotion-distribution")
def emotion_distribution():
    feedback = fetch_all_feedback()
    emotions = get_emotion_distribution(feedback)
    return [{"emotion": k, "count": v} for k, v in emotions.items()]


@app.get("/sentiment-trend")
def sentiment_trend():
    feedback = fetch_all_feedback()
    trend    = get_sentiment_trend(feedback)
    rows     = []
    for entry in trend:
        date = entry["date"]
        for sentiment in ["Positive", "Negative", "Neutral", "Mixed"]:
            rows.append({
                "date":      date,
                "sentiment": sentiment,
                "count":     entry.get(sentiment, 0)
            })
    return rows


@app.get("/total-feedback")
def total_feedback():
    return [{"value": get_feedback_count()}]


@app.get("/dominant-sentiment")
def dominant_sentiment():
    feedback = fetch_all_feedback()
    dist     = get_sentiment_distribution(feedback)
    dominant = max(dist, key=dist.get) if dist else "N/A"
    return [{"value": dominant}]


@app.get("/top-emotion")
def top_emotion():
    feedback = fetch_all_feedback()
    emotions = get_emotion_distribution(feedback)
    top      = max(emotions, key=emotions.get) if emotions else "N/A"
    return [{"value": top}]


@app.get("/urgency")
def urgency():
    feedback = fetch_all_feedback()
    counts   = {"High": 0, "Medium": 0, "Low": 0}
    for f in feedback:
        text = (f.get("key_issue") or "").lower()
        if any(w in text for w in ["urgent", "broken", "worst", "terrible", "immediately", "scam"]):
            counts["High"] += 1
        elif any(w in text for w in ["slow", "late", "issue", "problem", "confusing", "damaged"]):
            counts["Medium"] += 1
        else:
            counts["Low"] += 1
    return [{"level": k, "count": v} for k, v in counts.items()]


@app.get("/summary")
def summary():
    feedback = fetch_all_feedback()
    s        = get_executive_summary(feedback)
    return {
        "total_feedback"    : s.get("total_feedback", 0),
        "dominant_sentiment": s.get("dominant_sentiment", "N/A"),
        "top_emotion"       : s.get("top_emotion", "N/A"),
        "top_issues"        : [
            {"issue": i[0], "count": i[1]}
            for i in s.get("top_3_issues", [])
        ]
    }


@app.get("/feedback")
def all_feedback():
    feedback = fetch_all_feedback()
    return [
        {
            "id"       : f["id"],
            "text"     : f["text"][:100] + "..." if len(f["text"]) > 100 else f["text"],
            "sentiment": f["sentiment"],
            "emotion"  : f["emotion"],
            "key_issue": f["key_issue"],
            "timestamp": f["timestamp"]
        }
        for f in feedback
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
