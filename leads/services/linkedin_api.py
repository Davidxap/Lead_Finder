# leads/services/linkedin_api.py
import requests
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LinkedInAPIService:
    """Service to interact with LinkedIn API at linkedin.programando.io"""
    
    def __init__(self):
        self.api_url = "https://linkedin.programando.io/fetch_lead2"
        self.session = requests.Session()
    
    def fetch_leads(self, filters: Dict) -> Dict:
        """Fetch leads from LinkedIn API with given filters."""
        try:
            # Build request body
            body = self._build_request_body(filters)
            
            # Build headers (IMPORTANTE: Content-Type debe ser application/json)
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Lead-Finder/1.0"
            }
            
            logger.info(f"GET {self.api_url} (with JSON body)")
            logger.info(f"Body: {json.dumps(body, indent=2)}")
            
            # GET request con JSON body (inusual pero es lo que requiere esta API)
            response = requests.request(
                "GET",
                self.api_url,
                data=json.dumps(body),
                headers=headers,
                timeout=60
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            results = data.get('results', [])
            
            logger.info(f"Successfully fetched {len(results)} leads")
            
            return {
                'success': True,
                'results': results,
                'total': len(results),
                'error': None
            }
            
        except requests.exceptions.Timeout:
            logger.error("API request timeout")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': "Request timeout. Please try again."
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error: {e.response.status_code}")
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text
            
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"{e.response.status_code} Error: {error_detail}"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed: {str(e)}")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"Failed to connect: {str(e)}"
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {str(e)}")
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': "Invalid API response"
            }
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'results': [],
                'total': 0,
                'error': f"Error: {str(e)}"
            }
    
    def _build_request_body(self, filters: Dict) -> Dict:
        """
        Build request body.
        La API espera JSON en el body (aunque sea GET).
        """
        body = {}
        
        # Limit
        limit = filters.get('limit', 50)
        try:
            body['limit'] = min(int(limit), 100)
        except:
            body['limit'] = 50
        
        # Location - Como ARRAY
        location_list = []
        
        if filters.get('country'):
            location_list.append(filters['country'])
        
        if filters.get('location'):
            location_list.append(filters['location'])
        
        if location_list:
            body['location'] = location_list
        
        # Job Title -> position
        if filters.get('title'):
            body['position'] = filters['title']
        
        # Company -> company_name
        if filters.get('company'):
            body['company_name'] = filters['company']
        
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
            body['level'] = seniority_map.get(
                filters['seniority_level'], 
                filters['seniority_level'].title()
            )
        
        # Name
        if filters.get('name'):
            body['name'] = filters['name']
        
        logger.debug(f"Request body: {json.dumps(body, indent=2)}")
        return body
    
    def parse_lead_data(self, raw_lead: Dict) -> Dict:
        """Parse raw lead data from API into our format."""
        try:
            first_name = raw_lead.get('name', '')
            last_name = raw_lead.get('surname', '')
            full_name = f"{first_name} {last_name}".strip()
            
            linkedin_url = raw_lead.get('linkedin', '')
            if linkedin_url and not linkedin_url.startswith('http'):
                linkedin_url = f'https://{linkedin_url}'
            
            level = raw_lead.get('level', '')
            seniority = self._map_seniority(level)
            
            return {
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
            
        except Exception as e:
            logger.error(f"Error parsing lead: {str(e)}")
            raise
    
    def _map_seniority(self, api_level: str) -> str:
        """Map API seniority to database choices."""
        if not api_level:
            return ''
        
        level_lower = api_level.lower().strip()
        
        mapping = {
            'entry': 'entry', 'entry level': 'entry', 'junior': 'entry',
            'mid': 'mid', 'mid level': 'mid', 'intermediate': 'mid',
            'senior': 'senior', 'sr': 'senior', 'specialist': 'senior',
            'manager': 'manager', 'mgr': 'manager',
            'director': 'director', 'dir': 'director',
            'vp': 'vp', 'vice president': 'vp',
            'c-level': 'c_level', 'ceo': 'c_level', 'cto': 'c_level',
            'owner': 'owner', 'founder': 'owner',
            'partner': 'partner',
        }
        
        return mapping.get(level_lower, '')
    
    def filter_leads_locally(self, leads: List[Dict], filters: Dict) -> List[Dict]:
        """Apply client-side filters."""
        filtered = leads
        
        name = filters.get('name', '').lower()
        if name:
            filtered = [l for l in filtered if name in f"{l.get('name', '')} {l.get('surname', '')}".lower()]
        
        seniority = filters.get('seniority_level')
        if seniority:
            filtered = [l for l in filtered if self._map_seniority(l.get('level', '')) == seniority]
        
        company_size = filters.get('company_size')
        if company_size:
            filtered = [l for l in filtered if l.get('company_headcount', '') == company_size]
        
        logger.info(f"Filtered {len(leads)} -> {len(filtered)} leads")
        return filtered