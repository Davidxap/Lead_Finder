# leads/services/linkedin_api.py
import requests
import json
import logging
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class LinkedInAPIService:
    """
    Service to interact with LinkedIn API.
    Handles fetching leads and parsing responses.
    """
    
    def __init__(self):
        self.api_url = settings.LINKEDIN_API_URL
        self.user_agent = settings.LINKEDIN_API_USER_AGENT
        self.session = requests.Session()
    
    def fetch_leads(self, filters: Dict) -> Dict:
        """
        Fetch leads from LinkedIn API with given filters.
        
        Args:
            filters: Dictionary containing search filters
                - limit: Number of results to fetch
                - location: List of locations/countries
                - company: Company name
                - title: Job title
                - industry: Industry name
                - keywords: Search keywords
        
        Returns:
            Dictionary with 'results' and metadata
        """
        try:
            # Build request body
            body = self._build_request_body(filters)
            
            # Build headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": self.user_agent,
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            }
            
            logger.info(f"Fetching leads with filters: {filters}")
            
            # Make request
            req = requests.Request("GET", self.api_url, data=json.dumps(body), headers=headers)
            prepared = req.prepare()
            
            response = self.session.send(prepared, timeout=30)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            logger.info(f"Fetched {len(data.get('results', []))} leads")
            
            return {
                'success': True,
                'results': data.get('results', []),
                'total': len(data.get('results', [])),
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed: {str(e)}")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"Failed to fetch leads: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"An unexpected error occurred: {str(e)}"
            }
    
    def _build_request_body(self, filters: Dict) -> Dict:
        """
        Build request body from filters.
        
        Args:
            filters: Dictionary with filter parameters
        
        Returns:
            Dictionary ready to send to API
        """
        body = {}
        
        # Limit
        limit = filters.get('limit', 100)
        body['limit'] = min(int(limit), 1000)  # Max 1000
        
        # Location/Country
        location = filters.get('location') or filters.get('country')
        if location:
            if isinstance(location, list):
                body['location'] = location
            else:
                body['location'] = [location]
        
        # Company
        company = filters.get('company')
        if company:
            body['company'] = company
        
        # Job Title
        title = filters.get('title') or filters.get('job_title')
        if title:
            body['title'] = title
        
        # Industry
        industry = filters.get('industry')
        if industry:
            body['industry'] = industry
        
        # Keywords
        keywords = filters.get('keywords')
        if keywords:
            body['keywords'] = keywords
        
        return body
    
    def parse_lead_data(self, raw_lead: Dict) -> Dict:
        """
        Parse raw lead data from API into our format.
        
        Args:
            raw_lead: Raw lead data from API
        
        Returns:
            Parsed lead data ready for database
        """
        # Extract name
        name = raw_lead.get('name', '')
        name_parts = name.split(' ', 1) if name else ['', '']
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Determine seniority level from title
        title = raw_lead.get('position', '').lower()
        seniority = self._determine_seniority(title)
        
        return {
            'external_id': str(raw_lead.get('id', '')),
            'first_name': first_name,
            'last_name': last_name,
            'full_name': name,
            'email': raw_lead.get('email', ''),
            'phone': raw_lead.get('phone', ''),
            'linkedin_url': raw_lead.get('linkedin', ''),
            'photo_url': None,  # API doesn't provide photos
            'current_title': raw_lead.get('position', ''),
            'current_company': raw_lead.get('company_name', ''),
            'company_linkedin_url': raw_lead.get('company_linkedin', ''),
            'headline': raw_lead.get('headline', ''),
            'location': raw_lead.get('location', ''),
            'country': raw_lead.get('region', ''),  # Using region as country
            'industry': raw_lead.get('company_industry', ''),
            'company_size': raw_lead.get('company_headcount', ''),
            'seniority_level': seniority,
            'skills': raw_lead.get('skills', ''),
            'bio': raw_lead.get('headline', ''),  # Using headline as bio
        }
    
    def _determine_seniority(self, title: str) -> str:
        """Determine seniority level from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['ceo', 'cto', 'cfo', 'coo', 'chief', 'president']):
            return 'c_level'
        elif 'vp' in title_lower or 'vice president' in title_lower:
            return 'vp'
        elif 'director' in title_lower:
            return 'director'
        elif 'manager' in title_lower or 'head of' in title_lower:
            return 'manager'
        elif 'senior' in title_lower or 'sr' in title_lower or 'lead' in title_lower:
            return 'senior'
        elif 'junior' in title_lower or 'jr' in title_lower or 'associate' in title_lower:
            return 'entry'
        elif 'owner' in title_lower or 'founder' in title_lower:
            return 'owner'
        elif 'partner' in title_lower:
            return 'partner'
        else:
            return 'mid'
    
    def filter_leads_locally(self, leads: List[Dict], filters: Dict) -> List[Dict]:
        """
        Apply additional filters to leads locally (client-side filtering).
        
        Args:
            leads: List of lead dictionaries
            filters: Dictionary with filter criteria
        
        Returns:
            Filtered list of leads
        """
        filtered = leads
        
        # Filter by name
        name = filters.get('name', '').lower()
        if name:
            filtered = [
                lead for lead in filtered 
                if name in lead.get('name', '').lower()
            ]
        
        # Filter by seniority level
        seniority = filters.get('seniority_level')
        if seniority:
            filtered = [
                lead for lead in filtered
                if self._determine_seniority(lead.get('position', '')) == seniority
            ]
        
        # Filter by company size
        company_size = filters.get('company_size')
        if company_size:
            filtered = [
                lead for lead in filtered
                if company_size.lower() in lead.get('company_headcount', '').lower()
            ]
        
        return filtered