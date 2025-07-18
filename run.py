import streamlit as st
import joblib
import pandas as pd
import os
from io import BytesIO
import plotly.express as px
from datetime import datetime

from database import (
    create_table, create_staff_table, create_staff_logs_table,
    insert_ticket, fetch_all_tickets, update_ticket_status,
    insert_staff, validate_staff, log_staff_action, fetch_staff_logs
)
from email_utils import send_confirmation_email

# Load the trained model
model_path = os.path.join("app", "ml_model", "ticket_classifier.pkl")
model = joblib.load(model_path)

# Create necessary tables
create_table()
create_staff_table()
create_staff_logs_table()

# Session state defaults
if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

if "menu" not in st.session_state:
    st.session_state.menu = "Submit Ticket"

# Sidebar Navigation with persistent state
menu = st.sidebar.selectbox("Choose View", [
    "Submit Ticket", "Admin Dashboard", "Login", "Staff Logs", "Register New Staff"
], index=[
    "Submit Ticket", "Admin Dashboard", "Login", "Staff Logs", "Register New Staff"
].index(st.session_state.menu))

st.session_state.menu = menu  # Save selected menu


# --- Submit Ticket View ---
if menu == "Submit Ticket":
    st.title("🛠️ IT Helpdesk Ticket Classifier")
    st.markdown("Please fill out the form below to submit a support ticket.")

    with st.form("ticket_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        issue = st.text_area("Describe your issue")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        submitted = st.form_submit_button("Submit Ticket")

        if submitted:
            if name and email and issue:
                prediction = model.predict([issue])[0]
                insert_ticket(name, email, issue, priority, prediction)
                send_confirmation_email(email, name, issue, prediction)
                st.success(f"✅ Ticket submitted! Category: **{prediction}**")
            else:
                st.error("❌ Please fill in all the fields.")

# --- Admin Dashboard View ---
elif menu == "Admin Dashboard":
    if st.session_state.logged_user:
        st.title("📋 Admin Dashboard - All Submitted Tickets")

        # Logout button
        if st.button("🚪 Logout"):
            log_staff_action(st.session_state.logged_user, "Logged out")
            st.session_state.logged_user = None
            st.session_state.menu = "Login"
            st.experimental_rerun()

        tickets = fetch_all_tickets()
        search = st.text_input("🔍 Search tickets by issue or name")

        if search:
            tickets = [t for t in tickets if search.lower() in t[1].lower() or search.lower() in t[3].lower()]

        if tickets:
            df = pd.DataFrame(tickets, columns=["ID", "Name", "Email", "Issue", "Priority", "Category", "Status", "Created At"])
            st.write(f"Showing {len(tickets)} ticket(s):")

            st.download_button("📥 Export to CSV", data=df.to_csv(index=False), file_name="tickets.csv", mime="text/csv")

            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            st.download_button("📊 Export to Excel", data=excel_buffer.getvalue(),
                               file_name="tickets.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            st.dataframe(df, use_container_width=True)

            # Update Ticket Status
            st.subheader("🛠️ Manage Ticket Status")
            selected_ticket = st.selectbox("Select a Ticket ID to update", df["ID"])
            new_status = st.selectbox("Change status to", ["Open", "In Progress", "Closed"])

            if st.button("✅ Update Status"):
                update_ticket_status(selected_ticket, new_status)
                log_staff_action(st.session_state.logged_user, f"Updated ticket {selected_ticket} to '{new_status}'")
                st.success("✅ Ticket status updated!")

            # Charts
            st.subheader("📊 Ticket Distribution by Category")
            fig_cat = px.pie(df, names="Category", title="Tickets by Category")
            st.plotly_chart(fig_cat, use_container_width=True)

            st.subheader("📈 Ticket Status Overview")
            fig_status = px.pie(df, names="Status", title="Tickets by Status")
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No tickets found.")
    else:
        st.warning("⚠️ Please log in as staff to access the admin dashboard.")

# --- Login View ---
elif menu == "Login":
    st.title("🔐 Staff Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

        if login_btn:
            user = validate_staff(username, password)
            if user:
                st.session_state.logged_user = username
                log_staff_action(username, "Logged in")
                st.success(f"✅ Welcome, {username}!")
                st.session_state.menu = "Admin Dashboard"
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

# --- Staff Logs View ---
elif menu == "Staff Logs":
    if st.session_state.logged_user:
        st.title("📝 Staff Activity Logs")

        logs = fetch_staff_logs()
        if logs:
            df_logs = pd.DataFrame(logs, columns=["ID", "Username", "Action", "Timestamp"])

            st.write(f"Total logs: {len(df_logs)}")

            staff_filter = st.selectbox("Filter by staff", ["All"] + sorted(df_logs["Username"].unique().tolist()))
            if staff_filter != "All":
                df_logs = df_logs[df_logs["Username"] == staff_filter]

            date_filter = st.date_input("Filter by date")
            if date_filter:
                df_logs = df_logs[df_logs["Timestamp"].str.startswith(str(date_filter))]

            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("No staff activity logs found.")
    else:
        st.warning("⚠️ Please log in to view logs.")

# --- Register New Staff ---
elif menu == "Register New Staff":
    st.title("👤 Register New Staff User")
    st.info("Only admins should access this page to create new staff accounts.")

    with st.form("register_form"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["staff", "admin"])
        register_btn = st.form_submit_button("Create Account")

    if register_btn:
        if new_username and new_password:
            try:
                insert_staff(new_username, new_password, new_role)
                log_staff_action(st.session_state.logged_user or new_username, f"Registered new staff: {new_username}")
                st.success(f"✅ Staff user '{new_username}' created with role '{new_role}'.")
            except:
                st.error("❌ Username already exists. Try another one.")
        else:
            st.warning("⚠️ Username and password are required.")
