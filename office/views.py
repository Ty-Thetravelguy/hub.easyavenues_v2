from django.shortcuts import render

# Create your views here.
def office(request):
    return render(request, 'office/office.html')

