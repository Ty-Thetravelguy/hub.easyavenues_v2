from django.shortcuts import render

# Create your views here.
def external_links(request):
    return render(request, 'external_links/external_links.html')
