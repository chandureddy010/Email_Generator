"""
Main Flask application for AI Email Generator.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename

# Import configuration
from config import Config

# Import authentication modules
from auth.google_auth import GoogleAuth
from auth.gmail_service import GmailService

# Import AI agent modules
from ai_agent.email_generator import EmailGenerator

# Import utility modules
from utils.file_handler import FileHandler
from utils.validators import EmailValidator

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services with error handling
try:
    google_auth = GoogleAuth(app.config)
    email_generator = EmailGenerator(app.config['OPENROUTER_API_KEY'])
    file_handler = FileHandler()
    email_validator = EmailValidator()
    
    print("✓ All services initialized successfully")
    
except Exception as e:
    print(f"✗ Error initializing services: {str(e)}")
    raise

@app.route('/')
def index():
    """Main page - show login or email generator interface."""
    try:
        if 'credentials' not in session:
            return render_template('login.html')
        
        return render_template(
            'index.html', 
            email_types=app.config['EMAIL_TYPES']
        )
    except Exception as e:
        flash(f'Error loading page: {str(e)}', 'error')
        return render_template('login.html')

@app.route('/login')
def login():
    """Initiate Google OAuth login process."""
    try:
        auth_url = google_auth.get_authorization_url()
        return redirect(auth_url)
    except Exception as e:
        flash(f'Login failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth callback from Google."""
    try:
        # Get the full callback URL
        callback_url = request.url
        
        # Handle the callback and get credentials
        credentials = google_auth.handle_callback(callback_url)
        
        # Store credentials in session
        session['credentials'] = credentials
        session.permanent = True
        
        # Test Gmail connection
        try:
            gmail_service = GmailService(credentials)
            user_profile = gmail_service.get_user_profile()
            if user_profile:
                session['user_email'] = user_profile['email']
                flash(f'Successfully logged in as {user_profile["email"]}!', 'success')
            else:
                flash('Login successful, but could not retrieve user profile.', 'warning')
        except Exception as gmail_error:
            print(f"Gmail service test failed: {str(gmail_error)}")
            flash('Login successful, but Gmail access may be limited.', 'warning')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Authentication failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Log out user and clear session."""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/generate_emails', methods=['POST'])
def generate_emails():
    """Generate emails based on user input."""
    if 'credentials' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    
    try:
        # Get form data
        email_type = request.form.get('email_type')
        custom_instructions = request.form.get('custom_instructions', '').strip()
        email_mode = request.form.get('email_mode', 'single')
        
        # Validate email type
        if email_type not in app.config['EMAIL_TYPES']:
            flash('Invalid email type selected.', 'error')
            return redirect(url_for('index'))
        
        # Get recipient emails based on mode
        emails = []
        if email_mode == 'single':
            single_email = request.form.get('single_email', '').strip()
            if not single_email:
                flash('Please enter a recipient email address.', 'error')
                return redirect(url_for('index'))
            
            if not email_validator.is_valid(single_email):
                flash('Please enter a valid email address.', 'error')
                return redirect(url_for('index'))
            
            emails = [single_email.lower()]
            
        elif email_mode == 'bulk':
            # Handle file upload
            if 'bulk_file' not in request.files or not request.files['bulk_file'].filename:
                flash('Please upload a file with email addresses.', 'error')
                return redirect(url_for('index'))
            
            file = request.files['bulk_file']
            try:
                emails = file_handler.process_bulk_file(file)
                flash(f'Successfully loaded {len(emails)} email addresses from file.', 'success')
            except ValueError as ve:
                flash(str(ve), 'error')
                return redirect(url_for('index'))
        
        if not emails:
            flash('No valid email addresses found.', 'error')
            return redirect(url_for('index'))
        
        # Get sender name from user profile
        sender_name = session.get('user_email', '').split('@')[0].replace('.', ' ').title()
        
        # Generate emails
        flash('Generating emails... This may take a moment.', 'info')
        
        if len(emails) == 1:
            # Single email generation
            email_content = email_generator.generate_email(
                email_type=email_type,
                recipient_email=emails[0],
                custom_instructions=custom_instructions,
                sender_name=sender_name
            )
            
            generated_emails = [{
                'recipient': emails[0],
                'subject': email_content['subject'],
                'body': email_content['body'],
                'email_type': email_type
            }]
        else:
            # Bulk email generation
            generated_emails = email_generator.generate_bulk_emails(
                email_type=email_type,
                email_list=emails,
                custom_instructions=custom_instructions,
                sender_name=sender_name
            )
        
        # Store generated emails in session
        session['generated_emails'] = generated_emails
        session['generation_settings'] = {
            'email_type': email_type,
            'custom_instructions': custom_instructions,
            'sender_name': sender_name
        }
        
        flash(f'Successfully generated {len(generated_emails)} emails!', 'success')
        return render_template('generate.html', emails=generated_emails)
        
    except Exception as e:
        flash(f'Error generating emails: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/send_emails', methods=['POST'])
def send_emails():
    """Send generated emails through Gmail API."""
    if 'credentials' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    
    generated_emails = session.get('generated_emails', [])
    if not generated_emails:
        flash('No emails to send. Please generate emails first.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Initialize Gmail service
        gmail_service = GmailService(session['credentials'])
        
        # Send emails
        sent_count = 0
        failed_emails = []
        
        for email_data in generated_emails:
            try:
                success = gmail_service.send_email(
                    to_email=email_data['recipient'],
                    subject=email_data['subject'],
                    body=email_data['body']
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_emails.append(email_data['recipient'])
                    
            except Exception as send_error:
                print(f"Error sending email to {email_data['recipient']}: {str(send_error)}")
                failed_emails.append(email_data['recipient'])
        
        # Provide feedback
        total_count = len(generated_emails)
        
        if sent_count == total_count:
            flash(f'All {sent_count} emails sent successfully!', 'success')
        elif sent_count > 0:
            flash(f'{sent_count} out of {total_count} emails sent successfully.', 'warning')
            if failed_emails:
                flash(f'Failed to send to: {", ".join(failed_emails[:5])}{"..." if len(failed_emails) > 5 else ""}', 'error')
        else:
            flash('No emails were sent successfully. Please check your Gmail permissions and try again.', 'error')
            return redirect(url_for('generate_emails'))
        
        # Clear generated emails from session
        session.pop('generated_emails', None)
        
        return render_template(
            'success.html', 
            sent_count=sent_count, 
            total_count=total_count,
            failed_emails=failed_emails
        )
        
    except Exception as e:
        flash(f'Error sending emails: {str(e)}', 'error')
        return redirect(url_for('generate_emails'))

@app.route('/test_services')
def test_services():
    """Test all services connectivity (for debugging)."""
    if not app.config.get('FLASK_DEBUG'):
        return "Service testing only available in debug mode.", 403
    
    results = {}
    
    # Test OpenRouter API
    try:
        ai_test = email_generator.test_api_connection()
        results['openrouter'] = 'Connected' if ai_test else 'Failed'
    except Exception as e:
        results['openrouter'] = f'Error: {str(e)}'
    
    # Test Google OAuth (if credentials available)
    if 'credentials' in session:
        try:
            gmail_service = GmailService(session['credentials'])
            gmail_test = gmail_service.test_connection()
            results['gmail'] = 'Connected' if gmail_test else 'Failed'
        except Exception as e:
            results['gmail'] = f'Error: {str(e)}'
    else:
        results['gmail'] = 'Not authenticated'
    
    return jsonify(results)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'app_name': app.config['APP_NAME'],
        'debug_mode': app.config['FLASK_DEBUG']
    })

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

# Session configuration
@app.before_request
def configure_session():
    """Configure session settings."""
    session.permanent = True
    app.permanent_session_lifetime = 3600  # 1 hour

if __name__ == '__main__':
    print("🚀 Starting AI Email Generator...")
    print(f"📧 OpenRouter API: {'✓ Configured' if app.config.get('OPENROUTER_API_KEY') else '✗ Missing'}")
    print(f"🔐 Google OAuth: {'✓ Configured' if app.config.get('GOOGLE_CLIENT_ID') else '✗ Missing'}")
    print(f"📁 Upload Directory: {app.config['UPLOAD_FOLDER']}")
    print(f"🌐 Debug Mode: {app.config['FLASK_DEBUG']}")
    
    app.run(
        debug=app.config['FLASK_DEBUG'],
        host='0.0.0.0',
        port=5000
    )

