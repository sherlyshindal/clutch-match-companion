import math
import requests
import streamlit as st
from groq import Groq

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Clutch | Match Centre",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- API HELPERS ----------
@st.cache_data(ttl=60)
def get_cricket_matches():
    """Fetch current, upcoming, and recently completed matches from CricketData."""
    api_key = st.secrets.get("CRICKET_API_KEY")
    if not api_key:
        raise ValueError("CRICKET_API_KEY is missing from Streamlit secrets.")

    response = requests.get(
        "https://api.cricapi.com/v1/currentMatches",
        params={"apikey": api_key, "offset": 0},
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()

    if result.get("status") != "success":
        raise ValueError(result.get("reason", "The cricket API returned an error."))

    return result.get("data", [])


def get_ai_response(system_prompt, user_prompt):
    """Send a prompt to Groq and return the model response."""
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            return "GROQ_API_KEY is missing. Add it to your Streamlit secrets."

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_completion_tokens=700,
        )
        return response.choices[0].message.content or "Clutch couldn't generate a response."
    except Exception as error:
        return f"AI request failed: {error}"


def overs_to_balls(overs_value):
    """
    Cricket overs are not decimal numbers:
    5.1 means 5 overs and 1 ball, i.e. 31 balls.
    """
    try:
        text = str(overs_value)
        if "." in text:
            whole, ball_part = text.split(".", 1)
            whole_overs = int(whole or 0)
            balls = int((ball_part + "0")[:1])
        else:
            whole_overs = int(float(text))
            balls = 0
        balls = max(0, min(balls, 5))
        return whole_overs * 6 + balls
    except (TypeError, ValueError):
        return None


def format_score(score):
    runs = score.get("r", "?")
    wickets = score.get("w", "?")
    overs = score.get("o", "?")
    innings = score.get("inning", "Innings")
    return f"{innings}: {runs}/{wickets} ({overs} overs)"


def build_match_context(match):
    teams = match.get("teams") or []
    scores = match.get("score") or []
    lines = [
        f"Match: {match.get('name', 'Unknown match')}",
        f"Teams: {', '.join(teams) if teams else 'Not available'}",
        f"Match type: {match.get('matchType', 'Not available')}",
        f"Status: {match.get('status', 'Not available')}",
        f"Venue: {match.get('venue', 'Not available')}",
        f"Date: {match.get('date', 'Not available')}",
    ]
    if scores:
        lines.append("Scores returned by the API:")
        lines.extend(f"- {format_score(score)}" for score in scores)
    else:
        lines.append("The API has not supplied score details for this match.")

    lines.append(
        "Data limitation: the available response contains match metadata and score summaries only. "
        "It does not provide verified ball-by-ball events in this app. Do not invent events, "
        "player performances, partnerships, toss details, or match conditions."
    )
    return "\n".join(lines)


def get_match_numbers(match):
    """
    Return basic chase metrics when the API provides at least two innings
    and a recognizable limited-overs format. Otherwise return None.
    """
    scores = match.get("score") or []
    match_type = str(match.get("matchType", "")).lower()

    if match_type not in {"t20", "odi"} or len(scores) < 2:
        return None

    total_overs = 20 if match_type == "t20" else 50
    first_innings = scores[0]
    current_innings = scores[-1]

    try:
        target = int(first_innings["r"]) + 1
        runs = int(current_innings["r"])
        wickets = int(current_innings["w"])
        balls_faced = overs_to_balls(current_innings["o"])
        if balls_faced is None:
            return None

        total_balls = total_overs * 6
        balls_left = max(total_balls - balls_faced, 0)
        runs_needed = max(target - runs, 0)
        overs_completed = balls_faced / 6
        current_rate = runs / overs_completed if overs_completed > 0 else 0
        required_rate = runs_needed / (balls_left / 6) if balls_left > 0 else None

        return {
            "target": target,
            "runs": runs,
            "wickets": wickets,
            "balls_faced": balls_faced,
            "balls_left": balls_left,
            "runs_needed": runs_needed,
            "total_overs": total_overs,
            "current_rate": current_rate,
            "required_rate": required_rate,
            "current_innings": current_innings,
        }
    except (KeyError, TypeError, ValueError):
        return None


# ---------- CUSTOM DESIGN ----------
st.markdown(
    """
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
        p, label, span { font-family: 'DM Sans', sans-serif; }
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
        .match-subtitle { color: #858B98; font-size: 13px; }
        .score-label { color: #858B98; font-size: 13px; }
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
        .divider { border-top: 1px solid #2A3039; margin: 22px 0; }
        .metric-card {
            background: #15191F;
            border: 1px solid #282E37;
            border-radius: 14px;
            padding: 18px;
            min-height: 105px;
            margin-bottom: 10px;
        }
        .metric-label { color: #939AA7; font-size: 12px; margin-bottom: 10px; }
        .metric-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 27px;
            font-weight: 600;
            color: #F4F5F7;
        }
        .metric-highlight { color: #D5FF65; }
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
        .feature-description { color: #9BA2AE; font-size: 13px; line-height: 1.7; }
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
        div[data-testid="stAlert"] { border-radius: 10px; }
        .footer {
            color: #626A77;
            font-size: 12px;
            text-align: center;
            padding-top: 24px;
            border-top: 1px solid #252A32;
            margin-top: 30px;
        }
        @media (max-width: 640px) {
            .block-container { padding: 1rem 1rem 2rem 1rem; }
            .match-card { padding: 18px; }
            .score-number { font-size: 28px; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HEADER ----------
header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown(
        '<div class="brand">CLUTCH<span style="color:#F4F5F7">.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="brand-subtitle">THE INTELLIGENT MATCH COMPANION</div>',
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown(
        '<div style="text-align:right;color:#858B98;font-size:12px;padding-top:12px;">'
        'LIVE DATA &nbsp; • &nbsp; CRICKET</div>',
        unsafe_allow_html=True,
    )
st.markdown("<br>", unsafe_allow_html=True)

# ---------- SELECT MATCH ----------
st.markdown('<div class="section-label">SELECT A MATCH</div>', unsafe_allow_html=True)

try:
    matches = get_cricket_matches()
except Exception as error:
    st.error(f"Could not fetch cricket matches: {error}")
    st.info(
        "Check that CRICKET_API_KEY is set in .streamlit/secrets.toml "
        "and in your Streamlit Community Cloud app secrets."
    )
    st.stop()

if not matches:
    st.info("The API did not return any matches right now.")
    st.stop()

selected_match = st.selectbox(
    "Choose a match",
    matches,
    format_func=lambda match: (
        f"{match.get('name', 'Unknown match')} — "
        f"{match.get('status', 'Status unavailable')}"
    ),
)

teams = selected_match.get("teams") or []
scores = selected_match.get("score") or []
match_name = selected_match.get("name", "Cricket match")
match_status = selected_match.get("status", "Status unavailable")
venue = selected_match.get("venue", "Venue unavailable")
match_type = str(selected_match.get("matchType", "cricket")).upper()
match_context = build_match_context(selected_match)
numbers = get_match_numbers(selected_match)

st.caption(f"**Teams:** {' vs '.join(teams) if teams else 'Not available'}")
st.caption(f"**Venue:** {venue}  ·  **Status:** {match_status}")

# ---------- MATCH CENTRE / 01 ----------
st.markdown('<div class="section-label">MATCH CENTRE / 01</div>', unsafe_allow_html=True)

if scores:
    current_score = scores[-1]
    score_runs = current_score.get("r", "?")
    score_wickets = current_score.get("w", "?")
    score_overs = current_score.get("o", "?")
    innings_name = current_score.get("inning", "Latest innings")
    score_html = f'{score_runs}<span>/{score_wickets}</span>'
else:
    innings_name = "Score unavailable"
    score_overs = "—"
    score_html = "—"

st.markdown(
    f"""
    <div class="match-card">
        <div class="match-status">● &nbsp; {match_status.upper()}</div>
        <div class="match-title">{match_name}</div>
        <div class="match-subtitle">{match_type} &nbsp; / &nbsp; {venue}</div>
        <div class="divider"></div>
        <div class="score-label">{innings_name}</div>
        <div class="score-number">{score_html}</div>
        <div class="match-subtitle">{score_overs} overs</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if scores:
    with st.expander("View all score entries from the API"):
        for score in scores:
            st.write(
                f"**{score.get('inning', 'Innings')}** — "
                f"{score.get('r', '?')}/{score.get('w', '?')} "
                f"({score.get('o', '?')} overs)"
            )
else:
    st.info("The API has not supplied score details for this match.")

# ---------- THE NUMBERS / 02 ----------
st.markdown('<div class="section-label">THE NUMBERS / 02</div>', unsafe_allow_html=True)

if numbers:
    metric_values = [
        ("TARGET", str(numbers["target"]), False),
        ("RUNS NEEDED", str(numbers["runs_needed"]), True),
        ("BALLS LEFT", str(numbers["balls_left"]), False),
    ]
    metric_columns = st.columns(3)
    for column, (label, value, highlight) in zip(metric_columns, metric_values):
        with column:
            value_class = "metric-value metric-highlight" if highlight else "metric-value"
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="{value_class}">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.info(
        "Chase metrics are unavailable for this selection. They are calculated only "
        "when the API supplies at least two innings for a T20 or ODI match."
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------- CATCH ME UP / 03 ----------
st.markdown('<div class="section-label">CATCH ME UP / 03</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="feature-card">
        <div class="feature-title">Missed the action?</div>
        <div class="feature-description">
            Get an AI explanation of the selected match using the match details and
            scores available from the API. Ball-by-ball events may not be available.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

fan_level = st.selectbox(
    "Choose how you want the match explained",
    ["Beginner", "Regular fan", "Analyst"],
    key="fan_level",
)

if st.button("⚡ Generate AI Match Story", use_container_width=True):
    system_prompt = f"""
You are Clutch, an AI cricket match companion.
The user's cricket knowledge level is {fan_level}.
- Beginner: use simple words and explain cricket terms.
- Regular fan: explain the score and what it means.
- Analyst: give tactical context only when supported by the data.
Use only the supplied match information. Do not invent events, player statistics,
partnerships, toss details, or match conditions. The available data may contain
only a score summary, not ball-by-ball commentary. State those limitations clearly.
Keep the answer concise and useful.
"""
    with st.spinner("Clutch is analysing the selected match..."):
        story = get_ai_response(
            system_prompt,
            f"Explain the current match situation using this data:\n{match_context}",
        )
    st.markdown("### 🏏 AI Match Story")
    st.markdown(story)
    st.caption("AI-generated explanation based on the match information returned by the cricket API.")

# ---------- MATCH INSIGHTS / 04 ----------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">MATCH INSIGHTS / 04</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="feature-card">
        <div class="feature-title">Understand the pressure.</div>
        <div class="feature-description">
            Explore the required run rate and current scoring rate when the selected
            match has enough limited-overs innings data.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("Analyse match situation →", use_container_width=True):
    if not numbers:
        st.warning(
            "This match does not have enough innings data to calculate a chase. "
            "Choose a T20 or ODI match with at least two score entries."
        )
    else:
        a, b = st.columns(2)
        with a:
            st.metric(
                "Required run rate",
                f'{numbers["required_rate"]:.2f}' if numbers["required_rate"] is not None else "—",
            )
        with b:
            st.metric("Current run rate", f'{numbers["current_rate"]:.2f}')

        if numbers["balls_left"] > 0:
            st.info(
                f'The chasing side needs {numbers["runs_needed"]} runs from '
                f'{numbers["balls_left"]} balls. The required rate is '
                f'{numbers["required_rate"]:.2f} runs per over, compared with a '
                f'current scoring rate of {numbers["current_rate"]:.2f}.'
            )
        elif numbers["runs_needed"] == 0:
            st.success("The target shown by the score data has been reached.")
        else:
            st.info("No balls remain in the configured limited-overs innings.")
        st.caption("This is a mathematical calculation, not a trained win-probability model.")

# ---------- WIN PREDICTOR / 05 ----------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">WIN PREDICTOR / 05</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="feature-card">
        <div class="feature-title">Explore a hypothetical chase.</div>
        <div class="feature-description">
            Change the inputs to see how required runs, overs and wickets affect
            a simple illustrative score. This is not a real win probability.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("#### Adjust a hypothetical T20 chase")

input_col1, input_col2 = st.columns(2)
with input_col1:
    current_runs = st.slider("Runs scored", min_value=0, max_value=250, value=120, step=1)
    wickets = st.slider("Wickets lost", min_value=0, max_value=10, value=4, step=1)
with input_col2:
    overs = st.slider("Completed overs", min_value=0, max_value=19, value=15, step=1)
    prediction_target = st.number_input("Target runs", min_value=1, max_value=300, value=180, step=1)

runs_remaining = max(int(prediction_target) - current_runs, 0)
balls_remaining_predictor = (20 - overs) * 6
st.markdown("---")

if current_runs >= prediction_target:
    st.success("🏆 The target has been reached in this hypothetical scenario!")
elif wickets == 10 or balls_remaining_predictor == 0:
    st.error("The hypothetical chase is over. The target was not reached.")
else:
    overs_remaining = balls_remaining_predictor / 6
    required_run_rate = runs_remaining / overs_remaining
    current_run_rate = current_runs / overs if overs > 0 else 0
    wickets_remaining = 10 - wickets

    # Manually designed heuristic only; not trained on historical matches.
    difficulty = (
        (required_run_rate * 3)
        - (wickets_remaining * 1.5)
        - (current_run_rate * 0.5)
    )
    estimated_chance = 100 / (1 + math.exp(max(-20, min(20, difficulty - 12))))
    estimated_chance = max(5, min(95, estimated_chance))

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Runs remaining", runs_remaining)
    metric2.metric("Balls remaining", balls_remaining_predictor)
    metric3.metric("Required run rate", f"{required_run_rate:.2f}")

    st.markdown("#### Illustrative chase outlook")
    st.progress(int(estimated_chance))
    st.markdown(
        f"""
        <div style="text-align:center;padding:10px;">
            <div style="font-size:42px;font-weight:700;color:#D5FF65;">
                {estimated_chance:.1f}%
            </div>
            <div style="color:#9BA2AE;font-size:13px;">
                Prototype heuristic score — not a real win probability
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if required_run_rate > 12:
        st.warning("The chase is under heavy scoring pressure: more than 12 runs per over are needed.")
    elif required_run_rate > 9:
        st.info("The scoring rate needs to increase; remaining wickets could be important.")
    else:
        st.success("The required scoring rate is relatively manageable, but match conditions still matter.")
    st.caption("Hypothetical T20 scenario. This is a manually designed heuristic, not a trained ML model.")

# ---------- ASK CLUTCH / 06 ----------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">ASK CLUTCH / 06</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="feature-card">
        <div class="feature-title">Your match. Your questions.</div>
        <div class="feature-description">
            Ask about the selected match and get an explanation tailored to your
            cricket knowledge level.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

question = st.text_input(
    "Ask a question",
    placeholder="e.g. What does this score mean?",
    key="clutch_question",
)

if st.button("Ask Clutch →", use_container_width=True):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        system_prompt = f"""
You are Clutch, an AI cricket match companion.
The user's cricket knowledge level is {fan_level}.
Answer clearly and concisely. Explain cricket terms when useful.
Use only the match information provided. Do not invent scores, events, player
statistics, or match conditions. If the data does not contain the answer,
say that it is unavailable.
"""
        with st.spinner("Clutch is thinking..."):
            answer = get_ai_response(
                system_prompt,
                f"Match information:\n{match_context}\n\nUser question:\n{question}",
            )
        st.markdown("#### 💬 Clutch's Answer")
        st.markdown(answer)
        st.caption("AI-generated answer based on the selected match's available API data.")

# ---------- FOOTER ----------
st.markdown(
    """
    <div class="footer">
        CLUTCH © 2026 &nbsp; • &nbsp; BUILT FOR THE FANS
        <br><br>
        AI-powered cricket companion. Match coverage and score details depend on API availability.
        Win predictor is an illustrative heuristic, not a real probability.
    </div>
    """,
    unsafe_allow_html=True,
)
