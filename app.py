import streamlit as st

st.set_page_config(
    page_title="Clutch | Match Centre",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    .stApp {
        background-color: #0B0D10;
        color: #F4F5F7;
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #F4F5F7 !important;
    }

    p, label, span {
        font-family: 'DM Sans', sans-serif;
    }

    .brand {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -1.5px;
        color: #D5FF65;
    }

    .brand-subtitle {
        color: #858B98;
        font-size: 13px;
        margin-top: -5px;
    }

    .section-label {
        color: #A1A7B2;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 14px;
    }

    .match-card {
        background: linear-gradient(135deg, #191D24, #12151A);
        border: 1px solid #2A3039;
        border-radius: 18px;
        padding: 26px;
        margin: 12px 0 24px 0;
    }

    .match-status {
        color: #D5FF65;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }

    .match-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 23px;
        font-weight: 600;
        margin: 12px 0 4px 0;
        color: #F4F5F7;
    }

    .match-subtitle {
        color: #858B98;
        font-size: 13px;
    }

    .score-label {
        color: #858B98;
        font-size: 13px;
    }

    .score-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 36px;
        font-weight: 700;
        letter-spacing: -1px;
        color: #FFFFFF;
        margin-top: 5px;
    }

    .score-number span {
        font-size: 17px;
        color: #858B98;
        font-weight: 500;
    }

    .divider {
        border-top: 1px solid #2A3039;
        margin: 22px 0;
    }

    .metric-card {
        background: #15191F;
        border: 1px solid #282E37;
        border-radius: 14px;
        padding: 18px;
        min-height: 105px;
        margin-bottom: 10px;
    }

    .metric-label {
        color: #939AA7;
        font-size: 12px;
        margin-bottom: 10px;
    }

    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 27px;
        font-weight: 600;
        color: #F4F5F7;
    }

    .metric-highlight {
        color: #D5FF65;
    }

    .feature-card {
        background: #15191F;
        border: 1px solid #282E37;
        border-radius: 16px;
        padding: 22px;
        min-height: 130px;
        margin-bottom: 12px;
    }

    .feature-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 19px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #F4F5F7;
    }

    .feature-description {
        color: #9BA2AE;
        font-size: 13px;
        line-height: 1.7;
    }

    div.stButton > button {
        background: #D5FF65;
        color: #10130B;
        border: none;
        border-radius: 9px;
        font-weight: 700;
        min-height: 44px;
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        background: #C3EE54;
        color: #10130B;
        border: none;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    .footer {
        color: #626A77;
        font-size: 12px;
        text-align: center;
        padding-top: 24px;
        border-top: 1px solid #252A32;
        margin-top: 30px;
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 1rem 2rem 1rem;
        }

        .match-card {
            padding: 18px;
        }

        .score-number {
            font-size: 28px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ---------- SAMPLE MATCH DATA ----------
target = 180
runs_scored = 120
wickets_lost = 4
overs_completed = 15
total_overs = 20

runs_needed = target - runs_scored
balls_remaining = (total_overs - overs_completed) * 6

# Sample events from the current innings.
# Two wickets fell in these events; two had fallen earlier.
match_events = [
    {
        "over": "10.2",
        "event": "FOUR",
        "details": "Gill hits a boundary through cover."
    },
    {
        "over": "11.4",
        "event": "WICKET",
        "details": "Kohli is caught at mid-wicket."
    },
    {
        "over": "12.1",
        "event": "SIX",
        "details": "Rahul clears the boundary."
    },
    {
        "over": "13.3",
        "event": "FOUR",
        "details": "Rahul finds the gap on the leg side."
    },
    {
        "over": "14.5",
        "event": "WICKET",
        "details": "Rahul is bowled."
    }
]


# ---------- HEADER ----------
header_left, header_right = st.columns([3, 1])

with header_left:
    st.markdown(
        '<div class="brand">CLUTCH<span style="color:#F4F5F7">.</span></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="brand-subtitle">THE INTELLIGENT MATCH COMPANION</div>',
        unsafe_allow_html=True
    )

with header_right:
    st.markdown(
        '<div style="text-align:right;color:#858B98;font-size:12px;padding-top:12px;">'
        'DEMO MODE &nbsp; • &nbsp; T20</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ---------- MATCH CENTRE / 01 ----------
st.markdown(
    '<div class="section-label">MATCH CENTRE / 01</div>',
    unsafe_allow_html=True
)

st.markdown(f"""
<div class="match-card">
    <div class="match-status">● &nbsp; MATCH SIMULATION</div>
    <div class="match-title">India vs Australia</div>
    <div class="match-subtitle">
        T20 International &nbsp; / &nbsp; Second innings
    </div>
    <div class="divider"></div>
    <div class="score-label">INDIA &nbsp; • &nbsp; CHASING {target}</div>
    <div class="score-number">{runs_scored}<span>/{wickets_lost}</span></div>
    <div class="match-subtitle">
        {overs_completed}.0 overs &nbsp; / &nbsp; {total_overs} overs
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- THE NUMBERS / 02 ----------
st.markdown(
    '<div class="section-label">THE NUMBERS / 02</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

metrics = [
    (col1, "TARGET", str(target), False),
    (col2, "RUNS NEEDED", str(runs_needed), True),
    (col3, "BALLS LEFT", str(balls_remaining), False),
]

for column, label, value, highlight in metrics:
    with column:
        value_class = (
            "metric-value metric-highlight"
            if highlight
            else "metric-value"
        )

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="{value_class}">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ---------- CATCH ME UP / 03 ----------
st.markdown(
    '<div class="section-label">CATCH ME UP / 03</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="feature-card">
    <div class="feature-title">Missed the action?</div>
    <div class="feature-description">
        Get a quick recap of key moments, wickets, and boundaries
        so you can understand how the match has unfolded.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("⚡ Summarize Match", use_container_width=True):

    wickets = [
        event for event in match_events
        if event["event"] == "WICKET"
    ]

    boundaries = [
        event for event in match_events
        if event["event"] in ["FOUR", "SIX"]
    ]

    st.markdown("### 🏏 Match Summary")

    st.write(
        f"India has scored **{runs_scored}/{wickets_lost}** "
        f"while chasing {target}. "
        f"In the listed events, there were **{len(wickets)} wickets** "
        f"and **{len(boundaries)} boundaries**."
    )

    st.markdown("#### Key moments")

    for event in match_events:
        if event["event"] == "WICKET":
            icon = "🔴"
        elif event["event"] == "SIX":
            icon = "🟢"
        else:
            icon = "⚡"

        st.markdown(
            f"{icon} **Over {event['over']} — {event['event']}**  \n"
            f"{event['details']}"
        )

    st.caption(
        "This recap is generated from sample match events, "
        "not from live match data or an AI model."
    )


# ---------- MATCH INSIGHTS / 04 ----------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-label">MATCH INSIGHTS / 04</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="feature-card">
    <div class="feature-title">Understand the pressure.</div>
    <div class="feature-description">
        Explore the required run rate and understand what the
        chasing team needs to do to reach its target.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Analyse match situation  →", use_container_width=True):

    required_rate = runs_needed / (balls_remaining / 6)
    current_rate = runs_scored / overs_completed

    st.markdown(
        '<div class="section-label">CURRENT MATCH ANALYSIS</div>',
        unsafe_allow_html=True
    )

    a, b = st.columns(2)

    with a:
        st.metric("Required run rate", f"{required_rate:.2f}")

    with b:
        st.metric("Current run rate", f"{current_rate:.2f}")

    st.info(
        f"India needs {runs_needed} runs from {balls_remaining} balls. "
        f"The required rate is {required_rate:.2f} runs per over, "
        f"compared with the current scoring rate of {current_rate:.2f}."
    )

    st.caption(
        "This is a mathematical match analysis, not a prediction "
        "of the probability of winning."
    )
    # ---------- WIN PREDICTOR / 05 ----------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-label">WIN PREDICTOR / 05</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="feature-card">
    <div class="feature-title">Can they pull off the chase?</div>
    <div class="feature-description">
        Adjust the match situation to explore how the runs required,
        wickets remaining, and overs left affect the difficulty of the chase.
    </div>
</div>
""", unsafe_allow_html=True)

# User inputs
st.markdown("#### Adjust match situation")

input_col1, input_col2 = st.columns(2)

with input_col1:
    current_runs = st.slider(
        "Runs scored",
        min_value=0,
        max_value=250,
        value=120,
        step=1,
        key="predictor_runs"
    )

    wickets = st.slider(
        "Wickets lost",
        min_value=0,
        max_value=10,
        value=4,
        step=1,
        key="predictor_wickets"
    )

with input_col2:
    overs = st.slider(
        "Completed overs",
        min_value=0,
        max_value=19,
        value=15,
        step=1,
        key="predictor_overs"
    )

    prediction_target = st.number_input(
        "Target runs",
        min_value=1,
        max_value=300,
        value=180,
        step=1,
        key="predictor_target"
    )

# Calculate match situation
runs_remaining = max(prediction_target - current_runs, 0)
balls_remaining_predictor = (20 - overs) * 6

st.markdown("---")

# Handle completed or tied chases
if current_runs >= prediction_target:

    st.success("🏆 The target has been reached!")

elif wickets == 10 or balls_remaining_predictor == 0:

    st.error("The chase is over. The target was not reached.")

else:
    overs_remaining = balls_remaining_predictor / 6

    required_run_rate = runs_remaining / overs_remaining

    current_run_rate = (
        current_runs / overs
        if overs > 0
        else 0
    )

    wickets_remaining = 10 - wickets

    # Simple heuristic score — not a trained ML model.
    difficulty = (
        (required_run_rate * 3)
        - (wickets_remaining * 1.5)
        - (current_run_rate * 0.5)
    )

    # Convert the difficulty score to a rough probability.
    # Clamp the result to keep it between 5% and 95%.
    import math

    estimated_chance = 100 / (1 + math.exp(
        max(-20, min(20, difficulty - 12))
    ))

    estimated_chance = max(
        5,
        min(95, estimated_chance)
    )

    # Match situation metrics
    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric("Runs remaining", runs_remaining)

    with metric2:
        st.metric("Balls remaining", balls_remaining_predictor)

    with metric3:
        st.metric(
            "Required run rate",
            f"{required_run_rate:.2f}"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### Estimated chasing-team outlook")

    st.progress(int(estimated_chance))

    st.markdown(
        f"""
        <div style="text-align:center;padding:10px;">
            <div style="font-size:42px;font-weight:700;color:#D5FF65;">
                {estimated_chance:.1f}%
            </div>
            <div style="color:#9BA2AE;font-size:13px;">
                Illustrative chance of completing the chase
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if required_run_rate > 12:
        st.warning(
            "The chase is under heavy scoring pressure. "
            "The team needs more than 12 runs per over."
        )

    elif required_run_rate > 9:
        st.info(
            "The scoring rate needs to increase. "
            "The remaining wickets could be important."
        )

    else:
        st.success(
            "The required scoring rate is relatively manageable, "
            "but wickets and match conditions still matter."
        )

    st.caption(
        "Prototype estimate only. This uses a manually designed "
        "heuristic, not a trained machine-learning model or live match data. "
        "It does not account for batter quality, bowler quality, venue, "
        "pitch, weather, or historical match outcomes."
    )
    # ---------- ASK CLUTCH / 06 ----------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-label">ASK CLUTCH / 06</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="feature-card">
    <div class="feature-title">Your match. Your questions.</div>
    <div class="feature-description">
        Ask about the score, required run rate, remaining balls,
        or key moments from the match.
    </div>
</div>
""", unsafe_allow_html=True)

question = st.text_input(
    "Ask a question",
    placeholder="e.g. How many runs does India need?",
    key="clutch_question"
)

if st.button("Ask Clutch →", use_container_width=True):

    if not question.strip():
        st.warning("Please enter a question first.")

    else:
        q = question.lower()

        st.markdown("#### 💬 Clutch's Answer")

        if "target" in q:
            st.write(
                f"India is chasing a target of {target} runs."
            )

        elif "run rate" in q or "required rate" in q:
            rate = runs_needed / (balls_remaining / 6)

            st.write(
                f"India needs {runs_needed} runs from "
                f"{balls_remaining} balls. The required run rate "
                f"is {rate:.2f} runs per over."
            )

        elif "how many runs" in q or "runs needed" in q:
            st.write(
                f"India needs {runs_needed} more runs "
                f"to reach the target of {target}."
            )

        elif "ball" in q or "overs left" in q:
            st.write(
                f"There are {balls_remaining} balls remaining "
                f"({balls_remaining // 6} overs)."
            )

        elif "wicket" in q:
            st.write(
                f"India has lost {wickets_lost} wickets "
                f"and has {10 - wickets_lost} wickets remaining."
            )

        elif "boundary" in q or "four" in q or "six" in q:
            boundaries = [
                event for event in match_events
                if event["event"] in ["FOUR", "SIX"]
            ]

            st.write(
                f"There are {len(boundaries)} boundaries "
                "in the listed sample events."
            )

        elif "last" in q or "moment" in q or "happen" in q:
            last_event = match_events[-1]

            st.write(
                f"The latest listed event is from over "
                f"{last_event['over']}: {last_event['details']}"
            )

        else:
            st.info(
                "I can answer questions about the target, runs needed, "
                "required run rate, balls remaining, wickets, and "
                "key moments. Try asking about one of these!"
            )

    st.caption(
        "Prototype question answering using predefined rules. "
        "Not connected to an AI model or live match data."
    )


# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
    CLUTCH © 2026 &nbsp; • &nbsp; BUILT FOR THE FANS
    <br><br>
    Prototype using sample match data. Not connected to live scores.
</div>
""", unsafe_allow_html=True)