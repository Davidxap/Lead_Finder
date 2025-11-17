# leads/urls.py
from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    # Main search page
    path('', views.search_leads, name='search'),
    path('search/', views.search_leads, name='search_leads'),
    
    # List management
    path('lists/', views.view_lists, name='view_lists'),
    path('lists/create/', views.create_list, name='create_list'),
    path('lists/<int:list_id>/delete/', views.delete_list, name='delete_list'),
    path('lists/<int:list_id>/export/', views.export_list_csv, name='export_list'),
    
    # Lead operations
    path('add-to-list/', views.add_to_list, name='add_to_list'),
    path('bulk-add-to-list/', views.bulk_add_to_list, name='bulk_add_to_list'),
    path('lead/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    path('lists/<int:list_id>/remove/<int:lead_id>/', views.remove_from_list, name='remove_from_list'),
]