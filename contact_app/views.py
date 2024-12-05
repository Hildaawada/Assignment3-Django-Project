
# Create your views here.
from django.shortcuts import render, redirect
from .forms import ProfessionalForm
from .models import Professional
from django.shortcuts import get_object_or_404
from .nlp_utils import find_recommendations



def search_query(request):
    query = request.GET.get('query', '')
    recommendations = []

    if query:
        contacts = Professional.objects.all().values()  # Fetch all profiles or contacts
        recommendations = find_recommendations(query, list(contacts))  # Your recommendation logic

    return render(request, 'contact_app/search_query.html', {'query': query, 'recommendations': recommendations})
def add_professional(request):
    if request.method == 'POST':
        form = ProfessionalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Redirect to the success page
    else:
        form = ProfessionalForm()
    return render(request, 'contact_app/add_professional.html', {'form': form})

def contact_list(request):
    contacts = Professional.objects.all()
    return render(request, 'contact_app/contact_list.html', {'contacts': contacts})

def success_page(request):
    return render(request, 'contact_app/success_page.html')  # Render the success page template


def edit_professional(request, id):
    professional = Professional.objects.get(pk=id)
    if request.method == 'POST':
        form = ProfessionalForm(request.POST, instance=professional)
        if form.is_valid():
            form.save()
            return redirect('contact_list')  # Redirect after POST
    else:
        form = ProfessionalForm(instance=professional)
    return render(request, 'contact_app/edit_professional.html', {'form': form})

def delete_professional(request, id):
    professional = get_object_or_404(Professional, pk=id)
    if request.method == 'POST':  # Ensures that the deletion is confirmed via POST request
        professional.delete()
        return redirect('contact_list')  # Redirect to the list of professionals or a success page
    return render(request, 'contact_app/delete_professional.html', {'professional': professional})
