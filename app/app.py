import streamlit as st
import joblib
import os

# Load model pipeline (includes vectorizer and classifier)
model = joblib.load(os.path.join("app", "ml_model", "ticket_classifier.pkl"))
vectorizer = joblib.load(os.path.join("app", "ml_model", "ticket_vectorizer.pkl"))

st.title("🎫 IT Helpdesk Ticket Classifier")
ticket = st.text_area("Enter the ticket description:")

if st.button("Classify"):
    if ticket.strip():
        prediction = model.predict([ticket])[0]  # ✅ pass raw string inside list
        st.success(f"Predicted Category: **{prediction}**")
    else:
        st.warning("Please enter a ticket description.")
