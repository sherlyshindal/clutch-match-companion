
import html
import re
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

def parse_score(score_text, team_name):
    """Keep each team's score, even if it cannot be parsed numerically."""

    if not score_text:
        return None

    text = str(score_text).strip()

    pattern = r"(\d+)\s*/\s*(\d+)(?:\s*\(([\d.]+)\))?"
    result = re.search(pattern, text)

    if result:
        return {
            "team": team_name,
            "raw": text,
            "r": int(result.group(1)),
            "w": int(result.group(2)),
            "o": result.group(3) or "?",
        }

    return {
        "team": team_name,
        "raw": text,
        "r": None,
        "w": None,
        "o": None,
    }


@st.cache_data(ttl=60)
def get_cricket_matches():
    """Fetch matches from CricketData."""

    api_key = st.secrets.get("CRICKET_API_KEY")

    if not api_key:
        raise ValueError("CRICKET_API_KEY is missing from secrets.")

    response = requests.get(
        "https://api.cricapi.com/v1/cricScore",
        params={"apikey": api_key},
        timeout=20,
    )

    response.raise_for_status()
    result = response.json()

    if result.get("status") != "success":
        raise ValueError(result.get("reason", "Cricket API error"))

    matches = []

    for raw in result.get("data", []):

        team1 = raw.get("t1") or "Team 1"
        team2 = raw.get("t2") or "Team 2"

        match_state = str(raw.get("ms", "")).lower()

        scores = []

        score1 = parse_score(raw.get("t1s"), team1)
        score2 = parse_score(raw.get("t2s"), team2)

        if score1:
            scores.append(score1)

        if score2:
            scores.append(score2)

        matches.append({
            "id": raw.get("id"),
            "name": f"{team1} vs {team2}",
            "teams": [team1, team2],
            "status": raw.get("status", "Status unavailable"),
            "ms": match_state,
            "matchStarted": match_state == "live",
            "matchEnded": match_state == "result",
            "matchType": raw.get("matchType", "Cricket"),
            "venue": raw.get("venue", "Venue unavailable"),
            "dateTimeGMT": raw.get("dateTimeGMT", ""),
            "series": raw.get("series", ""),
            "score": scores,
        })

    return matches


def classify_match(match):
    """Classify matches using the API's match-state field."""

    state = str(match.get("ms", "")).lower()

    if state == "live":
        return "live"

    if state == "fixture":
        return "upcoming"

    if state == "result":
        return "completed"

    status = str(match.get("status", "")).lower()

    if match.get("matchEnded"):
        return "completed"

    if match.get("matchStarted"):
        return "live"

    if any(word in status for word in (
        "won by", "draw", "no result", "abandoned",
        "match tied", "completed"
    )):
        return "completed"

    if any(word in status for word in (
        "not started", "upcoming", "scheduled", "starts at"
    )):
        return "upcoming"

    return "unknown"


# ---------- AI HELPERS ----------

def build_match_context(match):

    teams = match.get("teams", [])
    scores = match.get("score", [])

    lines = [
        f"Match: {match.get('name', 'Unknown')}",
        f"Teams: {', '.join(teams)}",
        f"Match type: {match.get('matchType', 'Unknown')}",
        f"Status: {match.get('status', 'Unknown')}",
        f"Series: {match.get('series', 'Not available')}",
        f"Venue: {match.get('venue', 'Not available')}",
        f"Date: {match.get('dateTimeGMT', 'Not available')}",
    ]

    if scores:
        lines.append("Available team scores:")

        for score in scores:
            lines.append(
                f"{score['team']}: {score['raw']}"
            )
    else:
        lines.append("No score details are currently available.")

    lines.append(
        "Only match metadata and score summaries are available. "
        "Do not invent ball-by-ball events, player statistics, "
        "partnerships, toss details or match conditions. "
        "If information is missing, clearly say it is unavailable."
    )

    return "\n".join(lines)


def get_ai_response(system_prompt, user_prompt):

    try:
        api_key = st.secrets.get("GROQ_API_KEY")

        if not api_key:
            return "GROQ_API_KEY is missing from Streamlit secrets."

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

        return (
            response.choices[0].message.content
            or "Clutch couldn't generate a response."
        )

    except Exception as error:
        return f"Request failed: {error}"


# ---------- CUSTOM DESIGN ----------

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        :root {
            --bg: #0B0D10;
            --panel: #15191F;
            --border: #2A3039;
            --text: #F4F5F7;
            --muted: #9299A6;
            --accent: #D5FF65;
        }

        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        button[data-testid="stDeployButton"] {
            display: none;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
            font-family: 'DM Sans', sans-serif;
        }

        .block-container {
            max-width: 1100px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3, h4 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: var(--text) !important;
        }

        .brand {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 29px;
            font-weight: 700;
            letter-spacing: -1.5px;
            color: var(--accent);
        }

        .brand-subtitle {
            color: var(--muted);
            font-size: 11px;
            letter-spacing: 1.6px;
            margin-top: 5px;
        }

        .section-label {
            color: #A1A7B2;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin: 22px 0 10px 0;
        }

        .match-card {
            background: linear-gradient(135deg, #191D24, #12151A);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 21px;
            margin: 8px 0 16px 0;
        }

        .match-status {
            color: var(--accent);
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.4px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }

        .match-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 21px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--text);
        }

        .match-subtitle {
            color: var(--muted);
            font-size: 12px;
        }

        .divider {
            border-top: 1px solid var(--border);
            margin: 17px 0;
        }

        .score-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }

        .score-row:last-child {
            border-bottom: none;
        }

        .team-name {
            color: #D7DBE2;
            font-size: 13px;
            font-weight: 500;
        }

        .team-score {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 23px;
            font-weight: 700;
            color: #FFFFFF;
            text-align: right;
        }

        .score-unavailable {
            color: var(--muted);
            font-size: 13px;
        }

        .feature-card {
            background: var(--panel);
            border: 1px solid #282E37;
            border-radius: 13px;
            padding: 17px;
            margin: 8px 0 12px 0;
        }

        .feature-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 17px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--text);
        }

        .feature-description {
            color: #9BA2AE;
            font-size: 12px;
            line-height: 1.6;
        }

        div.stButton > button {
            background: var(--accent);
            color: #10130B;
            border: none;
            border-radius: 8px;
            font-weight: 700;
            min-height: 38px;
            padding: 0.35rem 1rem;
        }

        div.stButton > button:hover {
            background: #C3EE54;
            color: #10130B;
            border: none;
        }

        div[data-testid="stAlert"] {
            border-radius: 9px;
        }

        div[role="radiogroup"] {
            gap: 10px;
            margin: 8px 0 16px 0;
        }

        div[role="radiogroup"] label {
            background: #191D24;
            border: 1px solid #2A3039;
            border-radius: 9px;
            padding: 7px 15px;
        }

        div[role="radiogroup"] label:hover {
            border-color: var(--accent);
        }

        .footer {
            color: #626A77;
            font-size: 11px;
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #252A32;
            margin-top: 26px;
        }

        @media (max-width: 640px) {
            .block-container {
                padding: 1rem 1rem 2rem 1rem;
            }

            .match-card {
                padding: 16px;
            }

            .team-score {
                font-size: 19px;
            }
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
        '<div style="text-align:right;color:#858B98;font-size:11px;padding-top:10px;">'
        'CRICKET&nbsp;&nbsp;·&nbsp;&nbsp;MATCH CENTRE</div>',
        unsafe_allow_html=True,
    )


# ---------- FETCH MATCHES ----------

try:
    matches = get_cricket_matches()

except Exception as error:

    st.error(f"Could not fetch matches: {error}")

    st.info(
        "Check CRICKET_API_KEY in your local secrets.toml "
        "and Streamlit Community Cloud secrets."
    )

    st.stop()


if not matches:
    st.info("No matches were returned by the cricket API.")
    st.stop()


# ---------- CATEGORISE MATCHES ----------

live_matches = []
upcoming_matches = []
completed_matches = []
unclassified_matches = []

for match in matches:

    category = classify_match(match)

    if category == "live":
        live_matches.append(match)

    elif category == "upcoming":
        upcoming_matches.append(match)

    elif category == "completed":
        completed_matches.append(match)

    else:
        unclassified_matches.append(match)


# ---------- MATCH NAVIGATION ----------

active_tab = st.radio(
    "Match category",
    ["Live", "Upcoming", "Completed"],
    horizontal=True,
    label_visibility="collapsed",
    key="active_match_tab",
)

category_map = {
    "Live": (live_matches, "LIVE"),
    "Upcoming": (upcoming_matches, "UPCOMING"),
    "Completed": (completed_matches, "COMPLETED"),
}

active_matches, selected_category = category_map[active_tab]

st.markdown(
    f'<div class="section-label">{active_tab.upper()} MATCHES · {len(active_matches)}</div>',
    unsafe_allow_html=True,
)

if not active_matches:

    if unclassified_matches:
        st.caption(
            f"{len(unclassified_matches)} match(es) have an unclear API status."
        )

    st.info(
        f"No {active_tab.lower()} matches are currently available from the API."
    )

    st.stop()


selected_match = st.selectbox(
    "Select match",
    active_matches,
    format_func=lambda match: (
        f"{match.get('name', 'Unknown match')} — "
        f"{match.get('status', 'Status unavailable')}"
    ),
    key=f"{active_tab.lower()}_match_picker",
)


# ---------- SELECTED MATCH DATA ----------

teams = selected_match.get("teams", [])
scores = selected_match.get("score", [])

match_name = selected_match.get("name", "Cricket match")
match_status = selected_match.get("status", "Status unavailable")
venue = selected_match.get("venue", "Venue unavailable")
match_type = str(selected_match.get("matchType", "Cricket")).upper()
series = selected_match.get("series", "")
match_date = selected_match.get("dateTimeGMT", "")

match_context = build_match_context(selected_match)


if series:
    st.caption(f"Series: {series}")


# ---------- MATCH CENTRE ----------

st.markdown(
    '<div class="section-label">MATCH CENTRE</div>',
    unsafe_allow_html=True,
)

score_rows_html = ""

for score in scores:

    team = html.escape(str(score.get("team", "Team")))
    raw_score = html.escape(str(score.get("raw", "Score unavailable")))

    score_rows_html += f"""
    <div class="score-row">
        <div class="team-name">{team}</div>
        <div class="team-score">{raw_score}</div>
    </div>
    """


if not score_rows_html:
    score_rows_html = """
    <div class="score-unavailable">
        Score details are not available for this match yet.
    </div>
    """

match_card_html = f"""
<div class="match-card">
    <div class="match-status">
        ● &nbsp; {html.escape(selected_category)} &nbsp; · &nbsp;
        {html.escape(str(match_status).upper())}
    </div>

    <div class="match-title">{html.escape(str(match_name))}</div>

    <div class="match-subtitle">
        {html.escape(match_type)} &nbsp; / &nbsp;
        {html.escape(str(venue))}
    </div>

    <div class="divider"></div>

    {score_rows_html}
</div>
"""

st.html(match_card_html)


if match_date:
    st.caption(f"Scheduled / recorded time (GMT): {match_date}")


# ---------- MATCH SUMMARY ----------

st.markdown(
    '<div class="section-label">MATCH SUMMARY</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="feature-card">
        <div class="feature-title">Get the match at a glance</div>
        <div class="feature-description">
            Understand the score and match situation without going through
            every detail.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

fan_level = st.selectbox(
    "Explanation level",
    ["Beginner", "Regular fan", "Analyst"],
    key="fan_level",
)


if st.button("Generate Match Summary", key="summary_button"):

    system_prompt = f"""
You are Clutch, a cricket match companion.

The user's cricket knowledge level is {fan_level}.

Beginner: explain cricket terms in simple language.
Regular fan: explain the score and match situation.
Analyst: provide tactical context only when supported by the data.

Use only the supplied match information.
Do not invent events, player statistics, partnerships, toss details,
or match conditions.

If the available data is insufficient, say so clearly.

Keep the answer concise, useful and easy to understand.
"""

    with st.spinner("Preparing match summary..."):

        story = get_ai_response(
            system_prompt,
            f"Explain this match using the available information:\n{match_context}",
        )

    st.markdown("#### Match Summary")
    st.markdown(story)

    st.caption("Based on match information returned by the cricket API.")


# ---------- ASK CLUTCH ----------

st.markdown(
    '<div class="section-label">ASK CLUTCH</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="feature-card">
        <div class="feature-title">Have a question about the match?</div>
        <div class="feature-description">
            Ask Clutch to explain the score, match status or available cricket details.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

question = st.text_input(
    "Your question",
    placeholder="e.g. What does this score mean?",
    key="clutch_question",
)


if st.button("Ask Clutch", key="ask_button"):

    if not question.strip():

        st.warning("Enter a question first.")

    else:

        system_prompt = f"""
You are Clutch, a cricket match companion.

The user's cricket knowledge level is {fan_level}.

Answer clearly and concisely.
Explain cricket terms when useful.

Use only the match information provided.
Do not invent scores, events, player statistics or match conditions.

If the data does not contain the answer, say that it is unavailable.
"""

        with st.spinner("Clutch is thinking..."):

            answer = get_ai_response(
                system_prompt,
                f"Match information:\n{match_context}\n\n"
                f"User question:\n{question}",
            )

        st.markdown("#### Clutch's Answer")
        st.markdown(answer)

        st.caption(
            "Answer based on the selected match's available API data."
        )


# ---------- FOOTER ----------

st.markdown(
    """
    <div class="footer">
        CLUTCH © 2026 &nbsp; · &nbsp; BUILT FOR THE FANS
        <br><br>
        Match coverage depends on cricket API availability.
        AI responses are based on available match data.
    </div>
    """,
    unsafe_allow_html=True,
)
