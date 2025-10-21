from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    # Get form data
    smtp_server = request.form.get('smtp_server', '')
    smtp_port = request.form.get('smtp_port', '587')
    smtp_username = request.form.get('smtp_username', '')
    smtp_password = request.form.get('smtp_password', '')
    from_name = request.form.get('from_name', '')
    from_email = request.form.get('from_email', '')
    recipient_email = request.form.get('recipient_email', '')
    subject = request.form.get('subject', '')
    html_content = request.form.get('html_content', '')

    # Store in session for sending later
    request.environ['email_data'] = {
        'smtp_server': smtp_server,
        'smtp_port': smtp_port,
        'smtp_username': smtp_username,
        'smtp_password': smtp_password,
        'from_name': from_name,
        'from_email': from_email,
        'recipient_email': recipient_email,
        'subject': subject,
        'html_content': html_content
    }

    return render_template('preview.html',
                         html_content=html_content,
                         from_name=from_name,
                         from_email=from_email,
                         recipient_email=recipient_email,
                         subject=subject)

@app.route('/send', methods=['POST'])
def send_email():
    # Retrieve data from session
    email_data = request.environ.get('email_data', {})

    if not email_data:
        flash('Session expired. Please fill the form again.', 'error')
        return redirect(url_for('index'))

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email_data['subject']
        msg['From'] = f"{email_data['from_name']} <{email_data['from_email']}>"
        msg['To'] = email_data['recipient_email']

        # Create HTML part
        html_part = MIMEText(email_data['html_content'], 'html')
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(email_data['smtp_server'], int(email_data['smtp_port'])) as server:
            server.starttls()  # Secure the connection
            server.login(email_data['smtp_username'], email_data['smtp_password'])
            server.send_message(msg)

        flash('Email sent successfully!', 'success')
        return render_template('success.html')

    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)