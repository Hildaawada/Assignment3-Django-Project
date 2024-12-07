from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfessionalForm
from .models import Professional
from .nlp_utils import find_recommendations


def search_query(request):
    query = request.GET.get('query', '')
    error_message = None
    recommendations = []

    if query:
        contacts = Professional.objects.all().values()  # Fetch all profiles or contacts
        result = find_recommendations(query, list(contacts))

        if isinstance(result, str):
            # result is an error message
            error_message = result
        else:
            # result is a list of recommendations
            recommendations = result

    return render(
        request, 
        'contact_app/search_query.html', 
        {
            'query': query, 
            'recommendations': recommendations,
            'error_message': error_message
        }
    )


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
    professional = get_object_or_404(Professional, pk=id)
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
