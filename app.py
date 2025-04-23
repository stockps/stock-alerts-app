import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Stock Alerts", layout="centered")
st.markdown("<h1 style='text-align: center; color: #6c757d;'>Stock Alerts Management</h1>", unsafe_allow_html=True)

def send_email(product_name, current_qty, recipient_emails, lang="en", custom_msg=None):
    msg = MIMEMultipart()
    msg["From"] = "stockalerts.ps@gmail.com"
    msg["Subject"] = "Stock Alert Notification"

    messages = {
        "en": f"Product '{product_name}' has reached the minimum stock level.
Current quantity: {current_qty}.",
        "ar": f"نود إعلامكم بأن المنتج '{product_name}' وصل إلى الحد الأدنى من الكمية.
الكمية الحالية: {current_qty}.",
        "he": f"המוצר '{product_name}' הגיע לרמת המלאי המינימלית.
כמות נוכחית: {current_qty}."
    }

    text = custom_msg if custom_msg else messages.get(lang, messages["en"])
    msg.attach(MIMEText(text, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("stockalerts.ps@gmail.com", "APP_PASSWORD")
        for email in recipient_emails:
            msg["To"] = email
            server.sendmail("stockalerts.ps@gmail.com", email, msg.as_string())
        server.quit()
        st.success("Emails sent successfully.")
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Product", "Current Qty", "Minimum Qty"])

st.subheader("Add Product Info")
with st.form("entry_form"):
    col1, col2, col3 = st.columns(3)
    product = col1.text_input("Product")
    current_qty = col2.number_input("Current Quantity", min_value=0, step=1)
    min_qty = col3.number_input("Minimum Quantity", min_value=0, step=1)
    emails = st.text_input("Emails (comma-separated, up to 5)")
    lang = st.selectbox("Email Language", ["en", "ar", "he"])
    custom_msg = st.text_area("Custom Message (optional)")
    submitted = st.form_submit_button("Add")

    if submitted and product:
        new_row = pd.DataFrame([[product, current_qty, min_qty]], columns=["Product", "Current Qty", "Minimum Qty"])
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        if current_qty <= min_qty:
            recipients = [e.strip() for e in emails.split(",") if e.strip()]
            if 1 <= len(recipients) <= 5:
                send_email(product, current_qty, recipients, lang, custom_msg)
            else:
                st.warning("Please enter between 1 and 5 email addresses.")

st.subheader("Product Table")
st.dataframe(st.session_state.data)