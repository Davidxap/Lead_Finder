# leads/views.py
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import csv

from .forms import LeadSearchForm, CreateListForm, AddToListForm
from .models import Lead, LeadList, LeadListItem
from .services.linkedin_api import LinkedInAPIService
from .services.lead_service import LeadService

logger = logging.getLogger(__name__)


def search_leads(request):
    """
    Main search view - displays filters and results.
    Apollo-style interface with sidebar filters and results table.
    """
    form = LeadSearchForm(request.GET or None)
    api_service = LinkedInAPIService()
    
    # Initialize context
    context = {
        'form': form,
        'leads': [],
        'page_obj': None,
        'total_results': 0,
        'has_searched': False,
        'error': None,
        'all_lists': LeadList.objects.all().order_by('name'),
    }
    
    # If form is submitted and valid
    if request.GET and form.is_valid():
        context['has_searched'] = True
        filters = form.get_filters_dict()
        
        # Fetch leads from API
        api_response = api_service.fetch_leads(filters)
        
        if api_response['success']:
            raw_leads = api_response['results']
            
            # Parse leads
            parsed_leads = []
            for raw_lead in raw_leads:
                try:
                    parsed_lead = api_service.parse_lead_data(raw_lead)
                    parsed_leads.append(parsed_lead)
                except Exception as e:
                    logger.error(f"Error parsing lead: {str(e)}")
            
            # Apply local filters if needed
            if filters.get('name') or filters.get('seniority_level') or filters.get('company_size'):
                raw_leads_filtered = api_service.filter_leads_locally(raw_leads, filters)
                # Re-parse filtered leads
                parsed_leads = []
                for raw_lead in raw_leads_filtered:
                    try:
                        parsed_lead = api_service.parse_lead_data(raw_lead)
                        parsed_leads.append(parsed_lead)
                    except Exception as e:
                        logger.error(f"Error parsing filtered lead: {str(e)}")
            
            context['total_results'] = len(parsed_leads)
            
            # Pagination
            page = request.GET.get('page', 1)
            per_page = settings.LEADS_PER_PAGE
            
            paginator = Paginator(parsed_leads, per_page)
            
            try:
                page_obj = paginator.get_page(page)
            except PageNotAnInteger:
                page_obj = paginator.get_page(1)
            except EmptyPage:
                page_obj = paginator.get_page(paginator.num_pages)
            
            context['page_obj'] = page_obj
            context['leads'] = page_obj.object_list
            
            # Add message if no results
            if context['total_results'] == 0:
                messages.info(request, 'No leads found with the given filters. Try adjusting your search.')
        else:
            context['error'] = api_response['error']
            messages.error(request, f"Error fetching leads: {api_response['error']}")
    
    return render(request, 'leads/search.html', context)


@require_http_methods(["POST"])
def add_to_list(request):
    """
    Add a lead to a list.
    Can be called via form submission.
    """
    # Get lead data from POST
    external_id = request.POST.get('external_id')
    list_name = request.POST.get('list_name')
    
    if not external_id or not list_name:
        messages.error(request, 'Missing required information.')
        return redirect('leads:search')
    
    # Get all lead data from POST
    lead_data = {
        'external_id': external_id,
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', ''),
        'full_name': request.POST.get('full_name', ''),
        'email': request.POST.get('email', ''),
        'phone': request.POST.get('phone', ''),
        'linkedin_url': request.POST.get('linkedin_url', ''),
        'current_title': request.POST.get('current_title', ''),
        'current_company': request.POST.get('current_company', ''),
        'company_linkedin_url': request.POST.get('company_linkedin_url', ''),
        'headline': request.POST.get('headline', ''),
        'location': request.POST.get('location', ''),
        'country': request.POST.get('country', ''),
        'industry': request.POST.get('industry', ''),
        'company_size': request.POST.get('company_size', ''),
        'seniority_level': request.POST.get('seniority_level', ''),
        'skills': request.POST.get('skills', ''),
        'bio': request.POST.get('bio', ''),
    }
    
    try:
        # Create or update lead
        lead = LeadService.create_or_update_lead(lead_data)
        
        # Add to list
        success, message = LeadService.add_lead_to_list(lead, list_name)
        
        if success:
            messages.success(request, message)
        else:
            messages.warning(request, message)
            
    except Exception as e:
        logger.error(f"Error adding lead to list: {str(e)}")
        messages.error(request, f"Error: {str(e)}")
    
    # Redirect back to search with filters preserved
    return redirect(request.META.get('HTTP_REFERER', 'leads:search'))


def view_lists(request):
    """
    View all lists with their leads.
    """
    lists_data = LeadService.get_all_lists_with_leads()
    
    context = {
        'lists': lists_data,
        'total_lists': len(lists_data),
    }
    
    return render(request, 'leads/lists.html', context)


@require_http_methods(["POST"])
def create_list(request):
    """
    Create a new list.
    """
    form = CreateListForm(request.POST)
    
    if form.is_valid():
        name = form.cleaned_data['name']
        description = form.cleaned_data['description']
        
        success, message, lead_list = LeadService.create_list(name, description)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    else:
        messages.error(request, 'Invalid form data.')
    
    return redirect('leads:view_lists')


@require_http_methods(["POST"])
def delete_list(request, list_id):
    """
    Delete a list.
    """
    lead_list = get_object_or_404(LeadList, id=list_id)
    
    success, message = LeadService.delete_list(lead_list)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('leads:view_lists')


@require_http_methods(["POST"])
def remove_from_list(request, list_id, lead_id):
    """
    Remove a lead from a list.
    """
    lead_list = get_object_or_404(LeadList, id=list_id)
    lead = get_object_or_404(Lead, id=lead_id)
    
    success, message = LeadService.remove_lead_from_list(lead, lead_list)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('leads:view_lists')


def export_list_csv(request, list_id):
    """
    Export a list to CSV file.
    """
    lead_list = get_object_or_404(LeadList, id=list_id)
    leads = LeadService.get_leads_in_list(lead_list)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{lead_list.slug}_export.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'First Name',
        'Last Name',
        'Email',
        'Phone',
        'Job Title',
        'Company',
        'LinkedIn URL',
        'Location',
        'Country',
        'Industry',
        'Seniority Level',
        'Company Size',
    ])
    
    # Write data
    for lead in leads:
        # Get seniority display name
        seniority_display = ''
        if lead.seniority_level:
            for code, display in Lead.SENIORITY_CHOICES:
                if code == lead.seniority_level:
                    seniority_display = display
                    break
        
        writer.writerow([
            lead.first_name,
            lead.last_name,
            lead.email or '',
            lead.phone or '',
            lead.current_title,
            lead.current_company,
            lead.linkedin_url,
            lead.location,
            lead.country,
            lead.industry,
            seniority_display,
            lead.company_size,
        ])
    
    messages.success(request, f'List "{lead_list.name}" exported successfully.')
    return response


def lead_detail(request, lead_id):
    """
    View detailed information about a lead.
    """
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Get all lists this lead is in
    lists = LeadList.objects.filter(list_items__lead=lead)
    
    context = {
        'lead': lead,
        'lists': lists,
        'skills_list': lead.get_skills_list(),
    }
    
    return render(request, 'leads/lead_detail.html', context)


@require_http_methods(["POST"])
def bulk_add_to_list(request):
    """
    Add multiple leads to a list at once.
    """
    # Get lead IDs from POST (comma-separated)
    lead_ids = request.POST.get('lead_ids', '').split(',')
    list_name = request.POST.get('list_name')
    
    if not lead_ids or not list_name:
        messages.error(request, 'Missing required information.')
        return redirect('leads:search')
    
    # Get all lead data from POST (JSON format)
    import json
    leads_data = json.loads(request.POST.get('leads_data', '[]'))
    
    created_leads = []
    for lead_data in leads_data:
        try:
            lead = LeadService.create_or_update_lead(lead_data)
            created_leads.append(lead)
        except Exception as e:
            logger.error(f"Error creating lead: {str(e)}")
    
    # Bulk add to list
    result = LeadService.bulk_add_leads_to_list(created_leads, list_name)
    
    messages.success(
        request,
        f"Added {result['added']} leads to '{list_name}'. "
        f"Skipped {result['skipped']} duplicates."
    )
    
    return redirect('leads:search')