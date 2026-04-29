import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import re
from groq import Groq

# ─── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="SentiCo — Sentiment Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS — Dark Intelligence Aesthetic ───────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e2e8f0;
}

.stApp {
    background: #0a0a0f;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid #1e2030;
}

[data-testid="stSidebar"] * {
    color: #a0aec0 !important;
}

/* ── Header ── */
.sentico-header {
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid #1e2030;
    margin-bottom: 2rem;
}

.sentico-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #fff;
}

.sentico-logo span {
    color: #6366f1;
}

.sentico-tagline {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #4a5568;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

/* ── Metric Cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: #0f0f1a;
    border: 1px solid #1e2030;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
}

.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #4a5568;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #fff;
    line-height: 1;
}

.metric-sub {
    font-size: 0.72rem;
    color: #4a5568;
    margin-top: 0.35rem;
}

/* ── Section Headers ── */
.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #6366f1;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e2030;
}

/* ── Risk Badge ── */
.risk-badge {
    display: inline-block;
    padding: 0.3rem 0.9rem;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
}

.risk-green { background: #0d2b1a; color: #34d399; border: 1px solid #065f46; }
.risk-yellow { background: #2b2200; color: #fbbf24; border: 1px solid #78350f; }
.risk-red { background: #2b0a0a; color: #f87171; border: 1px solid #7f1d1d; }

/* ── Analysis Output ── */
.analysis-container {
    background: #0f0f1a;
    border: 1px solid #1e2030;
    border-radius: 8px;
    padding: 2rem;
    line-height: 1.8;
}

.analysis-container h2 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #6366f1;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2030;
    padding-bottom: 0.5rem;
    margin: 2rem 0 1rem 0;
}

.analysis-container p, .analysis-container li {
    color: #a0aec0;
    font-size: 0.92rem;
}

.analysis-container strong {
    color: #e2e8f0;
}

/* ── Upload Zone ── */
[data-testid="stFileUploader"] {
    background: #0f0f1a;
    border: 1px dashed #2d3748;
    border-radius: 8px;
    padding: 1rem;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

/* ── Info/Warning boxes ── */
.stInfo, .stWarning, .stSuccess, .stError {
    border-radius: 6px !important;
    font-size: 0.85rem !important;
}

/* ── Input fields ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: #0f0f1a !important;
    border: 1px solid #2d3748 !important;
    color: #e2e8f0 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Divider ── */
hr {
    border-color: #1e2030 !important;
}

/* ── Status dot ── */
.status-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #34d399;
    margin-right: 6px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Download button ── */
.stDownloadButton > button {
    background: #0f0f1a !important;
    color: #6366f1 !important;
    border: 1px solid #6366f1 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0f0f1a !important;
    border: 1px solid #1e2030 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    color: #a0aec0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────
st.markdown("""
<div class="sentico-header">
    <div class="sentico-logo">Senti<span>Co</span></div>
    <div class="sentico-tagline">◆ Customer Intelligence Platform &nbsp;·&nbsp; Internal Analyst Tool</div>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ◆ Configuration")
    
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Get your free key at console.groq.com"
    )
    
    st.markdown("---")
    
    business_name = st.text_input("Business Name", placeholder="e.g. Joe's Tacos")
    
    platform = st.selectbox(
        "Review Platform",
        ["Google Reviews", "Yelp", "DoorDash", "Uber Eats", "Grubhub", "Instagram", "YouTube", "Other"]
    )
    
    model_choice = st.selectbox(
        "AI Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ],
        help="70b = best quality | 8b = fastest, fewer tokens"
    )
    
    st.markdown("---")
    
    if not api_key:
        st.warning("⚠ Add your Groq API key to begin.")
        st.markdown("[Get free key →](https://console.groq.com)")
    else:
        st.markdown('<span class="status-dot"></span> **API Connected**', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; line-height:1.8;">
    MODEL<br>Open-source Llama<br>via Groq inference<br><br>
    BUILT BY<br>Pablo · San Marcos TX<br><br>
    VERSION<br>v1.0 MVP
    </div>
    """, unsafe_allow_html=True)

# ─── Step 1: Load Reviews ────────────────────────────────────────
st.markdown('<div class="section-header">01 — Load Reviews</div>', unsafe_allow_html=True)

input_method = st.radio(
    "Input method",
    ["📁 Upload JSON / CSV file", "✏️ Paste reviews manually"],
    horizontal=True
)

reviews = []

if input_method == "📁 Upload JSON / CSV file":
    uploaded_file = st.file_uploader(
        "Drop your Outscraper or Apify export here",
        type=["json", "csv"]
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".json"):
                data = json.load(uploaded_file)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            text = (
                                item.get("review_text") or
                                item.get("text") or
                                item.get("snippet") or
                                item.get("body") or ""
                            )
                            if text and text.strip():
                                reviews.append({
                                    "text": text.strip(),
                                    "rating": item.get("review_rating") or item.get("rating") or item.get("stars") or "N/A",
                                    "date": item.get("review_datetime_utc") or item.get("date") or "Unknown"
                                })

            elif uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                text_col = None
                for col in ["review_text", "text", "snippet", "body", "comment", "review"]:
                    if col in df.columns:
                        text_col = col
                        break
                if text_col:
                    for _, row in df.iterrows():
                        if pd.notna(row[text_col]) and str(row[text_col]).strip():
                            reviews.append({
                                "text": str(row[text_col]).strip(),
                                "rating": row.get("review_rating") or row.get("rating") or "N/A",
                                "date": row.get("review_datetime_utc") or row.get("date") or "Unknown"
                            })
                else:
                    st.warning("Could not detect a review text column. Expected: review_text, text, comment, or body.")

            if reviews:
                st.success(f"✓ {len(reviews)} reviews loaded from {uploaded_file.name}")

        except Exception as e:
            st.error(f"File read error: {e}")

else:
    pasted_text = st.text_area(
        "One review per line",
        height=180,
        placeholder="The tacos were incredible, best in San Marcos\nWait time was 45 minutes, way too long\nFriendly staff but the queso was cold"
    )
    if pasted_text.strip():
        for line in pasted_text.strip().split("\n"):
            if line.strip():
                reviews.append({"text": line.strip(), "rating": "N/A", "date": "Unknown"})
        st.success(f"✓ {len(reviews)} reviews loaded from paste")

# ─── Preview + Stats ─────────────────────────────────────────────
if reviews:
    total_in_file = len(reviews)
    blank_count = sum(1 for r in reviews if not r["text"].strip())
    usable = total_in_file - blank_count
    capped = min(usable, 80)

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Entries", total_in_file)
    with col2:
        st.metric("Usable Reviews", usable)
    with col3:
        st.metric("Blank / Skipped", blank_count)
    with col4:
        st.metric("Will Analyze", capped)

    if usable > 80:
        st.warning(f"⚠ Free tier cap: analyzing first 80 of {usable} reviews. Upgrade at console.groq.com/settings/billing for full dataset.")

    # Rating distribution chart
    ratings = [r["rating"] for r in reviews if r["rating"] != "N/A"]
    if ratings:
        with st.expander("📊 Rating Distribution"):
            rating_counts = pd.Series(ratings).value_counts().sort_index()
            fig = go.Figure(go.Bar(
                x=[str(r) for r in rating_counts.index],
                y=rating_counts.values,
                marker=dict(
                    color=rating_counts.values,
                    colorscale=[[0, '#f87171'], [0.5, '#fbbf24'], [1, '#34d399']],
                    showscale=False
                ),
                text=rating_counts.values,
                textposition='outside',
                textfont=dict(color='#a0aec0', size=11)
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='IBM Plex Mono', color='#a0aec0', size=11),
                xaxis=dict(title='Star Rating', gridcolor='#1e2030', color='#4a5568'),
                yaxis=dict(title='Count', gridcolor='#1e2030', color='#4a5568'),
                margin=dict(l=20, r=20, t=20, b=20),
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"Preview first 5 reviews"):
        for i, r in enumerate(reviews[:5]):
            st.markdown(f"**{i+1}.** {r['text'][:200]}")
            st.caption(f"Rating: {r['rating']} · Date: {r['date']}")
            if i < 4:
                st.divider()

# ─── Step 2: Analyze ─────────────────────────────────────────────
st.markdown('<div class="section-header">02 — Analyze</div>', unsafe_allow_html=True)

analyze_btn = st.button(
    "◆ RUN SENTIMENT ANALYSIS",
    disabled=not (reviews and api_key)
)

if analyze_btn:
    reviews_to_analyze = reviews[:80]

    with st.spinner("Running analysis with Llama 3.3 via Groq..."):

        review_block = "\n\n".join(
            [f"Review {i+1} (Rating: {r['rating']}, Date: {r['date']}):\n{r['text']}"
             for i, r in enumerate(reviews_to_analyze)]
        )

        prompt = f"""You are a senior customer sentiment analyst. Analyze these {len(reviews_to_analyze)} reviews for {business_name or 'this business'} on {platform}. Be specific, quote directly, name exact items/staff behaviors. Flag any complaint appearing 3+ times as priority.

REVIEWS:
{review_block}

Respond with ONLY these sections in order:

## HEALTH SCORECARD
- Score: [X.X/10] | Positive: [%] | Neutral: [%] | Negative: [%]
- Promoter Proxy: [% recommend language] vs [% warn-away language]
- Velocity: [Increasing/Stable/Declining/Unknown] — one sentence
- Risk: [🟢 GREEN / 🟡 YELLOW / 🔴 RED] — one sentence

## EXECUTIVE SUMMARY
3 sentences: overall experience, biggest strength, most urgent problem.

## TOP PRAISE THEMES
Top 3-5 only. Each: theme name — specific explanation — one direct quote.

## TOP COMPLAINT CLUSTERS
Top 3-5 only. Each: complaint name — frequency — severity [Low/Med/High] — one direct quote.

## OPERATIONAL DAMAGE REPORT
Top 3 only. Each on one line:
[Problem] | [quote] | [Low/Med/High] | [Staff/Kitchen/Platform/Facility/Management] | [fix]

## COMPETITIVE SIGNAL
- Competitors named: [list or "none detected"]
- Comparison language: [examples or "none detected"]
- Platform friction: [delivery vs dine-in complaints or "none detected"]

## NOTABLE KEYWORDS
- Positive: [8-10 words]
- Negative: [5-8 words]

## TIMING PATTERNS
Note date spikes, weekend vs weekday clusters, improving or declining trend. If dates unknown, say so in one sentence.

## RECOMMENDED ACTIONS
[URGENT — 7 days] Title: what, why, how.
[SHORT-TERM — 30 days] Title: what, why, how.
[STRATEGIC — 60-90 days] Title: what, why, how.
[QUICK WIN] Title: what, why, how."""

        try:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=model_choice,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior customer sentiment analyst. Be specific, direct, and quote evidence from reviews."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000,
            )

            analysis = response.choices[0].message.content

            # ── Parse sentiment numbers from response ──
            score_match = re.search(r'Score:\s*([\d.]+)/10', analysis)
            pos_match = re.search(r'Positive:\s*(\d+)%', analysis)
            neu_match = re.search(r'Neutral:\s*(\d+)%', analysis)
            neg_match = re.search(r'Negative:\s*(\d+)%', analysis)
            risk_match = re.search(r'Risk:.*?(GREEN|YELLOW|RED)', analysis)

            st.session_state["analysis"] = analysis
            st.session_state["review_count"] = len(reviews_to_analyze)
            st.session_state["business"] = business_name or "Business"
            st.session_state["platform"] = platform
            st.session_state["model"] = model_choice
            st.session_state["score"] = score_match.group(1) if score_match else "—"
            st.session_state["positive"] = int(pos_match.group(1)) if pos_match else None
            st.session_state["neutral"] = int(neu_match.group(1)) if neu_match else None
            st.session_state["negative"] = int(neg_match.group(1)) if neg_match else None
            st.session_state["risk"] = risk_match.group(1) if risk_match else None

        except Exception as e:
            st.error(f"Groq API error: {e}")
            st.info("Check your API key at console.groq.com")

# ─── Results ─────────────────────────────────────────────────────
if "analysis" in st.session_state:

    st.markdown('<div class="section-header">03 — Results</div>', unsafe_allow_html=True)

    # ── KPI Cards ──
    risk = st.session_state.get("risk")
    risk_class = {"GREEN": "risk-green", "YELLOW": "risk-yellow", "RED": "risk-red"}.get(risk, "risk-yellow")
    risk_emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}.get(risk, "🟡")

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Sentiment Score</div>
            <div class="metric-value">{st.session_state.get('score', '—')}<span style="font-size:1rem;color:#4a5568">/10</span></div>
            <div class="metric-sub">{st.session_state['business']}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Reviews Analyzed</div>
            <div class="metric-value">{st.session_state['review_count']}</div>
            <div class="metric-sub">{st.session_state['platform']}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Risk Level</div>
            <div class="metric-value" style="font-size:1.2rem; padding-top:0.2rem;">
                <span class="risk-badge {risk_class}">{risk_emoji} {risk or 'UNKNOWN'}</span>
            </div>
            <div class="metric-sub">Overall health signal</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Model Used</div>
            <div class="metric-value" style="font-size:0.85rem; padding-top:0.3rem; color:#6366f1;">{st.session_state['model']}</div>
            <div class="metric-sub">via Groq inference</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sentiment Donut Chart ──
    pos = st.session_state.get("positive")
    neu = st.session_state.get("neutral")
    neg = st.session_state.get("negative")

    if all(v is not None for v in [pos, neu, neg]):
        col_chart, col_report = st.columns([1, 2])

        with col_chart:
            st.markdown('<div class="section-header">Sentiment Breakdown</div>', unsafe_allow_html=True)
            fig_donut = go.Figure(go.Pie(
                labels=["Positive", "Neutral", "Negative"],
                values=[pos, neu, neg],
                hole=0.65,
                marker=dict(colors=["#34d399", "#6366f1", "#f87171"]),
                textinfo="label+percent",
                textfont=dict(family="IBM Plex Mono", size=11, color="#e2e8f0"),
                hovertemplate="%{label}: %{value}%<extra></extra>"
            ))
            fig_donut.add_annotation(
                text=f"<b>{st.session_state.get('score', '?')}</b><br><span style='font-size:10px'>/10</span>",
                x=0.5, y=0.5,
                font=dict(family="IBM Plex Mono", size=22, color="#ffffff"),
                showarrow=False
            )
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                height=280
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            # Bar chart
            fig_bar = go.Figure(go.Bar(
                x=["Positive", "Neutral", "Negative"],
                y=[pos, neu, neg],
                marker_color=["#34d399", "#6366f1", "#f87171"],
                text=[f"{v}%" for v in [pos, neu, neg]],
                textposition="outside",
                textfont=dict(color="#a0aec0", size=11, family="IBM Plex Mono")
            ))
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Mono", color="#a0aec0", size=10),
                xaxis=dict(gridcolor="#1e2030", color="#4a5568"),
                yaxis=dict(gridcolor="#1e2030", color="#4a5568", ticksuffix="%"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=220
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_report:
            st.markdown('<div class="section-header">Full Report</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="analysis-container">{st.session_state["analysis"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="analysis-container">{st.session_state["analysis"]}</div>', unsafe_allow_html=True)

    # ─── Export ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">04 — Export</div>', unsafe_allow_html=True)

    export_content = f"""# SentiCo Sentiment Report

**Business:** {st.session_state['business']}
**Platform:** {st.session_state['platform']}
**Reviews Analyzed:** {st.session_state['review_count']}
**Sentiment Score:** {st.session_state.get('score', '—')}/10
**Risk Level:** {st.session_state.get('risk', '—')}
**Model:** {st.session_state['model']} via Groq

---

{st.session_state['analysis']}

---
*Report generated by SentiCo | Built by Pablo*
*Powered by open-source Llama via Groq inference*
"""

    st.download_button(
        label="⬇ Download Report (.md)",
        data=export_content,
        file_name=f"sentico_{st.session_state['business'].replace(' ', '_')}_report.md",
        mime="text/markdown"
    )

elif not reviews:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color: #2d3748; font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em;">
        ◆ &nbsp; UPLOAD A FILE OR PASTE REVIEWS ABOVE TO BEGIN
    </div>
    """, unsafe_allow_html=True)
