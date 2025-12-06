from datetime import datetime
from database import db

class RFP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    requirements = db.Column(db.JSON, nullable=False)  # List of items, quantities, specs
    terms = db.Column(db.JSON, nullable=False)  # Payment terms, warranty, delivery
    status = db.Column(db.String(20), default='draft')  # draft, sent, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    proposals = db.relationship('Proposal', backref='rfp', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'budget': self.budget,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'requirements': self.requirements,
            'terms': self.terms,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'proposals_count': len(self.proposals)
        }

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    categories = db.Column(db.JSON, nullable=False)  # List of what they supply
    rating = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    proposals = db.relationship('Proposal', backref='vendor', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'categories': self.categories,
            'rating': self.rating,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'proposals_count': len(self.proposals)
        }

class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfp_id = db.Column(db.Integer, db.ForeignKey('rfp.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    original_email_content = db.Column(db.Text, nullable=False)
    parsed_data = db.Column(db.JSON, nullable=False)  # Pricing, terms, items
    total_price = db.Column(db.Float, nullable=False)
    delivery_time = db.Column(db.String(100))  # e.g., "30 days"
    warranty = db.Column(db.String(200))
    ai_score = db.Column(db.Float)  # 0-100
    ai_notes = db.Column(db.Text)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rfp_id': self.rfp_id,
            'vendor_id': self.vendor_id,
            'vendor': self.vendor.to_dict() if self.vendor else None,
            'original_email_content': self.original_email_content,
            'parsed_data': self.parsed_data,
            'total_price': self.total_price,
            'delivery_time': self.delivery_time,
            'warranty': self.warranty,
            'ai_score': self.ai_score,
            'ai_notes': self.ai_notes,
            'received_at': self.received_at.isoformat()
        }
