# leads/services/linkedin_api.py
import requests
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LinkedInAPIService:
    """
    Service to interact with LinkedIn API at linkedin.programando.io

    IMPORTANT NOTES BASED ON REAL API DATA:
    - API accepts ONLY ONE filter at a time (position, level, or company_industry)
    - Multiple filters cause 500 errors
    - Location/region filters don't work on API side
    - All other filters must be applied client-side
    - Default limit is 50, but we can increase it to 1000

    API Data Structure:
    {
        "location": "United States",           // Country name
        "region": "Northern America",          // Geographical region
        "position": "Director",                // Job title
        "level": "Director",                   // Seniority level
        "company_name": "Top 000",
        "company_industry": "Construction",
        "company_headcount": "1-10 employees",
        "skills": "...",
        "headline": "...",
        ...
    }

    Includes automatic fallback to mock data when API is unavailable.
    """

    def __init__(self):
        """Initialize the LinkedIn API service"""
        self.api_url = "https://linkedin.programando.io/fetch_lead2"
        self.session = requests.Session()

    def fetch_leads(self, filters: Dict) -> Dict:
        """
        Fetch leads from LinkedIn API with automatic fallback.

        Can fetch up to 1000 leads per request.
        If more are needed, makes multiple requests.

        Args:
            filters: Dictionary containing search filters

        Returns:
            Dictionary with 'success', 'results', 'total', 'error', and 'is_mock' keys
        """
        try:
            # Get requested limit (default 500, max 1000)
            requested_limit = int(filters.get('limit', 500))
            requested_limit = min(requested_limit, 1000)  # Cap at 1000

            # Build request body
            body = self._build_request_body(filters)
            body['limit'] = requested_limit

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "PostmanRuntime/7.49.1"
            }

            logger.info(f"Attempting API call: {self.api_url}")
            logger.info(f"Request body: {json.dumps(body, indent=2)}")
            logger.info(f"Requesting {requested_limit} leads")

            response = requests.get(
                self.api_url,
                data=json.dumps(body),
                headers=headers,
                timeout=30  # Increased timeout for larger requests
            )

            logger.info(f"API response status: {response.status_code}")

            # If error 500 or any error, return error immediately (NO MOCK)
            if response.status_code != 200:
                error_msg = f"API Error {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'results': []
                }

            data = response.json()
            results = data.get('results', [])

            logger.info(f"API returned {len(results)} leads")

            # Apply local filters since API doesn't support multiple filters
            if filters:
                logger.info(f"Applying local filters: {filters}")
                initial_count = len(results)
                results = self.filter_leads_locally(results, filters)
                final_count = len(results)
                logger.info(
                    f"Local filtering: {initial_count} -> {final_count} leads")

            logger.info(
                f"Successfully fetched {len(results)} leads from real API")

            return {
                'success': True,
                'results': results,
                'total': len(results),
                'error': None,
                'is_mock': False
            }

        except requests.exceptions.Timeout:
            logger.error("API timeout")
            return {
                'success': False,
                'error': "API Connection Timeout",
                'results': []
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"API connection error: {e}")
            return {
                'success': False,
                'error': f"API Connection Error: {str(e)}",
                'results': []
            }

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from API")
            return {
                'success': False,
                'error': "Invalid JSON response from API",
                'results': []
            }

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f"Unexpected Error: {str(e)}",
                'results': []
            }

    def _get_mock_data(self, filters: Dict) -> Dict:
        """Fetch mock data when API is unavailable"""
        try:
            from .mock_linkedin_data import MockLinkedInData

            limit = int(filters.get('limit', 500))
            limit = min(limit, 1000)  # Cap at 1000

            logger.info(f"Generating {limit} mock leads")

            mock_leads = MockLinkedInData.generate_leads(
                count=limit, filters=filters)

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
        """
        Build request body from filters.

        CRITICAL: API ONLY accepts ONE filter at a time!
        Multiple filters cause 500 Internal Server Error.

        Priority order (based on testing):
        1. location (country) - CRITICAL to avoid default Spain results
        2. region (geographical)
        3. position (title)
        4. level (seniority)
        """
        try:
            body = {}

            # PRIORITY 1: Location (Country)
            # This is the most critical filter to get right
            if filters.get('location'):
                # Ensure it's a list as per API requirements
                body['location'] = [filters['location']]
                logger.debug(
                    f"Using API filter: location = {filters['location']}")
                return body

            # PRIORITY 2: Position/Title
            if filters.get('title'):
                body['position'] = [filters['title']]
                logger.debug("Using API filter: position")
                return body

            # PRIORITY 3: Seniority Level
            if filters.get('seniority_level'):
                seniority_map = {
                    'entry': 'Entry Level',
                    'mid': 'Mid Level',
                    'senior': 'Senior',
                    'specialist': 'Specialist',
                    'manager': 'Manager',
                    'director': 'Director',
                    'head': 'Head',
                    'vp': 'VP',
                    'c_level': 'C-Level',
                    'owner': 'Owner',
                    'partner': 'Partner',
                    'intern': 'Intern',
                }
                mapped_level = seniority_map.get(
                    filters['seniority_level'],
                    filters['seniority_level'].title()
                )
                body['level'] = [mapped_level]
                logger.debug(f"Using API filter: level = {mapped_level}")
                return body

            # PRIORITY 4: Industry
            if filters.get('industry'):
                body['company_industry'] = [filters['industry']]
                logger.debug("Using API filter: company_industry")
                return body

            # Default: No filters (will get broad results)
            logger.debug("No API filters applied - fetching all results")
            return body

        except Exception as e:
            logger.error(f"Error building request body: {e}")
            return {}

    def parse_lead_data(self, raw_lead: Dict) -> Dict:
        """Parse raw API lead data into our format."""
        try:
            first_name = raw_lead.get('name', '')
            last_name = raw_lead.get('surname', '')
            full_name = f"{first_name} {last_name}".strip()

            # Normalize LinkedIn URL
            linkedin_url = raw_lead.get('linkedin', '')
            if linkedin_url and not linkedin_url.startswith('http'):
                linkedin_url = f'https://{linkedin_url}'

            # Map seniority level
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

                # Professional info
                'current_title': raw_lead.get('position', ''),
                'current_company': raw_lead.get('company_name', ''),
                'company_linkedin_url': raw_lead.get('company_linkedin', ''),
                'headline': raw_lead.get('headline', ''),
                'level': raw_lead.get('level', ''),
                'department': raw_lead.get('department', ''),

                # Location mapping based on REAL API structure:
                # API "location" = actual country (e.g., "United States")
                # API "region" = geographical region (e.g., "Northern America")
                'location': raw_lead.get('location', ''),      # Country name
                # Geographical region
                'country': raw_lead.get('region', ''),
                # Keep consistency
                'region': raw_lead.get('region', ''),

                # Company info
                'industry': raw_lead.get('company_industry', ''),
                'company_size': raw_lead.get('company_headcount', ''),
                'company_domain': raw_lead.get('company_domain', ''),
                'company_location': raw_lead.get('company_location', ''),
                'company_founded': str(raw_lead.get('company_founded', '')),
                'company_revenue': raw_lead.get('company_revenue', ''),
                'company_subindustry': raw_lead.get('company_subindustry', ''),

                # Additional
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
        """
        if not api_level:
            return ''

        level_lower = api_level.lower().strip()

        mapping = {
            # Entry levels
            'entry': 'entry',
            'entry level': 'entry',
            'junior': 'entry',
            'intern': 'intern',

            # Mid levels
            'mid': 'mid',
            'mid level': 'mid',
            'intermediate': 'mid',

            # Senior levels
            'senior': 'senior',
            'sr': 'senior',
            'senior level': 'senior',

            # Specialist
            'specialist': 'specialist',

            # Management
            'manager': 'manager',
            'mgr': 'manager',
            'head': 'head',

            # Directors
            'director': 'director',
            'dir': 'director',

            # VP
            'vp': 'vp',
            'vice president': 'vp',

            # C-Level
            'c-level': 'c_level',
            'c level': 'c_level',
            'executive': 'c_level',
            'ceo': 'c_level',
            'cto': 'c_level',
            'cfo': 'c_level',
            'coo': 'c_level',
            'cmo': 'c_level',

            # Owners
            'owner': 'owner',
            'founder': 'owner',

            # Partners
            'partner': 'partner',
        }

        return mapping.get(level_lower, '')

    def filter_leads_locally(self, leads: List[Dict], filters: Dict) -> List[Dict]:
        """
        Apply client-side filters to leads.

        This is necessary because the API doesn't support multiple filters
        or certain filters like location, region, company name, etc.
        """
        if not filters:
            return leads

        # DEBUG: Log unique countries when no filters applied
        unique_locations = set(lead.get('location', 'Unknown')
                               for lead in leads)
        unique_regions = set(lead.get('region', 'Unknown') for lead in leads)
        logger.info(
            f"DEBUG: Unique locations in API response: {unique_locations}")
        logger.info(f"DEBUG: Unique regions in API response: {unique_regions}")

        filtered = leads
        original_count = len(leads)

        # Filter by name (first name + last name)
        name_query = filters.get('name', '').lower().strip()
        if name_query:
            # Split query into tokens (e.g. "John Smith" -> ["john", "smith"])
            query_tokens = name_query.split()

            filtered = [
                lead for lead in filtered
                if all(token in f"{lead.get('name', '')} {lead.get('surname', '')}".lower() for token in query_tokens)
            ]
            logger.debug(
                f"Name filter '{name_query}': {original_count} -> {len(filtered)} leads")

        # Filter by title (position)
        title = filters.get('title', '').lower().strip()
        if title:
            filtered = [
                lead for lead in filtered
                if title in lead.get('position', '').lower()
            ]
            logger.debug(
                f"Title filter '{title}': {len(leads)} -> {len(filtered)} leads")

        # Filter by company
        company = filters.get('company', '').lower()
        if company:
            filtered = [
                lead for lead in filtered
                if company in lead.get('company_name', '').lower()
            ]
            logger.debug(
                f"Company filter '{company}': {len(leads)} -> {len(filtered)} leads")

        # Filter by location (API "location" field contains country names)
        # CASE INSENSITIVE search
        location = filters.get('location', '').lower().strip()
        if location:
            before_count = len(filtered)
            filtered = [
                lead for lead in filtered
                if location in lead.get('location', '').lower()
            ]
            logger.debug(
                f"Location filter '{location}': {before_count} -> {len(filtered)} leads")

            # DEBUG: Show sample of what was filtered
            if len(filtered) == 0 and before_count > 0:
                sample_locations = list(
                    set(lead.get('location', 'N/A') for lead in leads[:10]))
                logger.warning(
                    f"Location filter '{location}' found 0 results. Sample locations in data: {sample_locations}")

        # Filter by region (API "region" field contains geographical regions)
        # CASE INSENSITIVE search
        region = filters.get('region', '').lower().strip()

        # Normalize common region names
        if region == 'north america':
            region = 'northern america'

        if region:
            before_count = len(filtered)
            filtered = [
                lead for lead in filtered
                if region in lead.get('region', '').lower() or region in lead.get('location', '').lower()
            ]
            logger.debug(
                f"Region filter '{region}': {before_count} -> {len(filtered)} leads")

            # DEBUG: Show sample of what was filtered
            if len(filtered) == 0 and before_count > 0:
                sample_regions = list(set(f"{lead.get('region', 'N/A')}|{lead.get('location', 'N/A')}"
                                      for lead in leads[:10]))
                logger.warning(
                    f"Region filter '{region}' found 0 results. Sample region|location in data: {sample_regions}")

        # Filter by seniority level
        seniority = filters.get('seniority_level')
        if seniority:
            filtered = [
                lead for lead in filtered
                if self._map_seniority(lead.get('level', '')) == seniority
            ]
            logger.debug(
                f"Seniority filter '{seniority}': {len(leads)} -> {len(filtered)} leads")

        # Filter by company size
        company_size = filters.get('company_size')
        if company_size:
            filtered = [
                lead for lead in filtered
                if lead.get('company_headcount', '') == company_size
            ]
            logger.debug(
                f"Company size filter '{company_size}': {len(leads)} -> {len(filtered)} leads")

        # Filter by industry (only if not already filtered by API)
        if not filters.get('industry'):
            industry_filter = filters.get('industry', '').lower()
            if industry_filter:
                filtered = [
                    lead for lead in filtered
                    if industry_filter in lead.get('company_industry', '').lower()
                ]
                logger.debug(
                    f"Industry filter '{industry_filter}': {len(leads)} -> {len(filtered)} leads")

        # Filter by keywords (searches in skills, headline, position, bio, industry, company)
        keywords = filters.get('keywords', '').lower().strip()
        if keywords:
            keyword_tokens = keywords.split()
            filtered = [
                lead for lead in filtered
                if all(
                    token in (
                        f"{lead.get('skills', '')} "
                        f"{lead.get('headline', '')} "
                        f"{lead.get('position', '')} "
                        f"{lead.get('bio', '')} "
                        f"{lead.get('company_industry', '')} "
                        f"{lead.get('company_name', '')}"
                    ).lower()
                    for token in keyword_tokens
                )
            ]
            logger.debug(
                f"Keywords filter '{keywords}': {len(leads)} -> {len(filtered)} leads")

        logger.info(
            f"Local filtering complete: {original_count} -> {len(filtered)} leads")

        return filtered
