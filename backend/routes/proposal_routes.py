from flask import Blueprint, request, jsonify
from database import db
from models import Proposal, RFP, Vendor
from services.ai_service import ai_service

proposal_bp = Blueprint('proposal', __name__)

@proposal_bp.route('/proposal/list', methods=['GET'])
def list_proposals():
    """Get all proposals"""
    try:
        rfp_id = request.args.get('rfp_id')
        
        if rfp_id:
            proposals = Proposal.query.filter_by(rfp_id=rfp_id).all()
        else:
            proposals = Proposal.query.order_by(Proposal.received_at.desc()).all()
        
        return jsonify({
            'success': True,
            'proposals': [proposal.to_dict() for proposal in proposals]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@proposal_bp.route('/proposal/<int:proposal_id>', methods=['GET'])
def get_proposal(proposal_id):
    """Get specific proposal"""
    try:
        proposal = Proposal.query.get_or_404(proposal_id)
        return jsonify({
            'success': True,
            'proposal': proposal.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@proposal_bp.route('/proposal/parse', methods=['POST'])
def parse_proposal():
    """Parse vendor email with AI"""
    try:
        data = request.get_json()
        
        if not data or 'email_content' not in data:
            return jsonify({'error': 'Email content is required'}), 400
        
        # Parse email content with AI
        parsed_data = ai_service.parse_vendor_response(data['email_content'])
        
        return jsonify({
            'success': True,
            'parsed_data': parsed_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@proposal_bp.route('/proposal/compare', methods=['POST'])
def compare_proposals():
    """AI comparison and recommendation"""
    try:
        data = request.get_json()
        
        if not data or 'rfp_id' not in data:
            return jsonify({'error': 'RFP ID is required'}), 400
        
        rfp_id = data['rfp_id']
        rfp = RFP.query.get_or_404(rfp_id)
        
        # Get all proposals for this RFP
        proposals = Proposal.query.filter_by(rfp_id=rfp_id).all()
        
        if not proposals:
            return jsonify({'error': 'No proposals found for this RFP'}), 404
        
        # Prepare proposals data for AI comparison
        proposals_data = []
        for proposal in proposals:
            proposal_data = {
                'proposal_id': proposal.id,
                'vendor_id': proposal.vendor_id,
                'vendor_name': proposal.vendor.name if proposal.vendor else 'Unknown',
                'total_price': proposal.total_price,
                'delivery_time': proposal.delivery_time,
                'warranty': proposal.warranty,
                'parsed_data': proposal.parsed_data or {},
                'items': proposal.parsed_data.get('items', []) if proposal.parsed_data else [],
                'payment_terms': proposal.parsed_data.get('payment_terms', '') if proposal.parsed_data else '',
                'special_notes': proposal.parsed_data.get('special_notes', '') if proposal.parsed_data else ''
            }
            proposals_data.append(proposal_data)
        
        # Get AI comparison and recommendation
        comparison_result = ai_service.compare_and_recommend(proposals_data)
        
        # Update proposals with AI scores
        rankings = comparison_result.get('rankings', [])
        for ranking in rankings:
            proposal = Proposal.query.filter_by(
                rfp_id=rfp_id,
                vendor_id=ranking['vendor_id']
            ).first()
            if proposal:
                proposal.ai_score = ranking['score']
                proposal.ai_notes = ranking['detailed_analysis']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comparison': comparison_result,
            'proposals': [proposal.to_dict() for proposal in proposals],
            'rfp': rfp.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@proposal_bp.route('/proposal/<int:proposal_id>/score', methods=['PUT'])
def update_proposal_score(proposal_id):
    """Update proposal AI score and notes"""
    try:
        proposal = Proposal.query.get_or_404(proposal_id)
        data = request.get_json()
        
        if 'ai_score' in data:
            proposal.ai_score = float(data['ai_score'])
        if 'ai_notes' in data:
            proposal.ai_notes = data['ai_notes']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'proposal': proposal.to_dict(),
            'message': 'Proposal score updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@proposal_bp.route('/proposal/<int:proposal_id>', methods=['DELETE'])
def delete_proposal(proposal_id):
    """Delete proposal"""
    try:
        proposal = Proposal.query.get_or_404(proposal_id)
        
        db.session.delete(proposal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Proposal deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@proposal_bp.route('/proposal/stats', methods=['GET'])
def get_proposal_stats():
    """Get proposal statistics"""
    try:
        total_proposals = Proposal.query.count()
        
        # Stats by RFP
        rfp_stats = db.session.query(
            RFP.id,
            RFP.title,
            db.func.count(Proposal.id).label('proposal_count'),
            db.func.avg(Proposal.total_price).label('avg_price'),
            db.func.avg(Proposal.ai_score).label('avg_score')
        ).outerjoin(Proposal).group_by(RFP.id).all()
        
        # Stats by vendor
        vendor_stats = db.session.query(
            Vendor.id,
            Vendor.name,
            db.func.count(Proposal.id).label('proposal_count'),
            db.func.avg(Proposal.total_price).label('avg_price'),
            db.func.avg(Proposal.ai_score).label('avg_score')
        ).outerjoin(Proposal).group_by(Vendor.id).all()
        
        return jsonify({
            'success': True,
            'total_proposals': total_proposals,
            'rfp_stats': [
                {
                    'rfp_id': stat.id,
                    'rfp_title': stat.title,
                    'proposal_count': stat.proposal_count or 0,
                    'avg_price': float(stat.avg_price) if stat.avg_price else 0,
                    'avg_score': float(stat.avg_score) if stat.avg_score else 0
                }
                for stat in rfp_stats
            ],
            'vendor_stats': [
                {
                    'vendor_id': stat.id,
                    'vendor_name': stat.name,
                    'proposal_count': stat.proposal_count or 0,
                    'avg_price': float(stat.avg_price) if stat.avg_price else 0,
                    'avg_score': float(stat.avg_score) if stat.avg_score else 0
                }
                for stat in vendor_stats
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
