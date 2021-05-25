from django.shortcuts import render

# Create your views here.

def login(request):
	return render(request, 'login.html')

def catering_service_manager(request):
    return render(request, 'catering_service_manager.html')

def receptionist(request):
    return render(request, 'receptionist.html')
    
def book_room(request):
    return render(request, 'book_room.html')
    
def checkout(request):
    return render(request, 'checkout.html')