
# Create your views here.
from django.shortcuts import render, redirect
from .forms import ContactForm
from .models import Contact
from django.shortcuts import get_object_or_404

def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm()
    return render(request, 'contact_app/add_contact.html', {'form': form})

def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'contact_app/contact_list.html', {'contacts': contacts})



def edit_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contact_app/edit_contact.html', {'form': form, 'contact': contact})

def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    if request.method == 'POST':
        contact.delete()
        return redirect('contact_list')
    return render(request, 'contact_app/delete_contact.html', {'contact': contact})
