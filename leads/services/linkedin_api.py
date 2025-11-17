# leads/services/linkedin_api.py
import requests
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LinkedInAPIService:
    """
    Service to interact with LinkedIn API at linkedin.programando.io
    
    API Endpoint: GET with JSON body
    URL: https://linkedin.programando.io/fetch_lead2
    
    Request Format (JSON body in GET request):
    {
        "limit": 10,
        "location": ["United States", "San Francisco"],
        "position": "Software Engineer",
        "company_name": ["Google"],
        "company_industry": "Technology",
        "company_headcount": "1-10 employees",
        "skills": "Python",
        "level": "Senior",
        "name": "John"
    }
    
    Response Format:
    {
        "results": [
            {
                "id": 2566,
                "name": "Fred",
                "surname": "Fred",
                "linkedin": "linkedin.com/in/...",
                "location": "United States",
                "region": "Northern America",
                "position": "A Good One",
                "headline": "...",
                "level": "Specialist",
                "department": "",
                "skills": "",
                "company_name": "Top 000",
                "company_domain": "0.be",
                "company_linkedin": "https://...",
                "company_location": "Belgium",
                "company_industry": "Construction",
                "company_subindustry": "...",
                "company_headcount": "1-10 employees",
                "company_founded": "",
                "company_revenue": "Not Known"
            }
        ]
    }
    """
    
    def __init__(self):
        """Initialize the LinkedIn API service"""
        self.api_url = "https://linkedin.programando.io/fetch_lead2"
        self.session = requests.Session()
    
    def fetch_leads(self, filters: Dict) -> Dict:
        """
        Fetch leads from LinkedIn API with given filters.
        All filters are optional and can be combined.
        
        Args:
            filters: Dictionary containing search filters
                - name: Person's name
                - title: Job title
                - company: Company name
                - country: Country name
                - location: City or state
                - industry: Industry name
                - company_size: Company headcount
                - seniority_level: Seniority level
                - keywords: Skills or keywords
                - limit: Number of results (default: 50, max: 100)
        
        Returns:
            Dictionary with 'success', 'results', 'total', and 'error' keys
        """
        try:
            # Build request body from filters
            body = self._build_request_body(filters)
            
            # Build headers - Content-Type must be application/json
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Lead-Finder/1.0"
            }
            
            logger.info(f"Fetching leads from API: GET {self.api_url}")
            logger.info(f"Request body: {json.dumps(body, indent=2)}")
            
            # Make GET request with JSON body (unusual but required by this API)
            response = self.session.request(
                "GET",
                self.api_url,
                data=json.dumps(body),
                headers=headers,
                timeout=60
            )
            
            logger.info(f"API response status: {response.status_code}")
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            results = data.get('results', [])
            
            logger.info(f"Successfully fetched {len(results)} leads from API")
            
            return {
                'success': True,
                'results': results,
                'total': len(results),
                'error': None
            }
            
        except requests.exceptions.Timeout:
            logger.error("API request timeout after 60 seconds")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': "Request timeout. The API is taking too long to respond. Please try again."
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error: {e.response.status_code}")
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text[:500]
            
            logger.error(f"Error details: {error_detail}")
            
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"API Error {e.response.status_code}: {error_detail}"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"Failed to connect to API: {str(e)}"
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response as JSON: {str(e)}")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': "Invalid response from API. Please try again later."
            }
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"An unexpected error occurred: {str(e)}"
            }
    
    def _build_request_body(self, filters: Dict) -> Dict:
        """
        Build request body from filters.
        All filters are optional and can be used independently or combined.
        
        NOTE: API requires array format for:
        - location: array
        - company_name: array
        
        Args:
            filters: Dictionary with filter parameters from form
        
        Returns:
            Dictionary ready to send to API as JSON body
        """
        body = {}
        
        # Limit - Number of results to return
        limit = filters.get('limit', 50)
        try:
            body['limit'] = min(int(limit), 100)  # Max 100 results
        except (ValueError, TypeError):
            body['limit'] = 50  # Default to 50
        
        # Location - API expects ARRAY format
        location_list = []
        
        if filters.get('country'):
            location_list.append(filters['country'])
        
        if filters.get('location'):
            location_list.append(filters['location'])
        
        if location_list:
            body['location'] = location_list
        
        # Name - Search by person's name
        if filters.get('name'):
            body['name'] = filters['name']
        
        # Job Title -> position
        if filters.get('title'):
            body['position'] = filters['title']
        
        # Company -> company_name (API requires ARRAY format)
        if filters.get('company'):
            body['company_name'] = [filters['company']]
        
        # Industry -> company_industry
        if filters.get('industry'):
            body['company_industry'] = filters['industry']
        
        # Company Size -> company_headcount
        if filters.get('company_size'):
            body['company_headcount'] = filters['company_size']
        
        # Keywords -> skills
        if filters.get('keywords'):
            body['skills'] = filters['keywords']
        
        # Seniority Level -> level
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
            mapped_level = seniority_map.get(
                filters['seniority_level'], 
                filters['seniority_level'].title()
            )
            body['level'] = mapped_level
        
        logger.debug(f"Built request body with {len(body)} filters: {list(body.keys())}")
        
        return body
    
    def parse_lead_data(self, raw_lead: Dict) -> Dict:
        """
        Parse raw lead data from API into our Lead model format.
        
        Args:
            raw_lead: Raw lead dictionary from API response
        
        Returns:
            Dictionary with parsed lead data ready for Lead model
        
        Raises:
            Exception: If parsing fails
        """
        try:
            # Extract and combine name parts
            first_name = raw_lead.get('name', '')
            last_name = raw_lead.get('surname', '')
            full_name = f"{first_name} {last_name}".strip()
            
            # Normalize LinkedIn URL - add https:// if missing
            linkedin_url = raw_lead.get('linkedin', '')
            if linkedin_url and not linkedin_url.startswith('http'):
                linkedin_url = f'https://{linkedin_url}'
            
            # Map API seniority level to our database choices
            level = raw_lead.get('level', '')
            seniority = self._map_seniority(level)
            
            # Build parsed lead dictionary
            parsed = {
                'external_id': str(raw_lead.get('id', '')),
                'first_name': first_name,
                'last_name': last_name,
                'full_name': full_name,
                'email': raw_lead.get('email', ''),
                'phone': raw_lead.get('phone', ''),
                'linkedin_url': linkedin_url,
                'photo_url': None,  # API doesn't provide photos
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
        """
        Map API seniority level string to our database choices.
        
        Args:
            api_level: Seniority level string from API
        
        Returns:
            Mapped seniority code for our database
        """
        if not api_level:
            return ''
        
        level_lower = api_level.lower().strip()
        
        # Mapping dictionary from API values to our codes
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
        """
        Apply additional client-side filters to leads.
        Used when API doesn't support certain filters or for additional refinement.
        
        Args:
            leads: List of lead dictionaries from API
            filters: Dictionary with filter criteria
        
        Returns:
            Filtered list of leads
        """
        filtered = leads
        
        # Filter by name (case-insensitive partial match)
        name = filters.get('name', '').lower()
        if name:
            filtered = [
                lead for lead in filtered 
                if name in f"{lead.get('name', '')} {lead.get('surname', '')}".lower()
            ]
        
        # Filter by seniority level
        seniority = filters.get('seniority_level')
        if seniority:
            filtered = [
                lead for lead in filtered 
                if self._map_seniority(lead.get('level', '')) == seniority
            ]
        
        # Filter by company size (exact match)
        company_size = filters.get('company_size')
        if company_size:
            filtered = [
                lead for lead in filtered 
                if lead.get('company_headcount', '') == company_size
            ]
        
        logger.info(f"Local filtering: {len(leads)} leads -> {len(filtered)} leads after filtering")
        
        return filtered