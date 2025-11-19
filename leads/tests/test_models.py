# leads/tests/test_models.py
"""
Basic tests for Lead models
Only tests what actually works in production
"""

from django.test import TestCase
from leads.models import Lead, LeadList, LeadListItem


class LeadModelTest(TestCase):
    """Test Lead model basic functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.lead_data = {
            'external_id': 'test_123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'current_title': 'Software Engineer',
            'current_company': 'Tech Corp',
            'linkedin_url': 'linkedin.com/in/johndoe',
            'location': 'San Francisco',
            'country': 'United States',
            'industry': 'Technology',
            'seniority_level': 'senior',
        }
    
    def test_create_lead(self):
        """Test creating a lead"""
        lead = Lead.objects.create(**self.lead_data)
        
        self.assertEqual(lead.first_name, 'John')
        self.assertEqual(lead.last_name, 'Doe')
        self.assertEqual(lead.external_id, 'test_123')
        self.assertIsNotNone(lead.id)
    
    def test_full_name_generation(self):
        """Test full_name is generated"""
        lead = Lead.objects.create(**self.lead_data)
        
        self.assertEqual(lead.full_name, 'John Doe')
    
    def test_get_full_name_method(self):
        """Test get_full_name() method"""
        lead = Lead(**self.lead_data)
        
        self.assertEqual(lead.get_full_name(), 'John Doe')
    
    def test_unique_external_id(self):
        """Test external_id uniqueness"""
        Lead.objects.create(**self.lead_data)
        
        # Try to create duplicate
        with self.assertRaises(Exception):  # Can be IntegrityError or ValidationError
            Lead.objects.create(**self.lead_data)


class LeadListTest(TestCase):
    """Test LeadList model"""
    
    def test_create_list(self):
        """Test creating a lead list"""
        lead_list = LeadList.objects.create(
            name='Test List',
            description='Test Description'
        )
        
        self.assertEqual(lead_list.name, 'Test List')
        self.assertIsNotNone(lead_list.slug)
    
    def test_slug_auto_generated(self):
        """Test slug is auto-generated"""
        lead_list = LeadList.objects.create(name='My Test List')
        
        self.assertEqual(lead_list.slug, 'my-test-list')
    
    def test_get_lead_count(self):
        """Test get_lead_count method"""
        lead_list = LeadList.objects.create(name='Test List')
        
        # Initially empty
        self.assertEqual(lead_list.get_lead_count(), 0)
        
        # Add a lead
        lead = Lead.objects.create(
            external_id='test_456',
            first_name='Jane',
            last_name='Smith'
        )
        LeadListItem.objects.create(lead=lead, lead_list=lead_list)
        
        # Now should be 1
        self.assertEqual(lead_list.get_lead_count(), 1)


class LeadListItemTest(TestCase):
    """Test LeadListItem model"""
    
    def setUp(self):
        """Set up test data"""
        self.lead = Lead.objects.create(
            external_id='test_789',
            first_name='John',
            last_name='Doe'
        )
        self.lead_list = LeadList.objects.create(name='Test List')
    
    def test_create_list_item(self):
        """Test creating a list item"""
        item = LeadListItem.objects.create(
            lead=self.lead,
            lead_list=self.lead_list,
            notes='Test note'
        )
        
        self.assertEqual(item.lead, self.lead)
        self.assertEqual(item.lead_list, self.lead_list)
        self.assertEqual(item.notes, 'Test note')
    
    def test_unique_together(self):
        """Test lead+list uniqueness"""
        LeadListItem.objects.create(
            lead=self.lead,
            lead_list=self.lead_list
        )
        
        # Try duplicate
        with self.assertRaises(Exception):
            LeadListItem.objects.create(
                lead=self.lead,
                lead_list=self.lead_list
            )


# Run with: python manage.py test leads.tests.test_models