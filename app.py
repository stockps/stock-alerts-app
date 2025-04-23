import streamlit as st
import pandas as pd

st.set_page_config(page_title="Stock Alerts", page_icon=":package:", layout="centered")

st.title("تنبيهات المخزون - Stock Alerts")

uploaded_file = st.file_uploader("ارفع ملف Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("البيانات المدخلة:")
    st.dataframe(df)

    alerts = []
    for index, row in df.iterrows():
        if row['الكمية الحالية'] <= row['الحد الأدنى']:
            alerts.append(f"المنتج: {row['اسم المنتج']} وصل إلى الحد الأدنى ({row['الكمية الحالية']})")

    if alerts:
        st.error("تنبيهات:")
        for alert in alerts:
            st.write(alert)
    else:
        st.success("لا توجد منتجات وصلت إلى الحد الأدنى.")
