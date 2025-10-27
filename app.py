import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import random

# ---------- STREAMLIT PAGE CONFIG ----------
st.set_page_config(
    page_title="Hydrochaotic",   # Your app name
    page_icon="icon.png",         # Browser tab icon
    layout="centered",            # Options: "centered" or "wide"
    initial_sidebar_state="auto"  # Options: "auto", "expanded", "collapsed"
)

# ---------- CONFIG ----------
CSV_FILE = "data.csv"
DAILY_GOAL = 3000  # ml
HISTORY_DAYS = 7

# ---------- MESSAGES ----------
MESSAGES = [
    {"type":"Roast", "message":"Drink water before your organs file a complaint."},
    {"type":"Roast", "message":"Your cells are crispier than KFC."},
    {"type":"Quotes", "message":"Proud of you for hydrating (even a little)."},
    {"type":"Maths", "message":"I wouldn't mind you being dehydrated but fainting is kinda my thing 🙄"},
    {"type":"HIMYM", "message":"You’re the Barney of hydration — full of promises, no delivery."},
    {"type":"Council", "message":"🧘ye deekho chookari maar ke aapke paani peene ka intezaar."}
]

# ---------- MEMES ----------
MEMES = [
    {"url":"https://i.pinimg.com/1200x/5a/8b/0e/5a8b0e6b61977dab8509595c3998afec.jpg","caption":"relating to this isnt funny."},
    {"url":"https://i.pinimg.com/1200x/6a/dd/a7/6adda7b08880e234247df0c566b8ebc3.jpg","caption":"kiun nhin pi rhe aap paani."},
    {"url":"https://i.pinimg.com/1200x/3e/31/7f/3e317fdabd3c015819e6e096ca030e7f.jpg","caption":"You're not the only one with cameras."},
    {"url":"https://i.pinimg.com/1200x/b2/af/75/b2af75f216dd5cd75379789beff5b8a1.jpg","caption":"imagine fardan living longer than you cause he drank water and you didn't."},
    {"url":"https://i.pinimg.com/736x/37/c1/4c/37c14ca7f0d61a2a8db4788c09dd336b.jpg","caption":"me if u dont drink water."},
    {"url":"https://i.pinimg.com/736x/97/74/cd/9774cd9bd7daead2ac764adb34a0e72f.jpg","caption":"your mom if u need to go to the doc again."}
]

# ---------- HELPERS ----------
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Date", "Time", "Amount (ml)"])
        df.to_csv(CSV_FILE, index=False)
        return df
    df = pd.read_csv(CSV_FILE)
    if list(df.columns) == ["Date", "Water Intake (ml)"]:
        migrated = pd.DataFrame(columns=["Date", "Time", "Amount (ml)"])
        for _, row in df.iterrows():
            try:
                parsed = pd.to_datetime(row["Date"], errors='coerce')
                d = parsed.date() if not pd.isna(parsed) else row["Date"]
            except Exception:
                d = row["Date"]
            migrated = pd.concat(
                [migrated, pd.DataFrame([{"Date": d, "Time": "00:00:00", "Amount (ml)": row["Water Intake (ml)"]}])],
                ignore_index=True
            )
        migrated.to_csv(CSV_FILE, index=False)
        return migrated
    if "Date" not in df.columns or "Time" not in df.columns or "Amount (ml)" not in df.columns:
        df = pd.DataFrame(columns=["Date", "Time", "Amount (ml)"])
        df.to_csv(CSV_FILE, index=False)
        return df
    return df

def load_data():
    df = pd.read_csv(CSV_FILE)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time.fillna(pd.to_datetime("00:00:00").time())
    df['Amount (ml)'] = pd.to_numeric(df['Amount (ml)'], errors='coerce').fillna(0).astype(int)
    return df

def save_data(df):
    df_to_save = df.copy()
    df_to_save['Date'] = df_to_save['Date'].astype(str)
    df_to_save['Time'] = df_to_save['Time'].astype(str)
    df_to_save.to_csv(CSV_FILE, index=False)

def add_entry(amount_ml):
    now = datetime.now()
    new_row = {
        "Date": now.date(),
        "Time": now.time().replace(microsecond=0).isoformat(),
        "Amount (ml)": int(amount_ml)
    }
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    return now

def delete_entries(indices):
    df = load_data()
    if not indices:
        return False
    df = df.drop(index=indices).reset_index(drop=True)
    save_data(df)
    return True

def get_daily_total(df, target_date):
    rows = df[df['Date'] == target_date]
    return int(rows['Amount (ml)'].sum())

def get_history_aggregated(df, days=HISTORY_DAYS):
    today = date.today()
    dates = [today - timedelta(days=i) for i in range(days-1, -1, -1)]
    totals = []
    for d in dates:
        totals.append(get_daily_total(df, d))
    return dates, totals

# ---------- SESSION STATE ----------
if "refresh" not in st.session_state:
    st.session_state.refresh = 0
