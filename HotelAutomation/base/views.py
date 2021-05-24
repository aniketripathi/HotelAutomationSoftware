from django.shortcuts import render

# Create your views here.

def login(request):
	return render(request, 'login.html')

def catering_service_manager(request):
    return render(request, 'catering_service_manager.html')
