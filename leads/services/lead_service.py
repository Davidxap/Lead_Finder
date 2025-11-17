# leads/services/lead_service.py
import logging
from typing import Dict, List, Tuple, Optional, Any
from django.db import IntegrityError
from django.db.models import QuerySet
from leads.models import Lead, LeadList, LeadListItem

logger = logging.getLogger(__name__)


class LeadService:
    """
    Service to handle lead-related business logic.
    Handles CRUD operations for leads, lists, and their relationships.
    """
    
    @staticmethod
    def create_or_update_lead(lead_data: Dict[str, Any]) -> Lead:
        """
        Create a new lead or update existing one.
        
        Args:
            lead_data: Dictionary with lead information
        
        Returns:
            Lead instance
        """
        external_id = lead_data.get('external_id')
        
        if not external_id:
            raise ValueError("external_id is required")
        
        try:
            # Try to update existing lead
            lead, created = Lead.objects.update_or_create(
                external_id=external_id,
                defaults=lead_data
            )
            
            action = "created" if created else "updated"
            logger.info(f"Lead {lead.get_full_name()} {action} (ID: {lead.id})")
            
            return lead
            
        except Exception as e:
            logger.error(f"Error creating/updating lead: {str(e)}")
            raise
    
    @staticmethod
    def add_lead_to_list(lead: Lead, list_name: str, notes: str = "") -> Tuple[bool, str]:
        """
        Add a lead to a specific list.
        
        Args:
            lead: Lead instance
            list_name: Name of the list
            notes: Optional notes
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get or create the list
            lead_list, _ = LeadList.objects.get_or_create(
                name=list_name,
                defaults={'description': f'Auto-created list: {list_name}'}
            )
            
            # Check if lead already exists in list
            exists = LeadListItem.objects.filter(
                lead=lead,
                lead_list=lead_list
            ).exists()
            
            if exists:
                return False, f"Lead is already in list '{list_name}'"
            
            # Create the relationship
            LeadListItem.objects.create(
                lead=lead,
                lead_list=lead_list,
                notes=notes
            )
            
            logger.info(f"Lead {lead.get_full_name()} added to list '{list_name}'")
            return True, f"Lead successfully added to '{list_name}'"
            
        except Exception as e:
            logger.error(f"Error adding lead to list: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def remove_lead_from_list(lead: Lead, lead_list: LeadList) -> Tuple[bool, str]:
        """
        Remove a lead from a list.
        
        Args:
            lead: Lead instance
            lead_list: LeadList instance
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            deleted_count, _ = LeadListItem.objects.filter(
                lead=lead,
                lead_list=lead_list
            ).delete()
            
            if deleted_count > 0:
                logger.info(f"Lead {lead.get_full_name()} removed from list '{lead_list.name}'")
                return True, "Lead removed from list"
            else:
                return False, "Lead was not in this list"
                
        except Exception as e:
            logger.error(f"Error removing lead from list: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def create_list(name: str, description: str = "") -> Tuple[bool, str, Optional[LeadList]]:
        """
        Create a new lead list.
        
        Args:
            name: List name
            description: List description
        
        Returns:
            Tuple of (success: bool, message: str, lead_list: LeadList or None)
        """
        try:
            lead_list = LeadList.objects.create(
                name=name,
                description=description
            )
            logger.info(f"List '{name}' created")
            return True, f"List '{name}' created successfully", lead_list
            
        except IntegrityError:
            return False, f"List with name '{name}' already exists", None
        except Exception as e:
            logger.error(f"Error creating list: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def delete_list(lead_list: LeadList) -> Tuple[bool, str]:
        """
        Delete a lead list.
        
        Args:
            lead_list: LeadList instance
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            list_name = lead_list.name
            lead_list.delete()
            logger.info(f"List '{list_name}' deleted")
            return True, f"List '{list_name}' deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting list: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_all_lists_with_leads() -> List[Dict[str, Any]]:
        """
        Get all lists with their leads.
        
        Returns:
            List of dictionaries with list information and leads
        """
        lists = LeadList.objects.all().prefetch_related('list_items__lead')
        
        result: List[Dict[str, Any]] = []
        for lead_list in lists:
            list_data: Dict[str, Any] = {
                'id': lead_list.id,
                'name': lead_list.name,
                'slug': lead_list.slug,
                'description': lead_list.description,
                'created_at': lead_list.created_at,
                'lead_count': lead_list.get_lead_count(),
                'leads': []
            }
            
            # Get all leads in this list
            for item in lead_list.list_items.all():
                lead = item.lead
                list_data['leads'].append({
                    'id': lead.id,
                    'full_name': lead.get_full_name(),
                    'email': lead.email,
                    'phone': lead.phone,
                    'current_title': lead.current_title,
                    'current_company': lead.current_company,
                    'linkedin_url': lead.linkedin_url,
                    'location': lead.location,
                    'added_at': item.added_at,
                    'notes': item.notes,
                })
            
            result.append(list_data)
        
        return result
    
    @staticmethod
    def get_leads_in_list(lead_list: LeadList) -> QuerySet[Lead]:
        """
        Get all leads in a specific list.
        
        Args:
            lead_list: LeadList instance
        
        Returns:
            QuerySet of Lead instances
        """
        return lead_list.get_leads()
    
    @staticmethod
    def bulk_add_leads_to_list(leads: List[Lead], list_name: str) -> Dict[str, int]:
        """
        Add multiple leads to a list.
        
        Args:
            leads: List of Lead instances
            list_name: Name of the list
        
        Returns:
            Dictionary with results
        """
        # Get or create the list
        lead_list, _ = LeadList.objects.get_or_create(
            name=list_name,
            defaults={'description': f'Auto-created list: {list_name}'}
        )
        
        added = 0
        skipped = 0
        errors = 0
        
        for lead in leads:
            # Check if already exists
            exists = LeadListItem.objects.filter(
                lead=lead,
                lead_list=lead_list
            ).exists()
            
            if exists:
                skipped += 1
                continue
            
            try:
                LeadListItem.objects.create(
                    lead=lead,
                    lead_list=lead_list
                )
                added += 1
            except Exception as e:
                logger.error(f"Error adding lead {lead.id}: {str(e)}")
                errors += 1
        
        logger.info(f"Bulk add to '{list_name}': {added} added, {skipped} skipped, {errors} errors")
        
        return {
            'added': added,
            'skipped': skipped,
            'errors': errors,
            'total': len(leads)
        }