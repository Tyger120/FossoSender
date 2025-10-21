from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_session import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
Session(app)

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
    session['email_data'] = {
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

@app.route('/test-connection', methods=['POST'])
def test_connection():
    data = request.get_json()
    smtp_server = data.get('smtp_server', '')
    smtp_port = data.get('smtp_port', '587')
    smtp_username = data.get('smtp_username', '')
    smtp_password = data.get('smtp_password', '')
    
    try:
        # Test SMTP connection
        with smtplib.SMTP(smtp_server, int(smtp_port), timeout=10) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
        
        return jsonify({'success': True, 'message': 'Connection successful!'})
    except smtplib.SMTPAuthenticationError:
        return jsonify({'success': False, 'message': 'Authentication failed. Check your username and password.'})
    except smtplib.SMTPConnectError:
        return jsonify({'success': False, 'message': 'Could not connect to SMTP server. Check server and port.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Connection failed: {str(e)}'})

@app.route('/send', methods=['POST'])
def send_email():
    # Retrieve data from session
    email_data = session.get('email_data', {})

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
        with smtplib.SMTP(email_data['smtp_server'], int(email_data['smtp_port']), timeout=30) as server:
            server.starttls()
            server.login(email_data['smtp_username'], email_data['smtp_password'])
            server.send_message(msg)

        session.pop('email_data', None)
        
        flash('Email sent successfully!', 'success')
        return render_template('success.html')

    except smtplib.SMTPAuthenticationError:
        flash('Authentication failed. Check your SMTP username and password.', 'error')
        return redirect(url_for('index'))
    except smtplib.SMTPConnectError:
        flash('Could not connect to SMTP server. Check server address and port.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)