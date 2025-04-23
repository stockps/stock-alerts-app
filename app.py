import streamlit as st import pandas as pd import smtplib from email.mime.text import MIMEText from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Stock Alerts", layout="centered", page_icon="📦", initial_sidebar_state="collapsed") st.markdown(""" <style> body, .stApp { background-color: #f7f3ef; color: #3e3e3e; font-family: 'Segoe UI', sans-serif; } .stButton > button { background-color: #d9cbbd; color: #3e3e3e; border-radius: 10px; padding: 0.5em 1em; } .stTextInput, .stNumberInput, .stTextArea { background-color: #ffffff; border-radius: 10px; padding: 0.2em 0.5em; } </style> """, unsafe_allow_html=True)

st.title("تنبيهات المخزون - Stock Alerts")

st.write("أدخل بيانات المنتجات. سيتم إرسال تنبيه إذا وصلت الكمية للحد الأدنى.")

Data Entry Table

product_data = [] num_rows = st.number_input("عدد المنتجات", min_value=1, max_value=50, step=1)

for i in range(num_rows): st.markdown(f"### منتج {i+1}") name = st.text_input(f"اسم المنتج {i+1}", key=f"name_{i}") current_qty = st.number_input(f"الكمية الحالية {i+1}", min_value=0, key=f"qty_{i}") min_qty = st.number_input(f"الحد الأدنى {i+1}", min_value=0, key=f"min_{i}") product_data.append({"name": name, "current": current_qty, "min": min_qty})

Email section

emails = st.text_area("أدخل الإيميلات (من 1 إلى 5) مفصولة بفاصلة ", placeholder="example1@mail.com, example2@mail.com") email_list = [email.strip() for email in emails.split(',') if email.strip()]

lang = st.selectbox("اختر لغة الإشعار", ["العربية", "English", "עברית"])

Default message templates

def get_message(lang, product_name, current_qty): if lang == "العربية": return f"نود إعلامكم أن المنتج '{product_name}' قد وصل إلى الحد الأدنى. الكمية المتوفرة: {current_qty}." elif lang == "English": return f"We would like to inform you that the product '{product_name}' has reached its minimum threshold. Current stock: {current_qty}." elif lang == "עברית": return f"אנו רוצים להודיע לכם שהמוצר '{product_name}' הגיע לרף המינימום. כמות נוכחית: {current_qty}."

Send alerts

if st.button("تحقق وأرسل التنبيهات"): if len(email_list) == 0 or len(email_list) > 5: st.warning("يرجى إدخال من 1 إلى 5 إيميلات صحيحة.") else: alerts = [] for product in product_data: if product['name'] and product['current'] <= product['min']: alerts.append(product)

if not alerts:
        st.success("لا توجد منتجات وصلت للحد الأدنى.")
    else:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('stockalerts.ps@gmail.com', 'APP_PASSWORD')  # Use your app password here

            for product in alerts:
                msg = MIMEMultipart()
                msg['Subject'] = "تنبيه مخزون"
                msg['From'] = "stockalerts.ps@gmail.com"
                msg['To'] = ", ".join(email_list)

                message_body = get_message(lang, product['name'], product['current'])
                msg.attach(MIMEText(message_body, 'plain'))

                server.sendmail('stockalerts.ps@gmail.com', email_list, msg.as_string())

            server.quit()
            st.success("تم إرسال التنبيهات بنجاح!")
        except Exception as e:
            st.error(f"فشل في إرسال البريد الإلكتروني: {e}")

