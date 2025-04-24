import streamlit as st
import pandas as pd
import os

# إعداد لون الخلفية
page_bg = """
<style>
    body {
        background-color: #f5f5dc;
    }
    .stButton>button {
        color: white;
        background-color: #8b9474;
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

st.title("تنبيهات المخزون - نظام إدارة بسيط")

# تحميل أو إنشاء ملف البيانات
file_path = "stock_data.xlsx"
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
else:
    df = pd.DataFrame(columns=["اسم المنتج", "الكمية الحالية", "الحد الأدنى", "الإيميلات"])

# نموذج إدخال البيانات
with st.form("data_form"):
    product_name = st.text_input("اسم المنتج")
    current_stock = st.number_input("الكمية الحالية", min_value=0)
    min_stock = st.number_input("الحد الأدنى", min_value=0)
    emails = st.text_input("الإيميلات (افصل بينهم بفاصلة)")

    submitted = st.form_submit_button("إضافة")

    if submitted:
        new_row = {
            "اسم المنتج": product_name,
            "الكمية الحالية": current_stock,
            "الحد الأدنى": min_stock,
            "الإيميلات": emails
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(file_path, index=False)
        st.success("تمت إضافة المنتج وتخزين البيانات بنجاح.")

        if current_stock <= min_stock:
            st.error(f"تنبيه! الكمية الحالية من '{product_name}' أقل من الحد الأدنى ({min_stock})!")

# عرض الجدول
st.subheader("جدول المنتجات")
st.dataframe(df)