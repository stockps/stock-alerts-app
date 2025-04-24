stock_alerts_app/app.py

import pandas as pd import smtplib import streamlit as st from email.mime.multipart import MIMEMultipart from email.mime.text import MIMEText from datetime import datetime, timedelta from googletrans import Translator

translator = Translator()

--- إرسال الإيميل ---

def send_email(to_email, subject, body, from_email="stockalerts.ps@gmail.com", password="your_app_password"): try: msg = MIMEMultipart() msg['From'] = from_email msg['To'] = ", ".join(to_email) msg['Subject'] = subject msg.attach(MIMEText(body, 'plain'))

server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
except Exception as e:
    st.error(f"Email error: {e}")

--- التحقق من الحد الأدنى وتاريخ الانتهاء ---

def check_alerts(df, language, expiry_notice_days): today = datetime.today().date() for _, row in df.iterrows(): product = row['Product Name'] current_stock = row['Current Stock'] min_stock = row['Min Stock Level'] expiry_date = row['Expiry Date'] emails = row['Emails'].split(',') custom_msg = row['Custom Message'] if pd.notna(row['Custom Message']) else ''

# الحد الأدنى
    if current_stock <= min_stock:
        if not custom_msg:
            custom_msg = f"We would like to inform you that the product '{product}' has reached the minimum stock level. Current stock: {current_stock}."
        subject = f"Low stock alert: {product}"
        translated = translator.translate(custom_msg, dest=language).text
        send_email(emails, subject, translated)

    # تاريخ الانتهاء
    if pd.notna(expiry_date):
        expiry = pd.to_datetime(expiry_date).date()
        days_left = (expiry - today).days
        if days_left <= expiry_notice_days:
            msg = custom_msg or f"We would like to inform you that the product '{product}' will expire in {days_left} days."
            subject = f"Expiry alert: {product}"
            translated = translator.translate(msg, dest=language).text
            send_email(emails, subject, translated)

--- واجهة Streamlit ---

st.set_page_config(page_title="Stock Alerts App", layout="centered") st.title("Stock & Expiry Alerts")

uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx") expiry_notice_days = st.number_input("Days before expiry to send alert", min_value=1, max_value=365, value=90) language_option = st.selectbox("Language for Email", options=["en", "ar", "he"])

if uploaded_file: df = pd.read_excel(uploaded_file) required_columns = ["Product Name", "Current Stock", "Min Stock Level", "Expiry Date", "Emails", "Custom Message"] missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error(f"Missing columns in Excel file: {', '.join(missing)}")
else:
    st.success("File uploaded and validated successfully!")
    if st.button("Run Alerts Check"):
        check_alerts(df, language_option, expiry_notice_days)
        st.success("Alerts processed!")

st.markdown("""

Notes:

The Excel file must contain columns: Product Name, Current Stock, Min Stock Level, Expiry Date, Emails, Custom Message

Example for integration with accounting software will be supported in future. """)


