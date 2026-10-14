"""
app.py - Polished, High-Contrast Light & Dark Mode Dashboard for EventRank
"""

from datetime import date
import streamlit as st
from ranking import load_events, rank_events

# 1. Page Configuration
st.set_page_config(
    page_title="EventRank | Student Opportunities",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Adaptive CSS (Guarantees Sharp Contrast in Both Light and Dark Themes)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1250px;
    }

    /* Base Fallback / Dark Variables */
    :root {
        --card-bg: #1e293b;
        --card-border: #334155;
        --card-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        --accent-blue: #38bdf8;
        --color-heading: #f8fafc;
        --color-body: #cbd5e1;
        --color-subtle: #94a3b8;
    }

    /* Light Theme Adaptive Mode (Triggered by Streamlit's Light Theme) */
    @media (prefers-color-scheme: light) {
        :root {
            --card-bg: #ffffff;
            --card-border: #e2e8f0;
            --card-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
            --accent-blue: #2563eb;
            --color-heading: #0f172a;
            --color-body: #334155;
            --color-subtle: #64748b;
        }
    }

    /* Explicit Streamlit App Light Mode Hook */
    [data-theme="light"], .stApp[data-test="stApp"] {
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
        --card-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
        --accent-blue: #2563eb;
        --color-heading: #0f172a;
        --color-body: #334155;
        --color-subtle: #64748b;
    }

    /* Explicit Streamlit App Dark Mode Hook */
    [data-theme="dark"] {
        --card-bg: #1e293b;
        --card-border: #334155;
        --card-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        --accent-blue: #38bdf8;
        --color-heading: #f8fafc;
        --color-body: #cbd5e1;
        --color-subtle: #94a3b8;
    }

    /* Header Title */
    .dashboard-header {
        margin-bottom: 1.5rem;
    }
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #2563eb 50%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-sub {
        color: var(--color-subtle);
        font-size: 0.95rem;
        margin-top: 0.2rem;
    }

    /* KPI Summary Row */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: var(--card-shadow);
    }
    .kpi-icon {
        font-size: 1.8rem;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--color-heading);
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--color-subtle);
    }

    /* 3-Column Card Layout */
    .opp-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.4rem;
        margin-bottom: 0.6rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 250px;
        box-shadow: var(--card-shadow);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .opp-card:hover {
        transform: translateY(-3px);
        border-color: #6366f1;
    }

    /* Pill Badges */
    .badge-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
    }
    .type-pill {
        font-size: 0.72rem;
        font-weight: 800;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .pill-hackathon { background: rgba(239, 68, 68, 0.15); color: #dc2626; border: 1px solid rgba(239, 68, 68, 0.3); }
    .pill-internship { background: rgba(16, 185, 129, 0.15); color: #059669; border: 1px solid rgba(16, 185, 129, 0.3); }
    .pill-competition { background: rgba(245, 158, 11, 0.15); color: #d97706; border: 1px solid rgba(245, 158, 11, 0.3); }
    .pill-webinar { background: rgba(14, 165, 233, 0.15); color: #0284c7; border: 1px solid rgba(14, 165, 233, 0.3); }

    .score-accent {
        font-size: 1.2rem;
        font-weight: 800;
        color: var(--accent-blue);
    }
    .score-accent-sub {
        font-size: 0.7rem;
        color: var(--color-subtle);
        text-align: right;
        display: block;
        margin-top: -2px;
        font-weight: 600;
    }

    .opp-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--color-heading);
        margin: 0.3rem 0 0.7rem 0;
        line-height: 1.35;
    }

    .opp-details {
        font-size: 0.86rem;
        color: var(--color-body);
        margin: 0;
        line-height: 1.6;
    }
    .opp-details b {
        color: var(--color-heading);
    }

    .opp-footer {
        border-top: 1px solid var(--card-border);
        padding-top: 0.8rem;
        margin-top: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
        color: var(--color-subtle);
    }
</style>
""", unsafe_allow_html=True)

# 3. Load & Cache Dataset
@st.cache_data
def get_cached_events():
    return load_events("events.csv")

try:
    events = get_cached_events()
except Exception as e:
    st.error(f"Error loading events dataset: {e}")
    st.stop()

# 4. Sidebar Controls
st.sidebar.markdown("### 🔍 Personalized Filtering")
st.sidebar.markdown("Filter opportunities based on your track, availability, and target city.")

type_options = ["All Types", "Hackathon", "Internship", "Competition", "Webinar/Seminar"]
selected_type = st.sidebar.selectbox("Opportunity Type", type_options)

domain_options = ["Any", "AI/ML", "Cybersecurity", "Python", "Web Development", "Data Science", "Cloud Computing", "Open Source"]
selected_domain = st.sidebar.selectbox("Technology Track", domain_options)

skill_options = ["Any", "Beginner", "Intermediate", "Advanced"]
selected_skill = st.sidebar.selectbox("Required Skill Level", skill_options)

mode_options = ["Any", "Online", "Offline"]
selected_mode = st.sidebar.selectbox("Attendance Mode", mode_options)

location_input = st.sidebar.text_input("City Target (Offline Only)", "", placeholder="e.g. Bengaluru, Delhi, Mumbai")

max_budget = st.sidebar.slider("Maximum Fee Limit (₹ INR)", min_value=0, max_value=2000, value=1000, step=100)

team_size = st.sidebar.slider("Minimum Team Size Limit", min_value=1, max_value=5, value=1, help="Select 1 for Solo/Internships/Webinars, 2+ for teams.")

st.sidebar.markdown("---")
st.sidebar.caption("⚖️ **Scoring Weights:** Bayesian Trust Rating (35%), Preferences Fit (25%), Career Value (25%), Review Reliability (10%), Affordability (5%).")

# 5. Execute Ranking Pipeline
demo_date = date(2026, 10, 1)

preferences = {
    "opportunity_type": None if selected_type == "All Types" else selected_type,
    "domain": None if selected_domain == "Any" else selected_domain,
    "skill_level": None if selected_skill == "Any" else selected_skill,
    "mode": None if selected_mode == "Any" else selected_mode,
    "location": location_input.strip() if location_input.strip() else None,
    "max_budget": max_budget,
    "team_size": team_size,
}

results = rank_events(events, preferences, reference_date=demo_date)

# 6. Dashboard Header
st.markdown("""
<div class="dashboard-header">
    <h1 class="brand-title">EventRank</h1>
    <div class="brand-sub">Exploration panel for hackathons, tech internships, competitive coding, and webinars.</div>
</div>
""", unsafe_allow_html=True)

# 7. Summary Stats Row
kpi_total = len(results)
kpi_free = sum(1 for e in results if e["fee"] == 0)
kpi_online = sum(1 for e in results if e["mode"] == "Online")
kpi_avg = round(sum(e["final_score"] for e in results) / len(results), 1) if results else 0.0

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-icon">📅</div>
        <div>
            <div class="kpi-value">{kpi_total}</div>
            <div class="kpi-label">Matches Found</div>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">💜</div>
        <div>
            <div class="kpi-value">{kpi_free}</div>
            <div class="kpi-label">Free Entry</div>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">🌐</div>
        <div>
            <div class="kpi-value">{kpi_online}</div>
            <div class="kpi-label">Remote / Online</div>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">📈</div>
        <div>
            <div class="kpi-value">{kpi_avg}%</div>
            <div class="kpi-label">Avg Match Score</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Top Opportunities For You")
st.markdown("<p style='color: var(--color-subtle); font-size: 0.85rem; margin-top: -0.6rem; margin-bottom: 1.2rem;'>Ranked by relevance, trust metrics, and profile fit.</p>", unsafe_allow_html=True)

def get_pill_class(opp_type: str) -> str:
    mapping = {
        "Hackathon": "pill-hackathon",
        "Internship": "pill-internship",
        "Competition": "pill-competition",
        "Webinar/Seminar": "pill-webinar",
    }
    return mapping.get(opp_type, "pill-hackathon")

# 8. Render Results in a 3-Column Responsive Grid
if not results:
    st.warning("🔎 No matching opportunities found. Try selecting 'All Types' or increasing your budget limit.")
else:
    # 3-column layout
    col_count = 3
    cols = st.columns(col_count)

    for idx, item in enumerate(results, start=1):
        target_col = cols[(idx - 1) % col_count]
        fee_label = "FREE" if item["fee"] == 0 else f"₹{int(item['fee'])}"
        p_class = get_pill_class(item["opportunity_type"])

        with target_col:
            # Render card
            st.markdown(f"""
            <div class="opp-card">
                <div>
                    <div class="badge-bar">
                        <span class="type-pill {p_class}">{item['opportunity_type']}</span>
                        <div>
                            <span class="score-accent">{item['final_score']}%</span>
                            <span class="score-accent-sub">Match Score</span>
                        </div>
                    </div>
                    <h4 class="opp-title">{item['title']}</h4>
                    <p class="opp-details">
                        Track: <b>{item['domain']}</b><br>
                        Level: <b>{item['skill_level']}</b><br>
                        Format: <b>{item['mode']}</b> ({item['location']})<br>
                        Feedback: <span style="color: #d97706; font-weight:700;">★ {item['average_rating']}</span> ({item['review_count']} reviews)
                    </p>
                </div>
                <div class="opp-footer">
                    <div>📅 <b>{item['registration_deadline']}</b></div>
                    <div style="font-weight: 700; color: #059669;">{fee_label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Interactive Score Breakdown & Justification
            with st.expander(f"⚙️ Details & Why #{idx}"):
                st.markdown("**💡 Match Justification:**")
                for reason in item["reasons"]:
                    st.markdown(f"- ✅ {reason}")

                st.markdown("**📈 Scoring Factors:**")
                bd = item["score_breakdown"]
                st.progress(bd["rating_score"] / 100, text=f"Trust Rating (35%): {bd['rating_score']}%")
                st.progress(bd["preference_score"] / 100, text=f"Preference Fit (25%): {bd['preference_score']}%")
                st.progress(bd["learning_score"] / 100, text=f"Career Value (25%): {bd['learning_score']}%")
                st.progress(bd["review_confidence"] / 100, text=f"Review Volume (10%): {bd['review_confidence']}%")
                st.progress(bd["affordability_score"] / 100, text=f"Affordability (5%): {bd['affordability_score']}%")