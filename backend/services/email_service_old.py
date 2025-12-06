import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os
from datetime import datetime
from database import db
from models import RFP, Vendor, Proposal
from services.ai_service import ai_service

class EmailService:
    def __init__(self):
        self.imap_server = None
        self.imap_user = os.getenv('MAIL_USERNAME')
        self.imap_password = os.getenv('MAIL_PASSWORD')
        self.imap_host = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        self.imap_port = int(os.getenv('IMAP_PORT', 993))
    
    def send_rfp_email(self, rfp: RFP, vendor: Vendor) -> bool:
        """Send RFP to vendor via email"""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = vendor.email
            msg['Subject'] = f"Request for Proposal: {rfp.title}"
            
            # Email body
            body = f"""
Dear {vendor.name},

We are pleased to invite you to submit a proposal for the following requirement:

TITLE: {rfp.title}
DESCRIPTION: {rfp.description}
BUDGET: ${rfp.budget:,.2f}
DEADLINE: {rfp.deadline}

REQUIREMENTS:
{self._format_requirements(rfp.requirements)}

TERMS:
{self._format_terms(rfp.terms)}

Please submit your proposal including:
- Detailed pricing breakdown
- Delivery timeline
- Warranty information
- Payment terms
- Any special conditions

Submit your response by replying to this email before the deadline.

Best regards,
Procurement Team
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send email to {vendor.email}: {str(e)}")
            return False
    
    def _format_requirements(self, requirements: list) -> str:
        """Format requirements for email"""
        if not requirements:
            return "No specific requirements listed"
        
        formatted = []
        for item in requirements:
            formatted.append(f"- {item.get('name', '')}: {item.get('quantity', 0)} units")
            if item.get('specs'):
                formatted.append(f"  Specifications: {item['specs']}")
        
        return '\n'.join(formatted)
    
    def _format_terms(self, terms: dict) -> str:
        """Format terms for email"""
        formatted = []
        for key, value in terms.items():
            if value:
                formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return '\n'.join(formatted) if formatted else "Standard terms apply"
    
    def check_incoming_emails(self) -> int:
        """Check for incoming vendor responses and process them"""
        try:
            # Connect to IMAP server
            self.imap_server = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            self.imap_server.login(self.imap_user, self.imap_password)
            self.imap_server.select('INBOX')
            
            # Search for emails from last 24 hours
            since_date = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
            search_criteria = f'(SINCE {since_date})'
            
            status, messages = self.imap_server.search(None, search_criteria)
            
            if status != 'OK':
                return 0
            
            email_ids = messages[0].split()
            processed_count = 0
            
            for email_id in email_ids[-10:]:  # Process last 10 emails
                try:
                    # Fetch email
                    status, msg_data = self.imap_server.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract email content
                    sender = msg['From']
                    subject = msg['Subject']
                    body = self._extract_email_body(msg)
                    
                    # Check if this is a vendor response
                    if self._is_vendor_response(sender, subject):
                        if self._process_vendor_response(sender, subject, body):
                            processed_count += 1
                
                except Exception as e:
                    print(f"Error processing email {email_id}: {str(e)}")
                    continue
            
            # Close connection
            self.imap_server.close()
            self.imap_server.logout()
            
            return processed_count
            
        except Exception as e:
            print(f"Error checking emails: {str(e)}")
            return 0
    
    def _extract_email_body(self, msg) -> str:
        """Extract text body from email message"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        continue
        else:
            if msg.get_content_type() == "text/plain":
                try:
                    body = msg.get_payload(decode=True).decode()
                except:
                    pass
        
        return body
    
    def _is_vendor_response(self, sender: str, subject: str) -> bool:
        """Check if email is likely a vendor response"""
        # Check if sender is a known vendor
        email_match = re.search(r'<([^>]+)>', sender)
        sender_email = email_match.group(1) if email_match else sender
        
        vendor = Vendor.query.filter_by(email=sender_email).first()
        if not vendor:
            return False
        
        # Check subject for RFP-related keywords
        rfp_keywords = ['proposal', 'quote', 'quotation', 'bid', 'offer', 'rfp', 'request for proposal']
        subject_lower = subject.lower()
        
        return any(keyword in subject_lower for keyword in rfp_keywords)
    
    def _process_vendor_response(self, sender: str, subject: str, body: str) -> bool:
        """Process vendor response email"""
        try:
            # Extract vendor email
            email_match = re.search(r'<([^>]+)>', sender)
            sender_email = email_match.group(1) if email_match else sender
            
            # Find vendor
            vendor = Vendor.query.filter_by(email=sender_email).first()
            if not vendor:
                return False
            
            # Parse email content with AI
            parsed_data = ai_service.parse_vendor_response(body)
            
            # Find the RFP this is responding to
            # This is a simplified approach - in production, you'd use email threading or unique IDs
            rfps = RFP.query.filter(RFP.status.in_(['sent'])).all()
            
            for rfp in rfps:
                # Check if this vendor already has a proposal for this RFP
                existing_proposal = Proposal.query.filter_by(
                    rfp_id=rfp.id, 
                    vendor_id=vendor.id
                ).first()
                
                if existing_proposal:
                    # Update existing proposal
                    existing_proposal.original_email_content = body
                    existing_proposal.parsed_data = parsed_data
                    existing_proposal.total_price = parsed_data.get('total_price', 0)
                    existing_proposal.delivery_time = parsed_data.get('delivery_time', '')
                    existing_proposal.warranty = parsed_data.get('warranty', '')
                    existing_proposal.received_at = datetime.utcnow()
                else:
                    # Create new proposal
                    proposal = Proposal(
                        rfp_id=rfp.id,
                        vendor_id=vendor.id,
                        original_email_content=body,
                        parsed_data=parsed_data,
                        total_price=parsed_data.get('total_price', 0),
                        delivery_time=parsed_data.get('delivery_time', ''),
                        warranty=parsed_data.get('warranty', '')
                    )
                    db.session.add(proposal)
                
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing vendor response: {str(e)}")
            return False

# Singleton instance
email_service = EmailService()
