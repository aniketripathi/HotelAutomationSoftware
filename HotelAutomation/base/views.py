from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.cache import cache_control
from .models import User, Guest, Room, Discount, Catering

# Create your views here.

def login(request):
    error_message= ""
    request.session['username'] = None
    request.session['usertype'] = -1
    if request.method == 'POST':
        username = request.POST.get('username','')
        usertype = request.POST.get('usertype',"0")
        password = request.POST.get('password','')
        qs = User.objects.filter(username=username,password=password,usertype=usertype)
        if qs.exists():
            request.session['username'] = username
            request.session['usertype'] = usertype
            if int(usertype) == User.UserType.ADMINISTRATOR:
                return redirect('/base/admin')
                    
            elif int(usertype) == User.UserType.RECEPTIONIST:
                return redirect('/base/receptionist')
            else:
                return redirect('/base/catering_service_manager')
        else :
            error_message = 'Either username or password is invalid'
                 
    return render(request, 'login.html', {'error_message' : error_message})


def catering_service_manager(request):
    return render(request, 'catering_service_manager.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def receptionist(request):
    if 'username' in request.session and 'usertype' in request.session:
        username = request.session['username']
        usertype = request.session['usertype']
        if int(usertype) == User.UserType.RECEPTIONIST:
            rooms = list(Room.objects.all())
            return render(request, 'receptionist.html', {'rooms':rooms})
    return HttpResponse("<p> Access is Denied </p>")
     
    
def book_room(request):
    return render(request, 'book_room.html')
    
def checkout(request):
    return render(request, 'checkout.html')
    
def admin(request):
    return render(request, 'admin.html')
    