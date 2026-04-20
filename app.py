import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(
    page_title="ExpenseIQ Pro",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------
# PREMIUM CSS UI
# --------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a, #111827, #1e293b);
    color: white;
}

section[data-testid="stSidebar"] {
    background: rgba(17, 24, 39, 0.95);
    border-right: 1px solid rgba(255,255,255,0.08);
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
    margin-bottom: 0px;
}

.sub-title {
    color: #94a3b8;
    margin-top: -10px;
    margin-bottom: 20px;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.06);
}

.metric-label {
    color: #94a3b8;
    font-size: 14px;
}

.metric-value {
    font-size: 30px;
    font-weight: 700;
    color: white;
}

.stButton>button {
    background: linear-gradient(90deg,#3b82f6,#8b5cf6);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
}

.stButton>button:hover {
    transform: scale(1.02);
}

div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------
# DATABASE
# --------------------------------
conn = sqlite3.connect("expenseiq.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS expenses(
id INTEGER PRIMARY KEY AUTOINCREMENT,
dt TEXT,
category TEXT,
note TEXT,
amount REAL
)
""")
conn.commit()

# --------------------------------
# FUNCTIONS
# --------------------------------
def load_data():
    return pd.read_sql_query(
        "SELECT * FROM expenses ORDER BY dt DESC",
        conn
    )

def add_expense(dt, cat, note, amt):
    c.execute(
        "INSERT INTO expenses(dt,category,note,amount) VALUES(?,?,?,?)",
        (dt, cat, note, amt)
    )
    conn.commit()

# --------------------------------
# SIDEBAR
# --------------------------------
st.sidebar.markdown("## 💸 ExpenseIQ Pro")
st.sidebar.caption("Smart Personal Finance Manager")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Expense", "Transactions", "AI Insights"]
)

st.sidebar.markdown("---")
st.sidebar.info("Built with Python + Streamlit")

# --------------------------------
# HEADER
# --------------------------------
st.markdown('<p class="main-title">💸 ExpenseIQ Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Track smarter. Save better. Grow faster.</p>', unsafe_allow_html=True)

df = load_data()

# --------------------------------
# DASHBOARD
# --------------------------------
if page == "Dashboard":

    total = df["amount"].sum() if not df.empty else 0

    month = pd.Timestamp.today().strftime("%Y-%m")
    monthly = df[df["dt"].str.startswith(month)]["amount"].sum() if not df.empty else 0

    avg = df["amount"].mean() if not df.empty else 0

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("💰 Total Spend", f"₹{total:,.0f}")

    with c2:
        st.metric("📅 This Month", f"₹{monthly:,.0f}")

    with c3:
        st.metric("📈 Average Expense", f"₹{avg:,.0f}")

    st.markdown("## 📊 Analytics")

    if not df.empty:

        col1, col2 = st.columns(2)

        with col1:
            pie = px.pie(
                df,
                names="category",
                values="amount",
                hole=0.60
            )
            pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )
            st.plotly_chart(pie, use_container_width=True)

        with col2:
            line = df.groupby("dt", as_index=False)["amount"].sum()

            fig = px.line(
                line,
                x="dt",
                y="amount",
                markers=True
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No expenses found. Add transactions first.")

# --------------------------------
# ADD EXPENSE
# --------------------------------
elif page == "Add Expense":

    st.markdown("## ➕ Add New Expense")

    with st.form("expense_form"):

        col1, col2 = st.columns(2)

        dt = col1.date_input("Date", value=date.today())

        cat = col2.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Bills", "Health", "Education", "Other"]
        )

        note = st.text_input("Description")

        amt = st.number_input(
            "Amount ₹",
            min_value=0.0,
            step=50.0
        )

        submit = st.form_submit_button("Save Expense")

        if submit:
            add_expense(str(dt), cat, note, amt)
            st.success("Expense added successfully!")
            st.rerun()

# --------------------------------
# TRANSACTIONS
# --------------------------------
elif page == "Transactions":

    st.markdown("## 📄 Transaction History")

    if df.empty:
        st.warning("No transactions available.")

    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download CSV",
            csv,
            "expenses.csv",
            "text/csv"
        )

# --------------------------------
# AI INSIGHTS
# --------------------------------
elif page == "AI Insights":

    st.markdown("## 🤖 Smart Insights")

    if df.empty:
        st.info("Add some expenses first.")

    else:
        top = df.groupby("category")["amount"].sum().idxmax()
        top_amt = df.groupby("category")["amount"].sum().max()

        avg = df["amount"].mean()
        pred = avg * 30

        st.success(f"🔥 Highest Spending Category: {top} (₹{top_amt:,.0f})")

        st.warning(f"📌 Predicted Next 30 Days Spend: ₹{pred:,.0f}")

        if top_amt > avg * 5:
            st.error("⚠ You are overspending in one category.")

        st.info("💡 Tip: Use monthly budgets and reduce impulse purchases.")