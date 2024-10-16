
from django.urls import path
from . import views  

urlpatterns = [
    path('', views.add_contact, name='add_contact'),  
    path('contacts/', views.contact_list, name='contact_list'),  
    path('edit/<int:id>/', views.edit_contact, name='edit_contact'),  
    path('delete/<int:id>/', views.delete_contact, name='delete_contact'), 
]
