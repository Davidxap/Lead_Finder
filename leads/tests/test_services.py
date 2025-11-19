# leads/tests/test_services.py
"""
Service layer tests - Production ready
Based on actual working code, no type errors
"""

from django.test import TestCase
from leads.models import Lead, LeadList, LeadListItem
from leads.services.lead_service import LeadService


class LeadServiceTest(TestCase):
    """Test LeadService - All operations that work in production"""
    
    def setUp(self):
        """Set up test data"""
        self.lead_data = {
            'external_id': 'api_123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'current_title': 'Engineer',
            'current_company': 'Tech Corp',
        }
    
    def test_create_lead(self):
        """Test creating a new lead"""
        lead = LeadService.create_or_update_lead(self.lead_data)
        
        self.assertIsNotNone(lead.id)
        self.assertEqual(lead.external_id, 'api_123')
        self.assertEqual(lead.first_name, 'John')
        self.assertEqual(Lead.objects.count(), 1)
    
    def test_update_existing_lead(self):
        """Test updating an existing lead"""
        lead = LeadService.create_or_update_lead(self.lead_data)
        original_id = lead.id
        
        updated_data = self.lead_data.copy()
        updated_data['current_title'] = 'Senior Engineer'
        
        lead = LeadService.create_or_update_lead(updated_data)
        
        self.assertEqual(lead.id, original_id)
        self.assertEqual(lead.current_title, 'Senior Engineer')
        self.assertEqual(Lead.objects.count(), 1)
    
    def test_add_lead_to_new_list(self):
        """Test adding lead to new list"""
        lead = Lead.objects.create(**self.lead_data)
        
        success, message = LeadService.add_lead_to_list(lead, 'New List')
        
        self.assertTrue(success)
        self.assertTrue(LeadList.objects.filter(name='New List').exists())
    
    def test_add_lead_to_existing_list(self):
        """Test adding lead to existing list"""
        lead = Lead.objects.create(**self.lead_data)
        lead_list = LeadList.objects.create(name='Existing List')
        
        success, message = LeadService.add_lead_to_list(lead, 'Existing List')
        
        self.assertTrue(success)
        self.assertEqual(LeadListItem.objects.filter(lead_list=lead_list).count(), 1)
    
    def test_remove_lead_from_list(self):
        """Test removing lead from list"""
        lead = Lead.objects.create(**self.lead_data)
        lead_list = LeadList.objects.create(name='Test List')
        LeadListItem.objects.create(lead=lead, lead_list=lead_list)
        
        success, message = LeadService.remove_lead_from_list(lead, lead_list)
        
        self.assertTrue(success)
        self.assertFalse(
            LeadListItem.objects.filter(lead=lead, lead_list=lead_list).exists()
        )
    
    def test_create_list(self):
        """Test creating a list"""
        success, message, result = LeadService.create_list('New List', 'Description')
        
        self.assertTrue(success)
        self.assertTrue(LeadList.objects.filter(name='New List').exists())
        
        # Get the created list to verify
        created_list = LeadList.objects.get(name='New List')
        self.assertEqual(created_list.description, 'Description')
    
    def test_create_duplicate_list(self):
        """Test creating duplicate list fails"""
        LeadList.objects.create(name='Duplicate')
        
        success, message, result = LeadService.create_list('Duplicate', 'Test')
        
        self.assertFalse(success)
    
    def test_delete_list(self):
        """Test deleting a list"""
        lead_list = LeadList.objects.create(name='To Delete')
        
        success, message = LeadService.delete_list(lead_list)
        
        self.assertTrue(success)
        self.assertFalse(LeadList.objects.filter(name='To Delete').exists())
    
    def test_bulk_add_leads_to_list(self):
        """Test bulk adding leads"""
        leads = []
        for i in range(5):
            lead = Lead.objects.create(
                external_id=f'test_{i}',
                first_name=f'John{i}',
                last_name='Doe'
            )
            leads.append(lead)
        
        result = LeadService.bulk_add_leads_to_list(leads, 'Bulk List')
        
        self.assertEqual(result['added'], 5)
        self.assertEqual(result['skipped'], 0)


# Run with: python manage.py test leads.tests.test_services