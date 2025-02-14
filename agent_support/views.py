from django.shortcuts import render

# Create your views here.
def agent_support(request):
    return render(request, 'agent_support/agent_support.html')

