from django.shortcuts import render

# Create your views here.
def query_log(request):
    return render(request, 'query_log/query_log.html')

