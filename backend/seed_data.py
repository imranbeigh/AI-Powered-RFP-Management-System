#!/usr/bin/env python3
"""
Seed data script for AI-Powered RFP Management System
Creates sample vendors and RFPs for testing
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import RFP, Vendor, Proposal

def create_sample_vendors():
    """Create sample vendor data"""
    vendors = [
        {
            'name': 'John Smith',
            'email': 'john.smith@dell.com',
            'phone': '+1-555-0101',
            'company': 'Dell Technologies',
            'categories': ['IT Hardware', 'Laptops', 'Servers'],
            'rating': 4.5,
            'notes': 'Reliable vendor for enterprise hardware'
        },
        {
            'name': 'Sarah Johnson',
            'email': 'sarah.j@hp.com',
            'phone': '+1-555-0102',
            'company': 'HP Inc.',
            'categories': ['IT Hardware', 'Laptops', 'Printers'],
            'rating': 4.2,
            'notes': 'Good pricing on bulk orders'
        },
        {
            'name': 'Michael Chen',
            'email': 'mchen@lenovo.com',
            'phone': '+1-555-0103',
            'company': 'Lenovo Group',
            'categories': ['IT Hardware', 'Laptops', 'Workstations'],
            'rating': 4.0,
            'notes': 'Excellent customer support'
        },
        {
            'name': 'Emily Davis',
            'email': 'emily@officedepot.com',
            'phone': '+1-555-0104',
            'company': 'Office Depot',
            'categories': ['Office Furniture', 'Supplies'],
            'rating': 3.8,
            'notes': 'Wide range of office products'
        },
        {
            'name': 'Robert Wilson',
            'email': 'rwilson@microsoft.com',
            'phone': '+1-555-0105',
            'company': 'Microsoft Corporation',
            'categories': ['Software', 'Cloud Services'],
            'rating': 4.7,
            'notes': 'Premium software solutions'
        }
    ]

    created_vendors = []
    for vendor_data in vendors:
        # Check if vendor already exists
        existing = Vendor.query.filter_by(email=vendor_data['email']).first()
        if not existing:
            vendor = Vendor(**vendor_data)
            db.session.add(vendor)
            created_vendors.append(vendor)
        else:
            created_vendors.append(existing)
    
    db.session.commit()
    print(f"Created {len(created_vendors)} vendors")
    return created_vendors

def create_sample_rfps():
    """Create sample RFP data"""
    rfps = [
        {
            'title': 'Office IT Equipment Upgrade',
            'description': 'Need to upgrade office IT equipment including laptops, monitors, and accessories for 50 employees.',
            'budget': 75000.0,
            'deadline': (datetime.now() + timedelta(days=30)).date(),
            'requirements': [
                {'name': 'Laptops', 'quantity': 50, 'specs': '16GB RAM, 512GB SSD, Intel i7'},
                {'name': 'Monitors', 'quantity': 50, 'specs': '27-inch 4K display'},
                {'name': 'Docking Stations', 'quantity': 50, 'specs': 'USB-C with multiple ports'}
            ],
            'terms': {
                'payment_terms': 'Net 30 days',
                'warranty': '3 years manufacturer warranty',
                'special_conditions': 'Installation and setup included'
            },
            'status': 'draft'
        },
        {
            'title': 'Office Furniture Refresh',
            'description': 'Replace existing office furniture for better ergonomics and modern look.',
            'budget': 45000.0,
            'deadline': (datetime.now() + timedelta(days=45)).date(),
            'requirements': [
                {'name': 'Ergonomic Chairs', 'quantity': 60, 'specs': 'Adjustable height, lumbar support'},
                {'name': 'Standing Desks', 'quantity': 30, 'specs': 'Electric height adjustment'},
                {'name': 'Meeting Tables', 'quantity': 5, 'specs': '8-person capacity, cable management'}
            ],
            'terms': {
                'payment_terms': '50% upfront, 50% on delivery',
                'warranty': '5 years warranty',
                'special_conditions': 'Removal of old furniture included'
            },
            'status': 'draft'
        },
        {
            'title': 'Software Licenses Annual Renewal',
            'description': 'Annual renewal of software licenses for all employees.',
            'budget': 25000.0,
            'deadline': (datetime.now() + timedelta(days=15)).date(),
            'requirements': [
                {'name': 'Office 365 Licenses', 'quantity': 100, 'specs': 'Business Premium'},
                {'name': 'Adobe Creative Cloud', 'quantity': 10, 'specs': 'All Apps plan'},
                {'name': 'Antivirus Software', 'quantity': 150, 'specs': 'Enterprise edition'}
            ],
            'terms': {
                'payment_terms': 'Annual payment',
                'warranty': '24/7 support included',
                'special_conditions': 'Training sessions included'
            },
            'status': 'draft'
        }
    ]

    created_rfps = []
    for rfp_data in rfps:
        rfp = RFP(**rfp_data)
        db.session.add(rfp)
        created_rfps.append(rfp)
    
    db.session.commit()
    print(f"Created {len(created_rfps)} RFPs")
    return created_rfps

def create_sample_proposals(vendors, rfps):
    """Create sample proposal data for testing"""
    if not vendors or not rfps:
        print("No vendors or RFPs available for creating proposals")
        return

    # Create proposals for the first RFP
    rfp = rfps[0]
    
    sample_proposals = [
        {
            'vendor_id': vendors[0].id,  # Dell
            'original_email_content': '''Dear Procurement Team,

Thank you for the opportunity to bid on your Office IT Equipment Upgrade. Dell is pleased to offer the following:

Laptops (50 units): Dell Latitude 7420 with 16GB RAM, 512GB SSD, Intel i7 - $1,200 each
Monitors (50 units): Dell UltraSharp 27" 4K - $600 each
Docking Stations (50 units): Dell WD19 - $200 each

Total: $100,000
Delivery: 2 weeks
Warranty: 3 years with next business day support
Payment: Net 30 days

Best regards,
John Smith
Dell Technologies''',
            'parsed_data': {
                'items': [
                    {'name': 'Laptops', 'quantity': 50, 'unit_price': 1200, 'total_price': 60000},
                    {'name': 'Monitors', 'quantity': 50, 'unit_price': 600, 'total_price': 30000},
                    {'name': 'Docking Stations', 'quantity': 50, 'unit_price': 200, 'total_price': 10000}
                ],
                'total_price': 100000,
                'delivery_time': '2 weeks',
                'warranty': '3 years with next business day support',
                'payment_terms': 'Net 30 days',
                'special_notes': 'Includes installation service'
            },
            'total_price': 100000.0,
            'delivery_time': '2 weeks',
            'warranty': '3 years with next business day support',
            'ai_score': 85.0,
            'ai_notes': 'Good pricing but slightly over budget. Excellent warranty terms.'
        },
        {
            'vendor_id': vendors[1].id,  # HP
            'original_email_content': '''Dear Procurement Team,

HP is excited to submit our proposal for your Office IT Equipment Upgrade:

HP EliteBook 840 G9 (50 units): $1,100 each
HP EliteDisplay 27" 4K (50 units): $550 each
HP USB-C Dock (50 units): $180 each

Total: $91,500
Delivery: 1 week
Warranty: 3 years standard
Payment: Net 30

Thank you,
Sarah Johnson
HP Inc.''',
            'parsed_data': {
                'items': [
                    {'name': 'HP EliteBook 840 G9', 'quantity': 50, 'unit_price': 1100, 'total_price': 55000},
                    {'name': 'HP EliteDisplay 27" 4K', 'quantity': 50, 'unit_price': 550, 'total_price': 27500},
                    {'name': 'HP USB-C Dock', 'quantity': 50, 'unit_price': 180, 'total_price': 9000}
                ],
                'total_price': 91500,
                'delivery_time': '1 week',
                'warranty': '3 years standard',
                'payment_terms': 'Net 30',
                'special_notes': 'Quick delivery available'
            },
            'total_price': 91500.0,
            'delivery_time': '1 week',
            'warranty': '3 years standard',
            'ai_score': 92.0,
            'ai_notes': 'Best price point with fast delivery. Under budget.'
        },
        {
            'vendor_id': vendors[2].id,  # Lenovo
            'original_email_content': '''Dear Procurement Team,

Lenovo offers the following for your IT upgrade:

ThinkPad X1 Carbon (50 units): $1,300 each
ThinkVision P27 4K (50 units): $650 each
ThinkPad USB-C Dock (50 units): $220 each

Total: $108,500
Delivery: 3 weeks
Warranty: 3 years premium support
Payment: Net 30

Best regards,
Michael Chen
Lenovo''',
            'parsed_data': {
                'items': [
                    {'name': 'ThinkPad X1 Carbon', 'quantity': 50, 'unit_price': 1300, 'total_price': 65000},
                    {'name': 'ThinkVision P27 4K', 'quantity': 50, 'unit_price': 650, 'total_price': 32500},
                    {'name': 'ThinkPad USB-C Dock', 'quantity': 50, 'unit_price': 220, 'total_price': 11000}
                ],
                'total_price': 108500,
                'delivery_time': '3 weeks',
                'warranty': '3 years premium support',
                'payment_terms': 'Net 30',
                'special_notes': 'Premium business laptops'
            },
            'total_price': 108500.0,
            'delivery_time': '3 weeks',
            'warranty': '3 years premium support',
            'ai_score': 78.0,
            'ai_notes': 'Premium quality but higher price and longer delivery time.'
        }
    ]

    created_proposals = []
    for proposal_data in sample_proposals:
        proposal_data['rfp_id'] = rfp.id
        proposal = Proposal(**proposal_data)
        db.session.add(proposal)
        created_proposals.append(proposal)
    
    # Update RFP status to 'sent'
    rfp.status = 'sent'
    
    db.session.commit()
    print(f"Created {len(created_proposals)} proposals for RFP: {rfp.title}")
    return created_proposals

def main():
    """Main function to seed the database"""
    with app.app_context():
        print("Starting database seeding...")
        
        # Create tables
        db.create_all()
        print("Database tables created")
        
        # Create sample data
        vendors = create_sample_vendors()
        rfps = create_sample_rfps()
        
        # Create sample proposals for testing
        create_sample_proposals(vendors, rfps)
        
        print("\nDatabase seeding completed successfully!")
        print("\nSample data created:")
        print(f"- {len(vendors)} vendors")
        print(f"- {len(rfps)} RFPs")
        print(f"- Sample proposals for testing")
        
        print("\nYou can now run the application with: python app.py")

if __name__ == '__main__':
    main()
