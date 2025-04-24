import pandas as pd
import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from googletrans import Translator
import os

# إعداد المترجم
translator = Translator()

# دالة تحميل البيانات من ملف Excel
def load_data(file_path):
    return pd.read_excel(file_path)

# دالة إرسال البريد الإلكتروني
def send_email(to_email, subject, body, from_email="stockalerts.ps@gmail.com"):
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ", ".join(to_email)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, "your_password")  # أدخل كلمة مرور التطبيق الخاصة بك هنا
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email sent successfully to {', '.join(to_email)}")
    except Exception as e:
        print(f"Error: {e}")

# دالة التحقق من المخزون وإرسال التنبيهات
def check_stock_and_notify(df):
    for index, row in df.iterrows():
        product_name = row['Product Name']
        current_stock = row['Current Stock']
        min_stock = row['Min Stock Level']
        emails = row['Emails'].split(",")  # إذا كانت الإيميلات مفصولة بفواصل

        if current_stock <= min_stock:
            subject = f"Low stock alert: {product_name}"
            body = f"Dear Customer,\n\nWe would like to inform you that the product '{product_name}' has reached the minimum stock level.\nCurrent stock: {current_stock}\n\nBest regards,\nStock Alerts Team"
            send_email(emails, subject, body)

# دالة التحقق من تواريخ الانتهاء وإرسال التنبيهات
def check_expiry_dates_and_notify(df, reminder_days):
    for index, row in df.iterrows():
        product_name = row['Product Name']
        expiry_date = row['Expiry Date']
        emails = row['Emails'].split(",")  # إذا كانت الإيميلات مفصولة بفواصل

        # التحقق إذا كان تاريخ اليوم يقترب من تاريخ انتهاء صلاحية المنتج
        if expiry_date and (expiry_date - datetime.now()).days <= reminder_days:
            subject = f"Expiry Date Reminder: {product_name}"
            body = f"Dear Customer,\n\nWe would like to inform you that the product '{product_name}' is about to expire in {reminder_days} days.\nExpiry date: {expiry_date.strftime('%Y-%m-%d')}\n\nBest regards,\nStock Alerts Team"
            send_email(emails, subject, body)

# دالة لتحويل النصوص إلى اللغة المطلوبة
def translate_text(text, language_code):
    return translator.translate(text, src='en', dest=language_code).text

# دالة حفظ البيانات في ملف Excel
def save_data(df, file_path):
    df.to_excel(file_path, index=False)

# دالة لتحميل البيانات
def load_existing_data():
    file_path = input("Enter the path to your stock data Excel file: ")
    if os.path.exists(file_path):
        df = load_data(file_path)
        print(f"Data loaded successfully from {file_path}")
        check_stock_and_notify(df)
        check_expiry_dates_and_notify(df, reminder_days=90)  # التحقق من تواريخ الانتهاء لمدة 90 يوم
    else:
        print("The file path does not exist. Please try again.")

# واجهة المستخدم
def main():
    print("Stock Alerts - Inventory Management")
    while True:
        choice = input("Choose an option:\n1. Enter new product data\n2. Load existing data and check stock\n3. Exit\n")

        if choice == '1':
            enter_data()
        elif choice == '2':
            load_existing_data()
        elif choice == '3':
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()