# leads/services/linkedin_api.py
import requests
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LinkedInAPIService:
    """
    Service to interact with LinkedIn API at linkedin.programando.io
    
    Includes automatic fallback to mock data when API is unavailable.
    """
    
    def __init__(self):
        """Initialize the LinkedIn API service"""
        self.api_url = "https://linkedin.programando.io/fetch_lead2"
        self.session = requests.Session()
    
    def fetch_leads(self, filters: Dict) -> Dict:
        """
        Fetch leads from LinkedIn API with automatic fallback.
        
        Args:
            filters: Dictionary containing search filters
        
        Returns:
            Dictionary with 'success', 'results', 'total', 'error', and 'is_mock' keys
        """
        try:
            body = self._build_request_body(filters)
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "PostmanRuntime/7.49.1"
            }
            
            logger.info(f"Attempting API call: {self.api_url}")
            logger.info(f"Request body: {json.dumps(body, indent=2)}")
            
            response = requests.get(
                self.api_url,
                data=json.dumps(body),
                headers=headers,
                timeout=10  # Short timeout - if API is down, fail fast
            )
            
            logger.info(f"API response status: {response.status_code}")
            
            # If error 500 or any error, use mock immediately
            if response.status_code != 200:
                logger.error(f"API error {response.status_code} - switching to mock data")
                return self._get_mock_data(filters)
            
            data = response.json()
            results = data.get('results', [])
            
            logger.info(f"Successfully fetched {len(results)} leads from real API")
            
            return {
                'success': True,
                'results': results,
                'total': len(results),
                'error': None,
                'is_mock': False
            }
            
        except requests.exceptions.Timeout:
            logger.warning("API timeout - switching to mock data")
            return self._get_mock_data(filters)
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"API connection error: {e} - switching to mock data")
            return self._get_mock_data(filters)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from API - switching to mock data")
            return self._get_mock_data(filters)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)} - switching to mock data")
            return self._get_mock_data(filters)
    
    def _get_mock_data(self, filters: Dict) -> Dict:
        """Fetch mock data when API is unavailable"""
        try:
            from .mock_linkedin_data import MockLinkedInData
            
            limit = filters.get('limit', 50)
            logger.info(f"Generating {limit} mock leads")
            
            mock_leads = MockLinkedInData.generate_leads(count=limit, filters=filters)
            
            return {
                'success': True,
                'results': mock_leads,
                'total': len(mock_leads),
                'error': None,
                'is_mock': True
            }
        except Exception as e:
            logger.error(f"Error generating mock data: {e}")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"Both API and mock data failed: {e}",
                'is_mock': False
            }
    
    def _build_request_body(self, filters: Dict) -> Dict:
        """Build request body from filters - only ONE filter due to API limitations"""
        body = {}
        
        limit = filters.get('limit', 50)
        try:
            body['limit'] = min(int(limit), 1000)
        except (ValueError, TypeError):
            body['limit'] = 50
        
        # Priority: position > level > industry
        if filters.get('title'):
            body['position'] = [filters['title']]
            logger.debug("Using filter: position")
            return body
        
        if filters.get('seniority_level'):
            seniority_map = {
                'entry': 'Entry Level',
                'mid': 'Mid Level',
                'senior': 'Senior',
                'manager': 'Manager',
                'director': 'Director',
                'vp': 'VP',
                'c_level': 'C-Level',
                'owner': 'Owner',
                'partner': 'Partner',
            }
            mapped_level = seniority_map.get(filters['seniority_level'], filters['seniority_level'].title())
            body['level'] = [mapped_level]
            logger.debug("Using filter: level")
            return body
        
        if filters.get('industry'):
            body['company_industry'] = [filters['industry']]
            logger.debug("Using filter: industry")
            return body
        
        logger.debug("No specific filters, using limit only")
        return body
    
    def parse_lead_data(self, raw_lead: Dict) -> Dict:
        """Parse raw lead data from API into our Lead model format"""
        try:
            first_name = raw_lead.get('name', '')
            last_name = raw_lead.get('surname', '')
            full_name = f"{first_name} {last_name}".strip()
            
            linkedin_url = raw_lead.get('linkedin', '')
            if linkedin_url and not linkedin_url.startswith('http'):
                linkedin_url = f'https://{linkedin_url}'
            
            level = raw_lead.get('level', '')
            seniority = self._map_seniority(level)
            
            parsed = {
                'external_id': str(raw_lead.get('id', '')),
                'first_name': first_name,
                'last_name': last_name,
                'full_name': full_name,
                'email': raw_lead.get('email', ''),
                'phone': raw_lead.get('phone', ''),
                'linkedin_url': linkedin_url,
                'photo_url': None,
                'current_title': raw_lead.get('position', ''),
                'current_company': raw_lead.get('company_name', ''),
                'company_linkedin_url': raw_lead.get('company_linkedin', ''),
                'headline': raw_lead.get('headline', ''),
                'location': raw_lead.get('location', ''),
                'country': raw_lead.get('region', ''),
                'region': raw_lead.get('region', ''),
                'industry': raw_lead.get('company_industry', ''),
                'company_size': raw_lead.get('company_headcount', ''),
                'company_domain': raw_lead.get('company_domain', ''),
                'company_location': raw_lead.get('company_location', ''),
                'company_founded': raw_lead.get('company_founded', ''),
                'company_revenue': raw_lead.get('company_revenue', ''),
                'company_subindustry': raw_lead.get('company_subindustry', ''),
                'level': raw_lead.get('level', ''),
                'department': raw_lead.get('department', ''),
                'seniority_level': seniority,
                'skills': raw_lead.get('skills', ''),
                'bio': raw_lead.get('headline', ''),
            }
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing lead data: {str(e)}", exc_info=True)
            raise
    
    def _map_seniority(self, api_level: str) -> str:
        """Map API seniority level string to our database choices"""
        if not api_level:
            return ''
        
        level_lower = api_level.lower().strip()
        
        mapping = {
            'entry': 'entry',
            'entry level': 'entry',
            'junior': 'entry',
            'mid': 'mid',
            'mid level': 'mid',
            'intermediate': 'mid',
            'senior': 'senior',
            'sr': 'senior',
            'senior level': 'senior',
            'specialist': 'senior',
            'manager': 'manager',
            'mgr': 'manager',
            'director': 'director',
            'dir': 'director',
            'vp': 'vp',
            'vice president': 'vp',
            'c-level': 'c_level',
            'c level': 'c_level',
            'executive': 'c_level',
            'ceo': 'c_level',
            'cto': 'c_level',
            'cfo': 'c_level',
            'coo': 'c_level',
            'cmo': 'c_level',
            'owner': 'owner',
            'founder': 'owner',
            'partner': 'partner',
        }
        
        return mapping.get(level_lower, '')
    
    def filter_leads_locally(self, leads: List[Dict], filters: Dict) -> List[Dict]:
        """Apply client-side filters to leads"""
        filtered = leads
        
        name = filters.get('name', '').lower()
        if name:
            filtered = [
                lead for lead in filtered 
                if name in f"{lead.get('name', '')} {lead.get('surname', '')}".lower()
            ]
        
        company = filters.get('company', '').lower()
        if company:
            filtered = [
                lead for lead in filtered 
                if company in lead.get('company_name', '').lower()
            ]
        
        location = filters.get('location', '').lower()
        country = filters.get('country', '').lower()
        if location or country:
            filtered = [
                lead for lead in filtered 
                if (location and location in lead.get('location', '').lower()) or
                   (country and country in lead.get('region', '').lower())
            ]
        
        seniority = filters.get('seniority_level')
        if seniority:
            filtered = [
                lead for lead in filtered 
                if self._map_seniority(lead.get('level', '')) == seniority
            ]
        
        company_size = filters.get('company_size')
        if company_size:
            filtered = [
                lead for lead in filtered 
                if lead.get('company_headcount', '') == company_size
            ]
        
        industry = filters.get('industry', '').lower()
        if industry:
            filtered = [
                lead for lead in filtered 
                if industry in lead.get('company_industry', '').lower()
            ]
        
        keywords = filters.get('keywords', '').lower()
        if keywords:
            filtered = [
                lead for lead in filtered 
                if keywords in lead.get('skills', '').lower()
            ]
        
        logger.info(f"Local filtering: {len(leads)} -> {len(filtered)} leads")
        
        return filtered