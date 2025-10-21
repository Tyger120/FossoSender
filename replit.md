# Email Sender Application

## Overview

This is a Flask-based web application that enables users to send HTML emails through configurable SMTP servers. The application provides a user-friendly interface for composing emails, previewing them before sending, and managing SMTP configurations. It's designed as a tool for sending custom HTML emails with full control over SMTP settings, making it suitable for testing email templates or sending formatted messages.

## Recent Changes

**October 21, 2025 - Latest Update**
- **SSL/TLS Support**: Added support for both STARTTLS (port 587) and SSL/TLS (port 465) connections via dropdown selector
- **Multiple Recipients**: Users can now send emails to multiple recipients (comma or newline separated)
- **Email Validation**: Implemented robust server-side email validation to prevent malformed addresses from causing SMTP errors
- **PWA Support**: Converted application to Progressive Web App (PWA) for offline capability and mobile installation
  - Created manifest.json with app metadata
  - Implemented service worker for offline caching
  - Added PWA icons (192x192 and 512x512)
  - Service worker served from root for proper scope control

**October 21, 2025 - Previous Update**
- Fixed critical security vulnerability: Implemented server-side session storage using Flask-Session to prevent SMTP credentials from being exposed in client-side cookies
- Added SMTP connection testing functionality with dedicated `/test-connection` endpoint
- Improved error handling with specific exception types (SMTPAuthenticationError, SMTPConnectError)
- Added "Test SMTP Connection" button in the UI with real-time feedback via AJAX
- Implemented automatic session cleanup after email sending to minimize credential storage time
- Added timeouts to SMTP connections for better reliability
- Updated Flask app to bind to 0.0.0.0:5000 for proper network accessibility

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Problem**: Need an intuitive interface for email composition and SMTP configuration.

**Solution**: Multi-page Flask template system with progressive workflow (compose → preview → send).

**Key Design Decisions**:
- **Template Structure**: Three-page flow separating configuration, preview, and confirmation
  - `index.html`: Main form for SMTP settings and email composition
  - `preview.html`: Email preview before sending
  - `success.html`: Confirmation page after successful send
- **Styling Approach**: Custom CSS (`style.css`) with responsive container-based layout
- **Form Validation**: HTML5 validation for required fields with client-side JavaScript for SMTP connection testing
- **Static Email Template**: Includes a pre-built Chase bank-themed email template (`chase.html`) as a reference/example

**Rationale**: Progressive disclosure reduces user error by allowing review before sending, while the multi-step process provides clear feedback at each stage.

### Backend Architecture

**Problem**: Need to handle email composition, SMTP communication, and session management across multiple request/response cycles.

**Solution**: Flask application with server-side session storage for form data persistence.

**Core Components**:
- **Flask Framework**: Lightweight web framework for routing and templating
- **Session Management**: Flask-Session with filesystem-based storage (`SESSION_TYPE = 'filesystem'`)
  - Session data stored in `/tmp/flask_session`
  - Session signing enabled for security (`SESSION_USE_SIGNER = True`)
  - Non-permanent sessions (cleared on browser close)
- **Email Routing Flow**:
  1. `/` - Main form (GET)
  2. `/test-connection` - Test SMTP credentials without sending email (POST, returns JSON)
  3. `/preview` - Store form data in session and show preview (POST)
  4. `/send` - Retrieve session data, send email, and clear credentials from session (POST)

**Rationale**: Session storage allows form data to persist between preview and send actions without requiring hidden form fields or URL parameters, improving security for sensitive SMTP credentials.

### Email Sending Mechanism

**Problem**: Need to support various SMTP servers with different authentication requirements.

**Solution**: Configurable SMTP client using Python's built-in `smtplib`.

**Implementation Details**:
- **SMTP Configuration**: User-provided server, port, username, and password
- **Email Construction**: Uses `email.mime` for multipart messages supporting HTML content
- **Default Configuration**: Pre-configured for Gmail (smtp.gmail.com:587) but supports any SMTP server
- **Security**: TLS/STARTTLS support for port 587 connections

**Rationale**: Generic SMTP configuration provides maximum flexibility while defaulting to Gmail for ease of use.

### Security Considerations

**Problem**: Handling sensitive SMTP credentials and preventing unauthorized access.

**Solution**: Multi-layered security approach.

**Security Measures**:
- **Secret Key**: Environment-based configuration with fallback (`SECRET_KEY` environment variable)
- **Session Signing**: Cryptographic signing of session cookies to prevent tampering
- **Credential Storage**: Temporary storage in server-side sessions (not client-side cookies)
- **Password Fields**: HTML password input type for credential entry

**Limitations**: 
- No persistent credential storage (credentials cleared after session)
- No encryption at rest for session files
- Development secret key present as fallback (should be changed in production)

## External Dependencies

### Python Packages

- **Flask**: Web framework for routing and templating (core dependency)
- **Flask-Session**: Server-side session management extension
- **smtplib**: Python standard library for SMTP communication (no installation required)
- **email.mime**: Python standard library for email composition (no installation required)

### Third-Party Services

**SMTP Email Servers**: The application integrates with any SMTP server but is pre-configured for:
- Gmail (smtp.gmail.com:587) - Requires app-specific password
- Any standard SMTP server supporting STARTTLS

**Authentication Requirements**: 
- Gmail users must enable 2FA and generate app-specific passwords
- Other providers may have different authentication requirements

### Infrastructure Dependencies

- **Filesystem Access**: Requires write permissions to `/tmp/flask_session` for session storage
- **Network Access**: Outbound connections to SMTP servers on configured ports (typically 587 for TLS)
- **Environment Variables**: 
  - `SECRET_KEY` (optional, defaults to development key)

### Browser Requirements

- Modern browser with HTML5 support
- JavaScript enabled for SMTP connection testing feature
- CSS3 support for styling