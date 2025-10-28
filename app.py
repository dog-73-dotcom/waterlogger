import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import random

# ---------- CONFIG ----------
st.set_page_config(page_title="WaterYouDoing 💧", page_icon="💧", layout="centered")
CSV_FILE = "data.csv"
DAILY_GOAL = 3000  # ml
MEMES = [
    {"url": "https://i.imgur.com/VnYVYtM.png", "caption": "Hydrate or diedrate."},
    {"url": "https://i.imgur.com/Yl9rjFx.jpg", "caption": "Every sip counts."},
    {"url": "https://i.imgur.com/Dy2pVhV.jpeg", "caption": "Be the reason your kidneys smile."},
]

# ---------- DATA HANDLING ----------
def load_data():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Date", "Time", "Amount (ml)"])
        df.to_csv(CSV_FILE, index=False)
    return pd.read_csv(CSV_FILE)

def add_entry(amount_ml):
    now = datetime.now()  # using system time (GMT+0 on Streamlit Cloud)
    new_row = {
        "Date": now.date(),
        "Time": now.time().replace(microsecond=0).isoformat(),
        "Amount (ml)": int(amount_ml)
    }
    data = load_data()
    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
    data.to_csv(CSV_FILE, index=False)
    return now

def get_daily_total(data, day):
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce").dt.date
    return data[data["Date"] == day]["Amount (ml)"].sum()

# ---------- UI SETUP ----------
if "refresh" not in st.session_state:
    st.session_state.refresh = 0

st.title("💦 WaterYouDoing")
st.caption("Track your daily hydration like a pro 💧")

today = date.today()
data = load_data()
total_today = get_daily_total(data, today)
remaining = max(0, DAILY_GOAL - total_today)

st.metric(label="Today's Total", value=f"{total_today} ml", delta=f"-{remaining} ml to goal")

st.divider()

# ---------- QUICK BUTTONS ----------
quick_amounts = [250, 500]
quick_cols = st.columns(len(quick_amounts))

for idx, amt in enumerate(quick_amounts):
    with quick_cols[idx]:
        if st.button(f"+{amt} ml", key=f"quick_{amt}"):
            now = add_entry(amt)
            st.success(f"Added {amt} ml at {now.strftime('%I:%M %p')}")

            # Meme image + caption
            meme = random.choice(MEMES)
            st.image(meme['url'], use_container_width=True)
            st.markdown(
                f"<div style='text-align:center; font-size:14px; margin-top:4px;'>{meme['caption']}</div>",
                unsafe_allow_html=True
            )

            st.session_state.refresh += 1

# ---------- CUSTOM INPUT ----------
custom_amount = st.number_input("Or type amount (ml)", min_value=0, step=50, value=250)
if st.button("Add entry"):
    if custom_amount <= 0:
        st.warning("Stop trying stupid things, lil bro 😤")
    else:
        now = add_entry(custom_amount)
        st.success(f"Added {custom_amount} ml at {now.strftime('%I:%M %p')}")
        data = load_data()
        total_today = get_daily_total(data, date.today())
        if total_today >= DAILY_GOAL:
            st.success("🎉 HYDRATION SUPREMACY! You hit today's goal!")

# ---------- VIEW & DELETE BLOCK ----------
st.divider()
st.subheader(f"Logs for {today.isoformat()}")

data = load_data()
today_data = data[pd.to_datetime(data["Date"], errors="coerce").dt.date == today].copy()

if not today_data.empty:
    today_data_display = today_data.reset_index().rename(columns={"index": "row_index"})
    today_data_display["ID"] = today_data_display["row_index"] + 1
    st.dataframe(today_data_display[["ID", "Time", "Amount (ml)"]], use_container_width=True)

    delete_id = st.number_input("Delete entry ID", min_value=1, max_value=len(today_data_display), step=1)
    if st.button("Delete"):
        idx_to_drop = today_data_display.loc[today_data_display["ID"] == delete_id, "row_index"].values[0]
        data.drop(index=idx_to_drop, inplace=True)
        data.to_csv(CSV_FILE, index=False)
        st.success(f"Deleted entry #{delete_id}")
        st.session_state.refresh += 1
else:
    st.info("No entries yet for today. Drink some water, legend 💧")

# ---------- FOOTER ----------
st.divider()
st.caption("Made with 💙 and hydration by WaterYouDoing")
