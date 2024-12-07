from django.urls import path
from . import views  

urlpatterns = [
    path('contactadd/', views.add_professional, name='add_contact'),  
    path('contacts/', views.contact_list, name='contact_list'),  
    path('edit/<int:id>/', views.edit_professional, name='edit_contact'),  
    path('delete/<int:id>/', views.delete_professional, name='delete_contact'), 
    path('', views.search_query, name='search_query'),
    path('success/', views.success_page, name='success')  # New path for the success page


]
