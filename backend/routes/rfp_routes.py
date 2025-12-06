from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from database import db
from models import RFP
from services.ai_service import ai_service
from services.email_service import email_service

rfp_bp = Blueprint('rfp', __name__)

@rfp_bp.route('/rfp/create', methods=['POST'])
def create_rfp():
    """Create RFP from natural language"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({'error': 'Description is required'}), 400
        
        # Use AI to parse natural language
        parsed_data = ai_service.parse_natural_language_to_rfp(data['description'])
        
        # Parse deadline
        deadline = None
        if parsed_data.get('deadline'):
            try:
                deadline = datetime.strptime(parsed_data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                # Try other date formats
                try:
                    deadline = datetime.strptime(parsed_data['deadline'], '%m/%d/%Y').date()
                except ValueError:
                    # Default to 30 days from today if parsing fails
                    deadline = date.today() + timedelta(days=30)
        
        # Create RFP
        rfp = RFP(
            title=parsed_data.get('title', 'Untitled RFP'),
            description=data['description'],
            budget=float(parsed_data.get('budget', 0)),
            deadline=deadline,
            requirements=parsed_data.get('items', []),
            terms={
                'payment_terms': parsed_data.get('payment_terms', ''),
                'warranty': parsed_data.get('warranty', ''),
                'special_conditions': parsed_data.get('special_conditions', '')
            },
            status='draft'
        )
        
        db.session.add(rfp)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'rfp': rfp.to_dict(),
            'ai_parsed': parsed_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rfp_bp.route('/rfp/list', methods=['GET'])
def list_rfps():
    """Get all RFPs"""
    try:
        rfps = RFP.query.order_by(RFP.created_at.desc()).all()
        return jsonify({
            'success': True,
            'rfps': [rfp.to_dict() for rfp in rfps]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rfp_bp.route('/rfp/<int:rfp_id>', methods=['GET'])
def get_rfp(rfp_id):
    """Get specific RFP"""
    try:
        rfp = RFP.query.get_or_404(rfp_id)
        return jsonify({
            'success': True,
            'rfp': rfp.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rfp_bp.route('/rfp/<int:rfp_id>/update', methods=['PUT'])
def update_rfp(rfp_id):
    """Update RFP"""
    try:
        rfp = RFP.query.get_or_404(rfp_id)
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            rfp.title = data['title']
        if 'description' in data:
            rfp.description = data['description']
        if 'budget' in data:
            rfp.budget = float(data['budget'])
        if 'deadline' in data:
            try:
                rfp.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid deadline format. Use YYYY-MM-DD'}), 400
        if 'requirements' in data:
            rfp.requirements = data['requirements']
        if 'terms' in data:
            rfp.terms = data['terms']
        if 'status' in data:
            rfp.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'rfp': rfp.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rfp_bp.route('/rfp/<int:rfp_id>/send', methods=['POST'])
def send_rfp(rfp_id):
    """Send RFP to selected vendors"""
    try:
        rfp = RFP.query.get_or_404(rfp_id)
        data = request.get_json()
        
        if not data or 'vendor_ids' not in data:
            return jsonify({'error': 'Vendor IDs are required'}), 400
        
        vendor_ids = data['vendor_ids']
        if not vendor_ids:
            return jsonify({'error': 'At least one vendor must be selected'}), 400
        
        from models import Vendor
        
        # Get vendors
        vendors = Vendor.query.filter(Vendor.id.in_(vendor_ids)).all()
        
        if len(vendors) != len(vendor_ids):
            return jsonify({'error': 'One or more vendors not found'}), 404
        
        # Send emails
        sent_count = 0
        failed_vendors = []
        
        for vendor in vendors:
            if email_service.send_rfp_email(rfp, vendor):
                sent_count += 1
            else:
                failed_vendors.append(vendor.name)
        
        if sent_count > 0:
            rfp.status = 'sent'
            db.session.commit()
        
        return jsonify({
            'success': True,
            'sent_count': sent_count,
            'total_vendors': len(vendors),
            'failed_vendors': failed_vendors,
            'message': f'RFP sent to {sent_count} out of {len(vendors)} vendors'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rfp_bp.route('/rfp/<int:rfp_id>/proposals', methods=['GET'])
def get_rfp_proposals(rfp_id):
    """Get all proposals for a specific RFP"""
    try:
        rfp = RFP.query.get_or_404(rfp_id)
        proposals = [proposal.to_dict() for proposal in rfp.proposals]
        
        return jsonify({
            'success': True,
            'proposals': proposals,
            'rfp': rfp.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rfp_bp.route('/email/receive', methods=['POST'])
def receive_email():
    """Webhook endpoint to receive emails (alternative to IMAP polling)"""
    try:
        data = request.get_json()
        
        # This would handle incoming email webhooks
        # For now, trigger email checking
        processed_count = email_service.check_incoming_emails()
        
        return jsonify({
            'success': True,
            'processed_emails': processed_count,
            'message': f'Processed {processed_count} new emails'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rfp_bp.route('/email/check', methods=['POST'])
def check_emails():
    """Manually trigger email checking"""
    try:
        processed_count = email_service.check_incoming_emails()
        
        return jsonify({
            'success': True,
            'processed_emails': processed_count,
            'message': f'Processed {processed_count} new emails'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
