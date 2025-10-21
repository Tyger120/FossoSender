from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_session import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
Session(app)

def validate_email(email):
    """Validate email address format"""
    email = email.strip()
    if not email:
        return False
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False
    
    name, addr = parseaddr(email)
    return '@' in addr and '.' in addr.split('@')[1]

@app.route('/service-worker.js')
def service_worker():
    """Serve service worker from root for proper PWA scope"""
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')

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
    connection_type = request.form.get('connection_type', 'starttls')
    from_name = request.form.get('from_name', '')
    from_email = request.form.get('from_email', '')
    recipient_emails = request.form.get('recipient_emails', '')
    subject = request.form.get('subject', '')
    html_content = request.form.get('html_content', '')

    # Store in session for sending later
    session['email_data'] = {
        'smtp_server': smtp_server,
        'smtp_port': smtp_port,
        'smtp_username': smtp_username,
        'smtp_password': smtp_password,
        'connection_type': connection_type,
        'from_name': from_name,
        'from_email': from_email,
        'recipient_emails': recipient_emails,
        'subject': subject,
        'html_content': html_content
    }

    return render_template('preview.html',
                         html_content=html_content,
                         from_name=from_name,
                         from_email=from_email,
                         recipient_emails=recipient_emails,
                         subject=subject)

@app.route('/test-connection', methods=['POST'])
def test_connection():
    data = request.get_json()
    smtp_server = data.get('smtp_server', '')
    smtp_port = data.get('smtp_port', '587')
    smtp_username = data.get('smtp_username', '')
    smtp_password = data.get('smtp_password', '')
    connection_type = data.get('connection_type', 'starttls')
    
    try:
        # Test SMTP connection based on connection type
        if connection_type == 'ssl':
            with smtplib.SMTP_SSL(smtp_server, int(smtp_port), timeout=10) as server:
                server.login(smtp_username, smtp_password)
        else:
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
        # Parse multiple recipients (comma or newline separated)
        recipient_list = email_data['recipient_emails'].replace('\n', ',').split(',')
        recipient_list = [email.strip() for email in recipient_list if email.strip()]
        
        if not recipient_list:
            flash('No valid recipients provided.', 'error')
            return redirect(url_for('index'))
        
        # Validate all email addresses
        invalid_emails = [email for email in recipient_list if not validate_email(email)]
        if invalid_emails:
            flash(f'Invalid email addresses: {", ".join(invalid_emails)}', 'error')
            return redirect(url_for('index'))

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email_data['subject']
        msg['From'] = f"{email_data['from_name']} <{email_data['from_email']}>"
        msg['To'] = ', '.join(recipient_list)

        # Create HTML part
        html_part = MIMEText(email_data['html_content'], 'html')
        msg.attach(html_part)

        # Send email based on connection type
        connection_type = email_data.get('connection_type', 'starttls')
        
        if connection_type == 'ssl':
            with smtplib.SMTP_SSL(email_data['smtp_server'], int(email_data['smtp_port']), timeout=30) as server:
                server.login(email_data['smtp_username'], email_data['smtp_password'])
                server.send_message(msg)
        else:
            with smtplib.SMTP(email_data['smtp_server'], int(email_data['smtp_port']), timeout=30) as server:
                server.starttls()
                server.login(email_data['smtp_username'], email_data['smtp_password'])
                server.send_message(msg)

        session.pop('email_data', None)
        
        flash(f'Email sent successfully to {len(recipient_list)} recipient(s)!', 'success')
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