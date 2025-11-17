# leads/services/lead_service.py
import logging
from typing import Dict, List, Tuple, Optional, Any
from django.db import IntegrityError
from leads.models import Lead, LeadList, LeadListItem

logger = logging.getLogger(__name__)


class LeadService:
    """Service class to handle lead-related business logic."""
    
    @staticmethod
    def create_or_update_lead(lead_data: Dict) -> Lead:
        """Create or update a lead."""
        try:
            external_id = lead_data.get('external_id')
            
            if external_id:
                lead = Lead.objects.filter(external_id=external_id).first()
                if lead:
                    for key, value in lead_data.items():
                        if hasattr(lead, key):
                            setattr(lead, key, value)
                    lead.save()
                    logger.info(f"Updated lead: {lead.full_name}")
                    return lead
            
            valid_fields = {
                'external_id', 'first_name', 'last_name', 'full_name',
                'email', 'phone', 'linkedin_url', 'photo_url',
                'current_title', 'current_company', 'company_linkedin_url',
                'headline', 'location', 'country', 'industry',
                'company_size', 'seniority_level', 'skills', 'bio'
            }
            
            filtered_data = {k: v for k, v in lead_data.items() if k in valid_fields}
            lead = Lead.objects.create(**filtered_data)
            logger.info(f"Created lead: {lead.full_name}")
            return lead
            
        except IntegrityError:
            if external_id:
                return Lead.objects.get(external_id=external_id)
            raise
        except Exception as e:
            logger.error(f"Error creating/updating lead: {str(e)}")
            raise
    
    @staticmethod
    def add_lead_to_list(lead: Lead, list_name: str, notes: str = "") -> Tuple[bool, str]:
        """Add a lead to a list."""
        try:
            lead_list, created = LeadList.objects.get_or_create(
                name=list_name,
                defaults={'description': f'List: {list_name}'}
            )
            
            if created:
                logger.info(f"Created new list: {list_name}")
            
            list_item, item_created = LeadListItem.objects.get_or_create(
                lead=lead,
                lead_list=lead_list,
                defaults={'notes': notes}
            )
            
            if item_created:
                logger.info(f"Added lead {lead.id} to list '{list_name}'")
                return True, f"Lead '{lead.full_name}' added to '{list_name}'!"
            else:
                if notes and notes != list_item.notes:
                    list_item.notes = notes
                    list_item.save()
                    return True, f"Lead '{lead.full_name}' already in '{list_name}'. Notes updated."
                return True, f"Lead '{lead.full_name}' is already in '{list_name}'."
                
        except Exception as e:
            logger.error(f"Error adding lead to list: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def remove_lead_from_list(lead: Lead, lead_list: LeadList) -> Tuple[bool, str]:
        """Remove lead from list."""
        try:
            item = LeadListItem.objects.filter(lead=lead, lead_list=lead_list).first()
            if item:
                item.delete()
                logger.info(f"Removed lead {lead.id} from list '{lead_list.name}'")
                return True, "Lead removed successfully!"
            return False, "Lead is not in this list."
        except Exception as e:
            logger.error(f"Error removing lead from list: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_all_lists_with_leads() -> List[Dict[str, Any]]:
        """Get all lists with metadata."""
        lists = LeadList.objects.all().order_by('-created_at')
        return [{
            'id': lst.id,
            'name': lst.name,
            'slug': lst.slug,
            'description': lst.description,
            'lead_count': lst.get_lead_count(),
            'created_at': lst.created_at,
            'updated_at': lst.updated_at,
        } for lst in lists]
    
    @staticmethod
    def get_leads_in_list(lead_list: LeadList):  # Sin type hint para evitar warning
        """Get all leads in a specific list."""
        return lead_list.get_leads()
    
    @staticmethod
    def create_list(name: str, description: str = "") -> Tuple[bool, str, Optional[LeadList]]:
        """Create a new list."""
        try:
            if LeadList.objects.filter(name=name).exists():
                return False, f"A list named '{name}' already exists.", None
            
            lst = LeadList.objects.create(name=name, description=description)
            logger.info(f"Created list: {name} (ID: {lst.id})")
            return True, f"List '{name}' created successfully!", lst
            
        except Exception as e:
            logger.error(f"Error creating list: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def delete_list(lead_list: LeadList) -> Tuple[bool, str]:
        """Delete a list."""
        try:
            name = lead_list.name
            lead_list.delete()
            logger.info(f"Deleted list: {name}")
            return True, f"List '{name}' deleted successfully!"
        except Exception as e:
            logger.error(f"Error deleting list: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def bulk_add_leads_to_list(leads: List[Lead], list_name: str) -> Dict[str, int]:
        """Bulk add multiple leads to a list."""
        added = 0
        skipped = 0
        errors = 0
        
        try:
            lst, _ = LeadList.objects.get_or_create(
                name=list_name,
                defaults={'description': f'Bulk import: {list_name}'}
            )
        except Exception as e:
            logger.error(f"Error creating list for bulk add: {str(e)}")
            return {'added': 0, 'skipped': 0, 'errors': len(leads)}
        
        for lead in leads:
            try:
                _, created = LeadListItem.objects.get_or_create(
                    lead=lead, 
                    lead_list=lst
                )
                if created:
                    added += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"Error adding lead {lead.id} in bulk: {str(e)}")
                errors += 1
        
        logger.info(f"Bulk add to '{list_name}': {added} added, {skipped} skipped, {errors} errors")
        return {'added': added, 'skipped': skipped, 'errors': errors}