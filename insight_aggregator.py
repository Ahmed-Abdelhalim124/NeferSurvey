# insight_aggregator.py
from collections import Counter
from datetime import datetime
from database import fetch_all_feedback


def get_sentiment_distribution(feedback_list: list) -> dict:
    if not feedback_list:
        return {}
    sentiments = [f["sentiment"] for f in feedback_list if f["sentiment"]]
    total      = len(sentiments)
    counts     = Counter(sentiments)
    return {label: round((count / total) * 100, 1) for label, count in counts.items()}


def get_top_issues(feedback_list: list, top_n: int = 5) -> list:
    if not feedback_list:
        return []
    issues = [f["key_issue"] for f in feedback_list if f["key_issue"]]
    return Counter(issues).most_common(top_n)


def get_emotion_distribution(feedback_list: list) -> dict:
    if not feedback_list:
        return {}
    emotions = [f["emotion"] for f in feedback_list if f["emotion"]]
    return dict(Counter(emotions))


def get_sentiment_trend(feedback_list: list) -> list:
    if not feedback_list:
        return []
    from collections import defaultdict
    daily = defaultdict(lambda: Counter())
    for f in feedback_list:
        if not f["timestamp"] or not f["sentiment"]:
            continue
        try:
            date = datetime.fromisoformat(f["timestamp"]).strftime("%Y-%m-%d")
            daily[date][f["sentiment"]] += 1
        except Exception:
            continue
    trend = []
    for date in sorted(daily.keys()):
        entry = {"date": date}
        entry.update(daily[date])
        trend.append(entry)
    return trend


def get_executive_summary(feedback_list: list) -> dict:
    if not feedback_list:
        return {"total": 0, "message": "No feedback submitted yet."}
    total      = len(feedback_list)
    sentiment  = get_sentiment_distribution(feedback_list)
    top_issues = get_top_issues(feedback_list, top_n=3)
    emotions   = get_emotion_distribution(feedback_list)
    dominant   = max(sentiment, key=sentiment.get) if sentiment else "N/A"
    top_emotion= max(emotions,  key=emotions.get)  if emotions  else "N/A"
    return {
        "total_feedback"    : total,
        "dominant_sentiment": dominant,
        "top_emotion"       : top_emotion,
        "sentiment_split"   : sentiment,
        "top_3_issues"      : top_issues,
    }
