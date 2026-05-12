import streamlit as st
import pandas as pd
import requests
import random
from datetime import date, datetime

# Backend base URL
API_URL = "https://ueba-backend.onrender.com"   # update if needed

st.set_page_config(
    page_title="UEBA Dashboard",
    layout="wide"
)

st.title("UEBA Insider Risk Dashboard")

# ============================
# DATE SELECTOR
# ============================
selected_date = st.date_input("Select date", value=date.today())
date_str = selected_date.isoformat()

st.write(f"Showing data for: **{date_str}**")

# ============================
# RUN SCORING JOB
# ============================
if st.button("Run scoring job for this date"):
    resp = requests.post(f"{API_URL}/jobs/score/{date_str}")
    if resp.status_code == 200:
        st.success(f"Scoring job completed: {resp.json()}")
    else:
        st.error("Failed to run scoring job")

st.markdown("---")

# ============================
# HIGH-RISK USERS
# ============================
st.subheader("High-risk users")

min_score = st.slider("Minimum risk score", min_value=0, max_value=100, value=70)

params = {"date": date_str, "min_score": min_score}
resp = requests.get(f"{API_URL}/alerts/high-risk", params=params)

if resp.status_code == 200:
    data = resp.json()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        # User selection
        user_ids = df["user_id"].unique().tolist()
        selected_user = st.selectbox("Inspect user", user_ids)

        if selected_user:
            score_resp = requests.get(
                f"{API_URL}/score/user/{selected_user}",
                params={"date": date_str}
            )
            if score_resp.status_code == 200:
                score_data = score_resp.json()
                st.markdown("### User risk details")
                col1, col2, col3 = st.columns(3)
                col1.metric("User ID", score_data["user_id"])
                col2.metric("Risk score", f"{score_data['risk_score']:.1f}")
                col3.metric("Risk level", score_data["risk_level"].upper())
    else:
        st.info("No high-risk users for this date and threshold.")
else:
    st.error("Could not fetch high-risk users. Is the API running?")

# ============================
# GENERATE SAMPLE EVENTS
# ============================
st.subheader("Generate sample UEBA events")

if st.button("Generate sample UEBA events"):
    users = ["alice", "bob", "charlie", "david", "eve"]
    event_types = ["login", "file_access", "email_send", "process_start"]
    countries = ["US", "CA", "UK", "DE", "IN"]
    resources = [
        "\\\\server\\finance\\budget.xlsx",
        "\\\\server\\hr\\employees.csv",
        "\\\\server\\engineering\\design.docx",
        "\\\\server\\legal\\contracts.pdf"
    ]

    generated = 0

    for _ in range(50):
        user = random.choice(users)
        event_type = random.choice(event_types)
        country = random.choice(countries)
        resource = random.choice(resources)

        # FIXED: timestamp must be ISO8601 without trailing Z
        timestamp = f"{date_str}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00"

        event = {
            "timestamp": timestamp,
            "user_id": user,
            "entity_id": f"laptop-{random.randint(1,50)}",
            "event_type": event_type,
            "source_ip": f"10.0.{random.randint(0,255)}.{random.randint(1,254)}",
            "geo_country": country,
            "resource": resource,
            "event_metadata": {
                "action": "read" if event_type == "file_access" else "execute",
                "sensitivity": random.choice(["low", "medium", "high"])
            }
        }

        resp = requests.post(f"{API_URL}/events", json=event)
        if resp.status_code == 200:
            generated += 1

    st.success(f"Generated {generated} sample events for {date_str}")
