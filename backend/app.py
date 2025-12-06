from flask import Flask, render_template, request, jsonify
from flask_mail import Mail
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(
    __name__,
    static_folder='../frontend',
    template_folder='../frontend',
    static_url_path=''  # serve assets (css/js) from root so /css/... works
)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///rfp_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize extensions
mail = Mail(app)
CORS(app)

# Initialize database
from database import db
db.init_app(app)

# Import models and routes
from models import RFP, Vendor, Proposal
from services.email_service import email_service
from routes.rfp_routes import rfp_bp
from routes.vendor_routes import vendor_bp
from routes.proposal_routes import proposal_bp

# Inject Flask-Mail instance into email service so sending works
email_service.mail = mail

# Register blueprints
app.register_blueprint(rfp_bp, url_prefix='/api')
app.register_blueprint(vendor_bp, url_prefix='/api')
app.register_blueprint(proposal_bp, url_prefix='/api')

# Serve frontend pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-rfp')
def create_rfp():
    return render_template('create-rfp.html')

@app.route('/vendors')
def vendors():
    return render_template('vendors.html')

@app.route('/send-rfp')
def send_rfp():
    return render_template('send-rfp.html')

@app.route('/proposals')
def proposals():
    return render_template('proposals.html')

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
