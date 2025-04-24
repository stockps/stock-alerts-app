import pandas as pd import smtplib import streamlit as st from email.mime.multipart import MIMEMultipart from email.mime.text import MIMEText from datetime import datetime, timedelta from googletrans import Translator import os

إعداد المترجم

translator = Translator()

إرسال بريد إلكتروني

def send_email(to_email, subject, body, from_email="stockalerts.ps@gmail.com", password="your_app_password"): try: msg = MIMEMultipart() msg['From'] = from_email msg['To'] = ", ".join(to_email) msg['Subject'] = subject msg.attach(MIMEText(body, 'plain'))

server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    st.success(f"تم إرسال البريد إلى: {', '.join(to_email)}")
except Exception as e:
    st.error(f"حدث خطأ أثناء إرسال البريد: {e}")

توليد النص المترجم

def translate_text(text, lang): try: translated = translator.translate(text, dest=lang) return translated.text except: return text

فحص الكميات وتواريخ الانتهاء

def check_alerts(df, expiry_notice_months, lang): today = datetime.today() for index, row in df.iterrows(): name = row['Product Name'] stock = row['Current Stock'] min_stock = row['Min Stock Level'] expiry_date = row['Expiry Date'] email_list = row['Emails'].split(',')

if stock <= min_stock:
        subject = {
            'ar': f"تنبيه: وصل المنتج '{name}' للحد الأدنى",
            'en': f"Alert: Product '{name}' has reached minimum stock",
            'he': translate_text(f"Alert: Product '{name}' has reached minimum stock", 'he')
        }
        body = {
            'ar': f"نود إعلامكم أن المنتج '{name}' قد وصل للحد الأدنى في المخزون. الكمية الحالية: {stock}",
            'en': f"We would like to inform you that the product '{name}' has reached the minimum stock level.\nCurrent stock: {stock}",
            'he': translate_text(f"We would like to inform you that the product '{name}' has reached the minimum stock level.\nCurrent stock: {stock}", 'he')
        }
        send_email(email_list, subject[lang], body[lang])

    # تنبيه تاريخ الانتهاء
    if pd.notnull(expiry_date):
        expiry = pd.to_datetime(expiry_date)
        notice_date = expiry - timedelta(days=expiry_notice_months*30)
        if today >= notice_date:
            subject = {
                'ar': f"تنبيه: المنتج '{name}' يقترب من تاريخ انتهاء الصلاحية",
                'en': f"Alert: Product '{name}' is nearing expiration date",
                'he': translate_text(f"Alert: Product '{name}' is nearing expiration date", 'he')
            }
            body = {
                'ar': f"نود إعلامكم أن المنتج '{name}' تبقى على انتهاء صلاحيته {expiry_notice_months} شهور.",
                'en': f"We would like to inform you that the product '{name}' will expire in {expiry_notice_months} months.",
                'he': translate_text(f"We would like to inform you that the product '{name}' will expire in {expiry_notice_months} months.", 'he')
            }
            send_email(email_list, subject[lang], body[lang])

واجهة المستخدم

st.title("تنبيهات المخزون وتواريخ الانتهاء")

uploaded_file = st.file_uploader("ارفع ملف Excel يحتوي على بيانات المنتجات:", type=["xlsx"])

lang_option = st.selectbox("اختر لغة التنبيه:", ["ar", "en", "he"]) expiry_notice = st.slider("عدد الشهور قبل تاريخ الانتهاء لإرسال التنبيه:", 1, 12, 3)

if uploaded_file: df = pd.read_excel(uploaded_file) st.dataframe(df) if st.button("تشغيل التنبيهات"): check_alerts(df, expiry_notice, lang_option) st.success("تمت معالجة جميع التنبيهات.")

