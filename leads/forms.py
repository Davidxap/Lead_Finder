# leads/forms.py
from django import forms
from leads.models import LeadList


class LeadSearchForm(forms.Form):
    """
    Form for searching leads with filters.
    Mirrors Apollo's filter interface.
    """
    
    # Basic Filters
    name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name...',
        })
    )
    
    company = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name...',
        })
    )
    
    title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title...',
            'label': 'Job Title'
        })
    )
    
    # Location Filters
    COUNTRY_CHOICES = [
        ('', '-- Select Country --'),
        ('United States', 'United States'),
        ('United Kingdom', 'United Kingdom'),
        ('Canada', 'Canada'),
        ('Australia', 'Australia'),
        ('Germany', 'Germany'),
        ('France', 'France'),
        ('Spain', 'Spain'),
        ('Italy', 'Italy'),
        ('Netherlands', 'Netherlands'),
        ('Belgium', 'Belgium'),
        ('Brazil', 'Brazil'),
        ('Mexico', 'Mexico'),
        ('India', 'India'),
        ('China', 'China'),
        ('Japan', 'Japan'),
    ]
    
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State...',
        })
    )
    
    # Industry Filter
    industry = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Industry...',
        })
    )
    
    # Seniority Filter
    SENIORITY_CHOICES = [
        ('', '-- Select Level --'),
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('vp', 'VP'),
        ('c_level', 'C-Level'),
        ('owner', 'Owner/Founder'),
        ('partner', 'Partner'),
    ]
    
    seniority_level = forms.ChoiceField(
        choices=SENIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    # Company Size Filter
    COMPANY_SIZE_CHOICES = [
        ('', '-- Select Size --'),
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001-5000', '1001-5000 employees'),
        ('5001-10000', '5001-10000 employees'),
        ('10001+', '10000+ employees'),
    ]
    
    company_size = forms.ChoiceField(
        choices=COMPANY_SIZE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    # Keywords (Skills, Bio, etc.)
    keywords = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Keywords (skills, bio, etc.)...',
        })
    )
    
    # Results limit
    limit = forms.IntegerField(
        initial=100,
        required=False,
        widget=forms.HiddenInput()
    )
    
    def get_filters_dict(self):
        """
        Return cleaned data as a dictionary for API consumption.
        Removes empty values.
        """
        if not self.is_valid():
            return {}
        
        filters = {}
        for field, value in self.cleaned_data.items():
            if value:  # Only include non-empty values
                filters[field] = value
        
        return filters


class CreateListForm(forms.ModelForm):
    """
    Form to create a new lead list.
    """
    
    class Meta:
        model = LeadList
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Hot Prospects Q1 2025',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional description...',
                'rows': 3,
            }),
        }
        labels = {
            'name': 'List Name',
            'description': 'Description (Optional)',
        }


class AddToListForm(forms.Form):
    """
    Form to add a lead to an existing list or create a new one.
    """
    
    # Select existing list
    existing_list = forms.ModelChoiceField(
        queryset=LeadList.objects.all(),
        required=False,
        empty_label="-- Select Existing List --",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'existing-list-select',
        })
    )
    
    # Or create new list
    new_list_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Or create a new list...',
            'id': 'new-list-input',
        })
    )
    
    # Optional notes
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add notes about this lead (optional)...',
            'rows': 2,
        })
    )
    
    def clean(self):
        """
        Validate that either existing_list or new_list_name is provided.
        """
        cleaned_data = super().clean()
        existing_list = cleaned_data.get('existing_list')
        new_list_name = cleaned_data.get('new_list_name')
        
        if not existing_list and not new_list_name:
            raise forms.ValidationError(
                "Please select an existing list or create a new one."
            )
        
        return cleaned_data
    
    def get_list_name(self):
        """
        Return the list name to use (either existing or new).
        """
        if self.cleaned_data.get('existing_list'):
            return self.cleaned_data['existing_list'].name
        return self.cleaned_data.get('new_list_name', '')