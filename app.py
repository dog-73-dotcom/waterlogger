import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import random
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

# ---------- CSS FOR BUTTONS ----------
st.markdown("""
<style>
div.stButton > button {
    min-width: 90px;
    padding: 8px 0px;
    font-size: 16px;
    margin: 2px 0px;
}
.custom-box {
    background-color: #f5faff;
    color: black;
    padding: 10px;
    border-radius: 8px;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.set_page_config(page_title="HydroChaotic 💧", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px;">
  <div style="font-size:28px;">💧</div>
  <div style="font-size:30px; font-weight:600;">WaterYouDoing</div>
</div>
""", unsafe_allow_html=True)

init_csv()
data = load_data()

# Sidebar
with st.sidebar:
    st.header("Random stuff you dont need to worry about.")
    st.write("Daily goal:", f"**{DAILY_GOAL} ml**")
    reminder_toggle = st.checkbox("Enable in-app reminders while app is open", value=False)
    reminder_interval = st.number_input("Reminder interval (minutes)", min_value=1, max_value=1440, value=60)
    st.markdown("---")
    st.write("Theme:")
    theme_choice = st.radio("", ["Funny & chaotic", "Minimal & calm"], index=0)

# Columns layout rebalanced
col1, col2 = st.columns([1.5,1])

with col1:
    st.subheader("Add water intake")

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
                st.markdown(f"<div style='text-align:center; font-size:14px; margin-top:4px;'>{meme['caption']}</div>", unsafe_allow_html=True)


                st.session_state.refresh +=1

    # ---------- CUSTOM INPUT ----------
    custom_amount = st.number_input("Or type amount (ml)", min_value=0, step=50, value=250)
    if st.button("Add entry"):
        if custom_amount <= 0:
            st.warning("Stop trying stupid things, lil bro")
        else:
            now = add_entry(custom_amount)
            st.success(f"Added {custom_amount} ml at {now.strftime('%I:%M %p')}")
            data = load_data()
            total_today = get_daily_total(data, date.today())
            if total_today >= DAILY_GOAL:
                st.success("🎉 HYDRATION SUPREMACY! You hit today's goal!")

            # Meme + caption
            meme = random.choice(MEMES)
            st.image(meme['url'], use_container_width=True)
            st.markdown(f"<div style='text-align:center; font-size:14px; margin-top:4px;'>{meme['caption']}</div>", unsafe_allow_html=True)

            # Separate message
            msg = random.choice(MESSAGES)
            st.markdown(f"<div class='custom-box'>{msg['message']}</div>", unsafe_allow_html=True)

            st.session_state.refresh +=1

    st.markdown("---")
    view_date = st.date_input("View date", value=date.today(), key="view_date")

    # ---------- VIEW & DELETE BLOCK ----------
    st.subheader(f"Logs for {view_date.isoformat()}")
    data = load_data()
    view_df = data[data['Date'] == view_date].copy()
    if not view_df.empty:
        view_df_display = view_df.reset_index().rename(columns={"index":"row_index"})
        view_df_display["ID"] = view_df_display["row_index"] + 1
        view_df_display["Time"] = view_df_display["Time"].apply(lambda t: datetime.strptime(str(t), "%H:%M:%S").strftime("%I:%M %p"))
        st.dataframe(view_df_display[["ID","Time","Amount (ml)"]], use_container_width=True)

        to_delete_id = st.multiselect("Select rows to delete (ID)", options=list(view_df_display["ID"]))
        real_to_delete = [view_df_display.loc[view_df_display["ID"]==row,"row_index"].values[0] for row in to_delete_id]

        if st.button("Delete selected"):
            if real_to_delete:
                delete_entries(real_to_delete)
                st.success("Deleted selected entries.")
                st.session_state.refresh +=1
            else:
                st.warning("Pick at least one row to delete.")
    else:
        st.write("No entries for this date yet. Add one above!")

with col2:
    st.subheader("Imagine not drinking water.")
    total_today = get_daily_total(data, view_date)
    st.write(f"Total for {view_date.isoformat()}: **{total_today} ml**")
    progress_val = min(total_today/DAILY_GOAL,1.0)
    st.progress(progress_val)
    st.write(f"{int(progress_val*100)}% of {DAILY_GOAL} ml")

    st.markdown("---")
    dates, totals = get_history_aggregated(data,HISTORY_DAYS)
    chart_df = pd.DataFrame({"date":[d.isoformat() for d in dates],"total":totals})
    st.write("Last week of cat's water rehab:")
    st.bar_chart(chart_df.set_index("date")["total"])

    st.markdown("---")
    st.subheader("Ominous motivation.")
    st.write("Your drinking habits are not up to the mark.")
    if theme_choice=="Funny & chaotic":
        meme = random.choice(MEMES)
        st.image(meme['url'], use_container_width=True)
        st.markdown(f"<div style='text-align:center; font-size:14px; margin-top:4px;'>{meme['caption']}</div>", unsafe_allow_html=True)

        msg = random.choice(MESSAGES)
        st.markdown(f"<div class='custom-box'>{msg['message']}</div>", unsafe_allow_html=True)
    else:
        calm_msgs = [
            "Small steps — sip-by-sip.",
            "Consistency > intensity.",
            "One glass at a time."
        ]
        st.markdown(f"<div class='custom-box'>{random.choice(calm_msgs)}</div>", unsafe_allow_html=True)

st.markdown("---")
if st.checkbox("Show raw data (CSV)"):
    st.dataframe(load_data(), use_container_width=True)



