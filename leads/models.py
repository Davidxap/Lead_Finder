# leads/models.py
from django.db import models
from django.core.validators import URLValidator
from django.utils.text import slugify
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Lead(models.Model):
    """
    Model to store lead information from LinkedIn API.
    Each lead represents a person with professional information.
    """
    
    # Basic Information
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    full_name = models.CharField(max_length=200, blank=True)
    
    # Contact Information
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    
    # LinkedIn Information
    linkedin_url = models.URLField(max_length=500, blank=True, validators=[URLValidator()])
    photo_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Professional Information
    current_title = models.CharField(max_length=255, db_index=True)
    current_company = models.CharField(max_length=255, db_index=True)
    company_linkedin_url = models.URLField(max_length=500, blank=True)
    headline = models.TextField(blank=True)
    
    # Location
    location = models.CharField(max_length=255, db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    
    # Company Information
    industry = models.CharField(max_length=255, db_index=True, blank=True)
    company_size = models.CharField(max_length=100, blank=True)
    
    # Seniority
    SENIORITY_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('vp', 'VP'),
        ('c_level', 'C-Level'),
        ('owner', 'Owner'),
        ('partner', 'Partner'),
    ]
    seniority_level = models.CharField(
        max_length=20, 
        choices=SENIORITY_CHOICES, 
        blank=True,
        db_index=True
    )
    
    # Additional Information
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    bio = models.TextField(blank=True)
    
    # External Reference
    external_id = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True,
        help_text="Unique identifier from LinkedIn API"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    if TYPE_CHECKING:
        list_items: 'RelatedManager[LeadListItem]'
    
    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['current_company']),
            models.Index(fields=['country', 'location']),
            models.Index(fields=['industry']),
            models.Index(fields=['seniority_level']),
        ]
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
    
    def __str__(self) -> str:
        return f"{self.get_full_name()} - {self.current_company}"
    
    def save(self, *args, **kwargs) -> None:
        """Override save to auto-populate full_name"""
        if not self.full_name:
            self.full_name = self.get_full_name()
        super().save(*args, **kwargs)
    
    def get_full_name(self) -> str:
        """Return full name of the lead"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_skills_list(self) -> List[str]:
        """Return skills as a list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []
    
    def has_email(self) -> bool:
        """Check if lead has email"""
        return bool(self.email)
    
    def has_phone(self) -> bool:
        """Check if lead has phone"""
        return bool(self.phone)


class LeadList(models.Model):
    """
    Model to store custom lists created by users.
    Users can organize leads into different lists.
    """
    
    name = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True,
        help_text="Unique name for the list"
    )
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    if TYPE_CHECKING:
        list_items: 'RelatedManager[LeadListItem]'
    
    class Meta:
        db_table = 'lead_lists'
        ordering = ['-created_at']
        verbose_name = 'Lead List'
        verbose_name_plural = 'Lead Lists'
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs) -> None:
        """Override save to auto-generate slug"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_lead_count(self) -> int:
        """Return number of leads in this list"""
        return self.list_items.count()
    
    def get_leads(self) -> models.QuerySet['Lead']:
        """Return all leads in this list"""
        return Lead.objects.filter(list_items__lead_list=self)


class LeadListItem(models.Model):
    """
    Model to store the many-to-many relationship between Leads and Lists.
    This allows tracking when a lead was added to a list.
    """
    
    lead = models.ForeignKey(
        Lead, 
        on_delete=models.CASCADE, 
        related_name='list_items'
    )
    lead_list = models.ForeignKey(
        LeadList, 
        on_delete=models.CASCADE, 
        related_name='list_items'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Optional notes about this lead in this list")
    
    class Meta:
        db_table = 'lead_list_items'
        unique_together = ('lead', 'lead_list')  # Prevent duplicates
        ordering = ['-added_at']
        verbose_name = 'Lead List Item'
        verbose_name_plural = 'Lead List Items'
    
    def __str__(self) -> str:
        return f"{self.lead.get_full_name()} in {self.lead_list.name}"