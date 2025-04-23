import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# 1. تحميل البيانات من ملف Excel (يجب أن يكون ملف إكسل فيه الأعمدة المناسبة)
def load_data(file_path):
    return pd.read_excel(file_path)

# 2. تحديد وظيفة لإرسال البريد الإلكتروني
def send_email(to_email, subject, body, from_email="stockalerts.ps@gmail.com"):
    try:
        # إعداد البريد الإلكتروني
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ", ".join(to_email)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # إعداد الاتصال بالخادم
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, "your_password")  # أدخل هنا كلمة مرور التطبيق الخاص بك
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email sent successfully to {', '.join(to_email)}")
    except Exception as e:
        print(f"Error: {e}")

# 3. التحقق من المخزون وإرسال التنبيهات
def check_stock_and_notify(df):
    for index, row in df.iterrows():
        product_name = row['Product Name']
        current_stock = row['Current Stock']
        min_stock = row['Min Stock Level']
        emails = row['Emails'].split(",")  # إذا كانت الإيميلات مفصولة بفواصل
        
        # التحقق إذا كانت الكمية الحالية أقل من الحد الأدنى
        if current_stock <= min_stock:
            subject = f"Low stock alert: {product_name}"
            body = f"Dear Customer,\n\nWe would like to inform you that the product '{product_name}' has reached the minimum stock level.\nCurrent stock: {current_stock}\n\nBest regards,\nStock Alerts Team"
            
            # إرسال الإيميل لجميع العناوين
            send_email(emails, subject, body)

# 4. حفظ البيانات بشكل تلقائي (تخزين الإيميلات وحالة المخزون في ملف إكسل)
def save_data(df, file_path):
    df.to_excel(file_path, index=False)

# 5. نموذج لحفظ البيانات من التطبيق
def enter_data():
    data = []
    while True:
        product_name = input("Enter product name: ")
        current_stock = int(input(f"Enter current stock for {product_name}: "))
        min_stock = int(input(f"Enter minimum stock level for {product_name}: "))
        emails = input(f"Enter emails (comma separated) for {product_name}: ")
        
        # إضافة البيانات المدخلة إلى القائمة
        data.append([product_name, current_stock, min_stock, emails])
        
        more = input("Do you want to add more products? (y/n): ")
        if more.lower() != 'y':
            break
    
    # تحويل البيانات إلى DataFrame وتخزينها في ملف إكسل
    df = pd.DataFrame(data, columns=["Product Name", "Current Stock", "Min Stock Level", "Emails"])
    save_data(df, "stock_data.xlsx")

# 6. تحميل البيانات من ملف إكسل موجود
def load_existing_data():
    file_path = input("Enter the path to your stock data Excel file: ")
    if os.path.exists(file_path):
        df = load_data(file_path)
        print(f"Data loaded successfully from {file_path}")
        check_stock_and_notify(df)  # التحقق من المخزون وإرسال التنبيهات
    else:
        print("The file path does not exist. Please try again.")

# 7. واجهة المستخدم لتحديد العملية
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
