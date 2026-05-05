# ui.py
import gradio as gr
import pandas as pd
import time
from database import init_db, get_feedback_count
from sentiment_engine import analyze_feedback
from embedding_engine import get_embedding
from database import insert_feedback
from qa_engine import answer_question

init_db()

# ── 1. Single Feedback ────────────────────────────────────────────────────────

def handle_feedback_submission(feedback_text: str):
    if not feedback_text or len(feedback_text.strip()) < 10:
        return "⚠️ Please enter at least 10 characters of feedback."
    analysis  = analyze_feedback(feedback_text)
    embedding = get_embedding(feedback_text)
    insert_feedback(
        text      = feedback_text,
        sentiment = analysis["sentiment"],
        emotion   = analysis["emotion"],
        key_issue = analysis["key_issue"],
        embedding = embedding
    )
    count = get_feedback_count()
    return (
        f"✅ Feedback #{count} stored successfully!\n\n"
        f"📊 Sentiment : {analysis['sentiment']}\n"
        f"😐 Emotion   : {analysis['emotion']}\n"
        f"🔑 Key Issue : {analysis['key_issue']}\n"
        f"🚨 Urgency   : {analysis['urgency']}\n\n"
        f"📈 Refresh the Dashboard tab to see updates."
    )


# ── 2. Bulk Upload ────────────────────────────────────────────────────────────

def handle_file_upload(file):
    if file is None:
        return "⚠️ No file uploaded."
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file.name)
            if "feedback" in df.columns:
                feedbacks = df["feedback"].dropna().tolist()
            elif "text" in df.columns:
                feedbacks = df["text"].dropna().tolist()
            else:
                feedbacks = df.iloc[:, 0].dropna().tolist()
        elif file.name.endswith(".txt"):
            with open(file.name, "r", encoding="utf-8") as f:
                feedbacks = [l.strip() for l in f.readlines() if len(l.strip()) > 10]
        else:
            return "⚠️ Only .csv or .txt files are supported."

        if not feedbacks:
            return "⚠️ No valid feedback found in the file."

        total   = len(feedbacks)
        success = 0
        failed  = 0
        log     = []

        for i, text in enumerate(feedbacks, 1):
            try:
                analysis  = analyze_feedback(str(text))
                embedding = get_embedding(str(text))
                insert_feedback(
                    text      = str(text),
                    sentiment = analysis["sentiment"],
                    emotion   = analysis["emotion"],
                    key_issue = analysis["key_issue"],
                    embedding = embedding
                )
                success += 1
                log.append(f"✅ [{i}/{total}] {str(text)[:50]}... → {analysis['sentiment']}")
                time.sleep(0.3)
            except Exception as e:
                failed += 1
                log.append(f"❌ [{i}/{total}] Failed: {e}")

        return (
            f"📁 File processed!\n\n"
            f"✅ Success : {success}/{total}\n"
            f"❌ Failed  : {failed}/{total}\n"
            f"📦 Total in DB: {get_feedback_count()}\n\n"
            f"📋 Log:\n" + "\n".join(log)
        )
    except Exception as e:
        return f"❌ Error processing file: {e}"


# ── 3. Q&A ────────────────────────────────────────────────────────────────────

def handle_question(question: str):
    if not question or len(question.strip()) < 5:
        return "⚠️ Please enter a valid question.", ""
    result       = answer_question(question)
    answer       = result["answer"]
    sources      = result["sources"]
    sources_text = "\n\n📎 Sources Used:\n" + "\n".join([
        f"  [ID {s['id']}] Score:{s['score']} — {s['text']}"
        for s in sources
    ]) if sources else "\n\n📎 No sources found."
    return answer, sources_text


# ── 4. Grafana iframe ─────────────────────────────────────────────────────────

GRAFANA_URL = "http://localhost:3000/d/advhxxb/nefersurvey-intelligence?orgId=1&kiosk=true&theme=dark&refresh=10s&from=now-6h&to=now&timezone=browser"

def get_dashboard_html():
    ts = int(time.time())
    return f"""
    <div style="width:100%; height:850px; border-radius:12px; overflow:hidden; border:1px solid #6C63FF;">
        <iframe
            src="{GRAFANA_URL}&ts={ts}"
            width="100%"
            height="100%"
            frameborder="0"
            allow="fullscreen"
        ></iframe>
    </div>
    <p style="color:#a78bfa; text-align:center; margin-top:8px; font-size:13px;">
        📊 Live Grafana Dashboard — auto-refreshes every 10s |
        <a href="http://localhost:3000/d/advhxxb/nefersurvey-intelligence" target="_blank" style="color:#6C63FF;">Open fullscreen ↗</a>
    </p>
    """


# ── 5. Build UI ───────────────────────────────────────────────────────────────

def build_ui():
    with gr.Blocks(
        theme=gr.themes.Base(primary_hue="violet", neutral_hue="slate"),
        css="""
        .gradio-container { background: #0f0f1a; }
        h1 { color: #a78bfa !important; text-align: center; }
        h3 { color: #c4b5fd !important; }
        footer { display: none !important; }
        """
    ) as demo:

        gr.Markdown("""
        # 🧠 NeferSurvey — Survey Intelligence Engine
        ### AI-Powered Customer Feedback Analysis System
        ---
        """)

        with gr.Tabs():

            with gr.TabItem("📝 Submit Feedback"):
                gr.Markdown("### ✍️ Submit Single Feedback")
                with gr.Row():
                    with gr.Column(scale=2):
                        feedback_input = gr.Textbox(
                            label="Customer Feedback",
                            placeholder="Enter customer feedback here...",
                            lines=6
                        )
                        submit_btn = gr.Button("🚀 Analyze & Submit", variant="primary")
                    with gr.Column(scale=1):
                        analysis_output = gr.Textbox(
                            label="Analysis Result",
                            lines=8,
                            interactive=False
                        )

            with gr.TabItem("📁 Bulk Upload"):
                gr.Markdown("### 📁 Upload Feedback File")
                gr.Markdown("""
                Upload a **CSV** or **TXT** file containing multiple feedback entries.
                - **CSV**: must have a column named `feedback` or `text`
                - **TXT**: one feedback per line
                """)
                with gr.Row():
                    with gr.Column(scale=1):
                        file_input = gr.File(
                            label="Upload CSV or TXT file",
                            file_types=[".csv", ".txt"],
                            type="filepath"
                        )
                        upload_btn = gr.Button("📤 Process File", variant="primary")
                    with gr.Column(scale=2):
                        upload_output = gr.Textbox(
                            label="Processing Log",
                            lines=20,
                            interactive=False
                        )

            with gr.TabItem("📊 Dashboard"):
                gr.Markdown("### 📊 Live Intelligence Dashboard — Powered by Grafana")
                dashboard_frame = gr.HTML(value=get_dashboard_html())
                refresh_btn     = gr.Button("🔄 Refresh Dashboard", variant="secondary")

            with gr.TabItem("💬 Ask the Data"):
                gr.Markdown("### Ask Questions Grounded in Customer Feedback")
                gr.Markdown("*Answers generated exclusively from stored feedback — no hallucination.*")
                with gr.Row():
                    with gr.Column():
                        question_input = gr.Textbox(
                            label="Your Question",
                            placeholder="e.g. What are the most common complaints?",
                            lines=2
                        )
                        ask_btn = gr.Button("🔍 Ask", variant="primary")
                with gr.Row():
                    with gr.Column():
                        answer_output = gr.Textbox(
                            label="💬 Answer",
                            lines=6,
                            interactive=False
                        )
                    with gr.Column():
                        sources_output = gr.Textbox(
                            label="📎 Sources",
                            lines=6,
                            interactive=False
                        )

        submit_btn.click(fn=handle_feedback_submission, inputs=[feedback_input],  outputs=[analysis_output])
        upload_btn.click(fn=handle_file_upload,         inputs=[file_input],      outputs=[upload_output])
        refresh_btn.click(fn=get_dashboard_html,        inputs=[],                outputs=[dashboard_frame])
        ask_btn.click(fn=handle_question,               inputs=[question_input],  outputs=[answer_output, sources_output])

    return demo


if __name__ == "__main__":
    print("🚀 Launching NeferSurvey UI...")
    print("📊 Grafana Dashboard : http://localhost:3000")
    print("🤖 Gradio UI         : http://localhost:7860")
    print("🔌 API Server        : http://localhost:8000")
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, inbrowser=True)
