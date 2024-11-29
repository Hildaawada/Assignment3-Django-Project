
# Create your views here.
from django.shortcuts import render, redirect
from .forms import ProfessionalForm
from .models import Professional
from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect
from .forms import ProfessionalForm

def add_professional(request):
    if request.method == 'POST':
        form = ProfessionalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Redirect after POST
    else:
        form = ProfessionalForm()
    return render(request, 'contact_app/add_professional.html', {'form': form})

def contact_list(request):
    contacts = Professional.objects.all()
    return render(request, 'contact_app/contact_list.html', {'contacts': contacts})



def edit_professional(request, id):
    professional = Professional.objects.get(pk=id)
    if request.method == 'POST':
        form = ProfessionalForm(request.POST, instance=professional)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Redirect after POST
    else:
        form = ProfessionalForm(instance=professional)
    return render(request, 'edit_professional.html', {'form': form})

def delete_professional(request, id):
    professional = get_object_or_404(Professional, pk=id)
    if request.method == 'POST':  # Ensures that the deletion is confirmed via POST request
        professional.delete()
        return redirect('professionals_list_url')  # Redirect to the list of professionals or a success page
    return render(request, 'confirm_delete.html', {'professional': professional})
