import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from googletrans import Translator
import os

# إعداد المترجم
translator = Translator()

# دالة تحميل البيانات من ملف Excel
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

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
        # أدخل هنا كلمة مرور التطبيق الخاصة بحسابك
        server.login(from_email, "your_password")
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        st.success(f"تم إرسال البريد الإلكتروني بنجاح إلى {', '.join(to_email)}")
    except Exception as e:
        st.error(f"حدث خطأ أثناء إرسال البريد الإلكتروني: {e}")

# دالة التحقق من المخزون وإرسال التنبيهات
def check_stock_and_notify(df):
    for index, row in df.iterrows():
        product_name = row['Product Name']
        current_stock = row['Current Stock']
        min_stock = row['Min Stock Level']
        emails = row['Emails'].split(",")  # يفترض أن الإيميلات مفصولة بفواصل

        if current_stock <= min_stock:
            subject = f"تنبيه انخفاض المخزون: {product_name}"
            body = (
                f"عميلنا العزيز,\n\n"
                f"نود إعلامكم بأن المنتج '{product_name}' وصل إلى الحد الأدنى للمخزون.\n"
                f"المخزون الحالي: {current_stock}\n\n"
                "مع تحيات فريق تنبيهات المخزون"
            )
            send_email(emails, subject, body)

# دالة التحقق من تواريخ الانتهاء وإرسال التنبيهات
def check_expiry_dates_and_notify(df, reminder_days):
    for index, row in df.iterrows():
        product_name = row['Product Name']
        expiry_date = row['Expiry Date']
        emails = row['Emails'].split(",")  # يفترض أن الإيميلات مفصولة بفواصل

        # التأكد من وجود تاريخ انتهاء صالح وأنه من نوع datetime
        if pd.notnull(expiry_date) and isinstance(expiry_date, pd.Timestamp):
            days_to_expiry = (expiry_date - datetime.now()).days
            if days_to_expiry <= reminder_days:
                subject = f"تنبيه موعد انتهاء الصلاحية: {product_name}"
                body = (
                    f"عميلنا العزيز,\n\n"
                    f"نود إعلامكم بأن المنتج '{product_name}' سوف ينتهي صلاحيته خلال {days_to_expiry} يوم.\n"
                    f"تاريخ الانتهاء: {expiry_date.strftime('%Y-%m-%d')}\n\n"
                    "مع تحيات فريق تنبيهات المخزون"
                )
                send_email(emails, subject, body)

# دالة ترجمة النصوص إلى لغة محددة (يمكن استخدامها لاحقًا إذا دعت الحاجة)
def translate_text(text, language_code):
    return translator.translate(text, src='en', dest=language_code).text

# دالة حفظ البيانات في ملف Excel
def save_data(df, file_name):
    df.to_excel(file_name, index=False)
    st.success(f"تم حفظ البيانات بنجاح في الملف {file_name}")

# الواجهة الرئيسية باستخدام Streamlit
def main():
    st.title("تنبيهات المخزون - إدارة الجرد")
    st.write("مرحبا بكم في نظام تنبيهات المخزون.")

    # قائمة الخيارات في الشريط الجانبي
    menu = ["إدخال بيانات منتج جديد", "تحميل بيانات المخزون وفحص التنبيهات"]
    choice = st.sidebar.selectbox("اختر الخيار", menu)

    if choice == "إدخال بيانات منتج جديد":
        st.header("إدخال بيانات منتج جديد")
        with st.form(key="product_form"):
            product_name = st.text_input("اسم المنتج")
            current_stock = st.number_input("المخزون الحالي", min_value=0, step=1)
            min_stock = st.number_input("الحد الأدنى للمخزون", min_value=0, step=1)
            expiry_date = st.date_input("تاريخ انتهاء الصلاحية")
            emails = st.text_input("الإيميلات (افصل بين كل إيميل بفاصلة)")
            submit_form = st.form_submit_button(label="إضافة المنتج")

        if submit_form:
            # إنشاء DataFrame من البيانات المدخلة
            data = {
                "Product Name": [product_name],
                "Current Stock": [current_stock],
                "Min Stock Level": [min_stock],
                "Expiry Date": [pd.Timestamp(expiry_date)],
                "Emails": [emails]
            }
            df_new = pd.DataFrame(data)
            st.success("تمت إضافة بيانات المنتج بنجاح!")
            st.dataframe(df_new)

            # زر لحفظ البيانات في ملف Excel
            if st.button("حفظ البيانات في ملف Excel"):
                file_name = "stock_data.xlsx"
                if os.path.exists(file_name):
                    # إذا كان الملف موجودًا مسبقًا، يتم دمج البيانات الجديدة مع البيانات القديمة
                    df_existing = pd.read_excel(file_name)
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    save_data(df_combined, file_name)
                else:
                    save_data(df_new, file_name)

    elif choice == "تحميل بيانات المخزون وفحص التنبيهات":
        st.header("تحميل بيانات المخزون وفحص التنبيهات")
        uploaded_file = st.file_uploader("اختر ملف Excel لبيانات المخزون", type=["xlsx"])
        if uploaded_file is not None:
            try:
                df = load_data(uploaded_file)
                st.success("تم تحميل البيانات بنجاح!")
                st.dataframe(df)
                reminder_days = st.number_input("عدد الأيام للتنبيه قبل انتهاء الصلاحية", min_value=1, value=90, step=1)
                if st.button("فحص المخزون وإرسال التنبيهات"):
                    check_stock_and_notify(df)
                    check_expiry_dates_and_notify(df, reminder_days)
                    st.success("تمت عملية الفحص وإرسال التنبيهات إذا لزم الأمر.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")

if __name__ == "__main__":
    main()