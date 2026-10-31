
import streamlit as st
from groq import Groq
import math

st.set_page_config(
    page_title="Clutch | Match Centre",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def get_ai_response(system_prompt, user_prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_completion_tokens=700
        )

        return response.choices[0].message.content

    except KeyError:
        return "GROQ_API_KEY is missing. Please add it to your Streamlit secrets."

    except Exception as e:
        return f"AI request failed: {str(e)}"


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

# Context shared with both AI features.
event_context = "\n".join(
    [
        f"Over {event['over']}: {event['event']} - {event['details']}"
        for event in match_events
    ]
)

match_context = f"""
Match: India vs Australia, T20 International, second innings.
India's score: {runs_scored}/{wickets_lost}.
Target: {target}.
Overs completed: {overs_completed} out of {total_overs}.
Runs needed: {runs_needed}.
Balls remaining: {balls_remaining}.

Selected key events (this is NOT the complete ball-by-ball commentary):
{event_context}

Important:
- These are only selected events, not the full innings.
- Two wickets appear in the listed events. The score shows four wickets in total.
- Do not invent additional events, player statistics, or match conditions.
- If information is unavailable, clearly say so.
"""


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
        Get an AI-generated story of key moments, wickets,
        boundaries, and changes in match momentum.
    </div>
</div>
""", unsafe_allow_html=True)

fan_level = st.selectbox(
    "Choose how you want the match explained",
    ["Beginner", "Regular fan", "Analyst"],
    key="fan_level"
)

if st.button("⚡ Generate AI Match Story", use_container_width=True):

    system_prompt = f"""
    You are Clutch, a cricket match companion.

    Explain cricket in a clear, engaging and useful way.

    The user's cricket knowledge level is: {fan_level}.

    Adjust your explanation:
    - Beginner: use simple words and explain cricket terms.
    - Regular fan: explain the important moments and their impact.
    - Analyst: give more tactical context, while staying grounded in the data.

    Use only the match information supplied.
    Do not invent events, statistics, player form, or match conditions.
    Make clear that the event list contains selected moments only.
    Focus on what happened, why it matters, and what to watch next.
    Keep the answer concise and easy to read.
    """

    with st.spinner("Clutch is analysing the match..."):
        story = get_ai_response(
            system_prompt,
            f"Create a match story using this information:\n{match_context}"
        )

    st.markdown("### 🏏 AI Match Story")
    st.markdown(story)

    st.caption(
        "AI-generated explanation based on selected sample match events. "
        "Not connected to live match data."
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

runs_remaining = max(prediction_target - current_runs, 0)
balls_remaining_predictor = (20 - overs) * 6

st.markdown("---")

if current_runs >= prediction_target:

    st.success("🏆 The target has been reached!")

elif wickets == 10 or balls_remaining_predictor == 0:

    st.error("The chase is over. The target was not reached.")

else:
    overs_remaining = balls_remaining_predictor / 6
    required_run_rate = runs_remaining / overs_remaining

    current_run_rate = (
        current_runs / overs if overs > 0 else 0
    )

    wickets_remaining = 10 - wickets

    # Simple heuristic score, not a trained ML model.
    difficulty = (
        (required_run_rate * 3)
        - (wickets_remaining * 1.5)
        - (current_run_rate * 0.5)
    )

    estimated_chance = 100 / (
        1 + math.exp(max(-20, min(20, difficulty - 12)))
    )

    estimated_chance = max(5, min(95, estimated_chance))

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric("Runs remaining", runs_remaining)

    with metric2:
        st.metric("Balls remaining", balls_remaining_predictor)

    with metric3:
        st.metric("Required run rate", f"{required_run_rate:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### Illustrative chase outlook")
    st.progress(int(estimated_chance))

    st.markdown(
        f"""
        <div style="text-align:center;padding:10px;">
            <div style="font-size:42px;font-weight:700;color:#D5FF65;">
                {estimated_chance:.1f}%
            </div>
            <div style="color:#9BA2AE;font-size:13px;">
                Prototype heuristic score, not a real win probability
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
        "heuristic, not a trained machine-learning model or live match data."
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
        Ask Clutch anything about the match. Get an explanation
        tailored to your cricket knowledge level.
    </div>
</div>
""", unsafe_allow_html=True)

question = st.text_input(
    "Ask a question",
    placeholder="e.g. Why was Rahul's wicket important?",
    key="clutch_question"
)

if st.button("Ask Clutch →", use_container_width=True):

    if not question.strip():
        st.warning("Please enter a question first.")

    else:
        system_prompt = f"""
        You are Clutch, an AI cricket match companion.

        The user's cricket knowledge level is: {fan_level}.

        Answer in a clear and friendly way.
        Use only the match information provided.
        Do not invent scores, events, player statistics, or match conditions.
        If the data does not contain the answer, say so.
        Explain cricket terminology when useful.
        Keep answers focused and concise.
        """

        with st.spinner("Clutch is thinking..."):
            answer = get_ai_response(
                system_prompt,
                f"""
                Match information:
                {match_context}

                User's question:
                {question}
                """
            )

        st.markdown("#### 💬 Clutch's Answer")
        st.markdown(answer)

        st.caption(
            "AI-generated answer based on the supplied sample match data. "
            "Not connected to live scores."
        )


# ---------- FOOTER ----------

st.markdown("""
<div class="footer">
    CLUTCH © 2026 &nbsp; • &nbsp; BUILT FOR THE FANS
    <br><br>
    AI-powered prototype using sample match data. Not connected to live scores.
</div>
""", unsafe_allow_html=True)
