# leads/services/mock_linkedin_data.py
import random
from typing import Dict, List, Optional, Any


class MockLinkedInData:
    
    FIRST_NAMES = ["John", "Sarah", "Michael", "Emma", "David", "Lisa", "James", "Maria", "Robert", "Jennifer"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    COMPANIES = ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla", "Salesforce", "Adobe", "Oracle"]
    
    INDUSTRIES = ["Technology", "Software", "Financial Services", "Healthcare", "Consulting", "E-commerce", "Manufacturing"]
    
    COMPANY_SIZES = [
        "Myself Only", "1-10 employees", "11-50 employees", "51-200 employees",
        "201-500 employees", "501-1000 employees", "1001-5000 employees",
        "5001-10000 employees", "10001+ employees"
    ]
    
    LOCATIONS = {
        'United States': ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA"],
        'Canada': ["Toronto, ON", "Vancouver, BC"],
        'United Kingdom': ["London", "Manchester"]
    }
    
    LEVELS = ['Entry Level', 'Mid Level', 'Senior', 'Manager', 'Director', 'VP', 'C-Level']
    
    @staticmethod
    def generate_leads(count: int = 50, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate mock leads that MATCH the filters"""
        if filters is None:
            filters = {}
        
        leads: List[Dict[str, Any]] = []
        
        # Pre-determine values based on filters to ensure matches
        target_company = filters.get('company', random.choice(MockLinkedInData.COMPANIES))
        target_size = filters.get('company_size', random.choice(MockLinkedInData.COMPANY_SIZES))
        target_industry = filters.get('industry', random.choice(MockLinkedInData.INDUSTRIES))
        
        # Location handling
        if filters.get('location'):
            target_location = filters['location']
            target_country = "United States"  # Default
        elif filters.get('country'):
            target_country = filters['country']
            locations = MockLinkedInData.LOCATIONS.get(target_country, ["Unknown"])
            target_location = random.choice(locations)
        else:
            target_country = "United States"
            target_location = "San Francisco, CA"
        
        # Seniority mapping
        seniority_map = {
            'entry': 'Entry Level',
            'mid': 'Mid Level',
            'senior': 'Senior',
            'manager': 'Manager',
            'director': 'Director',
            'vp': 'VP',
            'c_level': 'C-Level',
        }
        
        target_level = 'Senior'  # Default
        if filters.get('seniority_level'):
            target_level = seniority_map.get(filters['seniority_level'], 'Senior')
        
        target_title = filters.get('title', 'Software Engineer')
        target_keywords = filters.get('keywords', 'Python')
        
        for i in range(count):
            # Use target values with some variation
            company = target_company if filters.get('company') else random.choice(MockLinkedInData.COMPANIES)
            company_size = target_size if filters.get('company_size') else random.choice(MockLinkedInData.COMPANY_SIZES)
            industry = target_industry if filters.get('industry') else random.choice(MockLinkedInData.INDUSTRIES)
            location = target_location if filters.get('location') or filters.get('country') else random.choice(MockLinkedInData.LOCATIONS['United States'])
            level = target_level if filters.get('seniority_level') else random.choice(MockLinkedInData.LEVELS)
            position = target_title if filters.get('title') else 'Software Engineer'
            
            # Build skills including keywords
            skills_base = ["Python", "JavaScript", "React", "AWS", "Docker", "SQL"]
            if filters.get('keywords'):
                if filters['keywords'] not in skills_base:
                    skills_base.append(filters['keywords'])
            skills = ", ".join(random.sample(skills_base, min(4, len(skills_base))))
            
            first_name = random.choice(MockLinkedInData.FIRST_NAMES)
            last_name = random.choice(MockLinkedInData.LAST_NAMES)
            
            lead: Dict[str, Any] = {
                "id": 10000 + i,
                "name": first_name,
                "surname": last_name,
                "linkedin": f"linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{i}",
                "location": location,
                "region": target_country,
                "position": position,
                "headline": f"{position} at {company}",
                "level": level,
                "department": random.choice(["Engineering", "Sales", "Marketing", "Operations", ""]),
                "skills": skills,
                "company_name": company,
                "company_domain": f"{company.lower().replace(' ', '')}.com",
                "company_linkedin": f"https://linkedin.com/company/{company.lower().replace(' ', '-')}",
                "company_location": location,
                "company_industry": industry,
                "company_subindustry": f"Specialized {industry}",
                "company_headcount": company_size,
                "company_founded": str(random.randint(1990, 2020)),
                "company_revenue": random.choice(["$1M-$10M", "$10M-$50M", "$100M+", "Not Known"])
            }
            leads.append(lead)
        
        return leads