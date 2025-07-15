from flask import Flask, render_template_string, request
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load HTML form
with open('form.html', 'r', encoding='utf-8') as file:
    form_template = file.read()

# Google Sheet Setup
SHEET_ID = "1gyVC_iHfDR4GDebCt1zjWWQ-1W4L4EhGotDIexdwvu8"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
sheet_client = gspread.authorize(creds)
sheet = sheet_client.open_by_key(SHEET_ID).sheet1

# Gmail credentials
GMAIL_USER = "tskarthi2003@gmail.com"
GMAIL_APP_PASSWORD = "jysu dvcs pddi dqcy"  # App Password

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            college_name = request.form['college_name']
            qualification = request.form['qualification']
            department = request.form['department']
            passed_out = request.form['passed_out']
            address = request.form['address']
            mobile = request.form['mobile']
            email = request.form['email']
            course = request.form['course']
            communication = request.form['communication']
            skills_list = request.form.getlist('skills[]')  
            skills = ', '.join(skills_list)
            codings_list = request.form.getlist('codings[]')
            codings = ', '.join(codings_list)
            backlogs = request.form['backlogs']
            backlog_count = request.form['backlog_count'] if request.form.get('backlog_count') else '0'
            arrears = request.form['arrears']

            # Save resume locally
            resume = request.files['resume']
            if resume.filename == '':
                raise Exception("Resume not uploaded")
            filename = f"{first_name}_{last_name}_{resume.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume.save(file_path)

            submitted_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

            # ✅ Check for duplicate email
            existing_emails = sheet.col_values(9)  
            if email in existing_emails:
              sheet.append_row([
                  first_name,
                  last_name,
                  college_name,
                  qualification,
                  department,
                  passed_out,
                  address,
                  mobile,
                  email,
                  course,
                  communication,
                  skills,
                  codings,
                  backlogs,
                  backlog_count,
                  arrears,
                  filename,
                  submitted_time,
                  "Duplicate Entry"
              ])
              return render_template_string(form_template, message="✅ Submitted successfully! But You Have Already Used This Email For Registration", success=False)


            

            # ✅ Send email with resume
            message = MIMEMultipart()
            message['From'] = GMAIL_USER
            message['To'] = GMAIL_USER
            message['Subject'] = f"New Candidate - {first_name} {last_name}"

            body = f"""
📝 New Candidate Submission:

👤 Name: {first_name} {last_name}
🏫 College: {college_name}
🎓 Qualification: {qualification}
📚 Department: {department}
📅 Passed Out: {passed_out}
📍 Address: {address}
📱 Mobile: {mobile}
📧 Email: {email}
📘 Course: {course}
🗣️ Communication: {communication}
💡 Skills: {skills}
📚 Backlogs: {backlogs} ({backlog_count})
⏮️ Arrears: {arrears}
🕒 Submitted: {submitted_time}
"""
            message.attach(MIMEText(body, "plain"))

            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                message.attach(part)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.send_message(message)

            return render_template_string(form_template, message="✅ Submitted successfully!", success=True)

        except Exception as e:
            print("Error:", e)
            return render_template_string(form_template, message=f"❌ Something went wrong: {e}", success=False)

    return render_template_string(form_template, message=None)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
