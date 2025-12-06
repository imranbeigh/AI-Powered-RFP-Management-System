from flask import Blueprint, request, jsonify
from database import db
from models import Vendor

vendor_bp = Blueprint('vendor', __name__)

@vendor_bp.route('/vendor/add', methods=['POST'])
def add_vendor():
    """Add new vendor"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vendor data is required'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        existing_vendor = Vendor.query.filter_by(email=data['email']).first()
        if existing_vendor:
            return jsonify({'error': 'Vendor with this email already exists'}), 400
        
        # Create vendor
        vendor = Vendor(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            company=data.get('company', ''),
            categories=data.get('categories', []),
            rating=float(data.get('rating', 0.0)),
            notes=data.get('notes', '')
        )
        
        db.session.add(vendor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vendor': vendor.to_dict(),
            'message': 'Vendor added successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendor_bp.route('/vendor/list', methods=['GET'])
def list_vendors():
    """Get all vendors"""
    try:
        vendors = Vendor.query.order_by(Vendor.name).all()
        return jsonify({
            'success': True,
            'vendors': [vendor.to_dict() for vendor in vendors]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendor_bp.route('/vendor/<int:vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    """Get specific vendor"""
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        return jsonify({
            'success': True,
            'vendor': vendor.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendor_bp.route('/vendor/<int:vendor_id>', methods=['PUT'])
def update_vendor(vendor_id):
    """Update vendor"""
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vendor data is required'}), 400
        
        # Update fields
        if 'name' in data:
            vendor.name = data['name']
        if 'email' in data:
            # Check if email is already used by another vendor
            existing_vendor = Vendor.query.filter(
                Vendor.email == data['email'],
                Vendor.id != vendor_id
            ).first()
            if existing_vendor:
                return jsonify({'error': 'Email already used by another vendor'}), 400
            vendor.email = data['email']
        if 'phone' in data:
            vendor.phone = data['phone']
        if 'company' in data:
            vendor.company = data['company']
        if 'categories' in data:
            vendor.categories = data['categories']
        if 'rating' in data:
            vendor.rating = float(data['rating'])
        if 'notes' in data:
            vendor.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vendor': vendor.to_dict(),
            'message': 'Vendor updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendor_bp.route('/vendor/<int:vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id):
    """Delete vendor"""
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        
        # Check if vendor has proposals
        if vendor.proposals:
            return jsonify({
                'error': 'Cannot delete vendor with existing proposals'
            }), 400
        
        db.session.delete(vendor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vendor deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendor_bp.route('/vendor/search', methods=['GET'])
def search_vendors():
    """Search vendors by name, company, or categories"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        
        vendors_query = Vendor.query
        
        if query:
            vendors_query = vendors_query.filter(
                (Vendor.name.ilike(f'%{query}%')) |
                (Vendor.company.ilike(f'%{query}%')) |
                (Vendor.email.ilike(f'%{query}%'))
            )
        
        if category:
            vendors_query = vendors_query.filter(
                Vendor.categories.contains([category])
            )
        
        vendors = vendors_query.order_by(Vendor.name).all()
        
        return jsonify({
            'success': True,
            'vendors': [vendor.to_dict() for vendor in vendors],
            'count': len(vendors)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendor_bp.route('/vendor/categories', methods=['GET'])
def get_categories():
    """Get all unique vendor categories"""
    try:
        vendors = Vendor.query.all()
        all_categories = set()
        
        for vendor in vendors:
            if vendor.categories:
                all_categories.update(vendor.categories)
        
        categories = sorted(list(all_categories))
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
