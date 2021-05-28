from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.cache import cache_control
from datetime import datetime, timedelta
from .models import User, Guest, Room, Discount, Catering

# Create your views here.

token = 0

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
    if check_access(request, User.UserType.RECEPTIONIST):
        rooms = list(Room.objects.all())
        return render(request, 'receptionist.html', {'rooms':rooms})
        
    return access_denied()
    
     
    
def book_room(request):
    if check_access(request, User.UserType.RECEPTIONIST) or check_access(request, User.UserType.ADMINISTRATOR):
        rooms = list(Room.objects.all())
        message = 'qweqw'
        if request.method == 'POST':
            room_number = request.POST.get('room_number', 0)
            guest_name = request.POST.get('guest_name', '')
            guest_id = request.POST.get('guest_id', '')
            date = request.POST.get('date', None)
            time = request.POST.get('time', None)
            days = request.POST.get('days', 1)
            advance = request.POST.get('advance', False)
            use_discount = request.POST.get('use_discount', False)
            discount = request.POST.get('discount', 0)
            phone_number = request.POST.get('phone_number', '')
            error, message = validate_booking(Room.objects.get(room_number=room_number), guest_name, guest_id, date, time, days, advance, use_discount, discount, phone_number)
        print(error)
        return render(request, 'book_room.html', {'rooms':rooms, 'message':message, 'error':error})
    return access_denied()
    
def checkout(request):
    return render(request, 'checkout.html')
    
def admin(request):
    return render(request, 'admin.html')
    
# Non views method

def check_access(request, accesstype):
    access = False
    if 'username' in request.session and 'usertype' in request.session:
        username = request.session['username']
        usertype = request.session['usertype']
        if int(usertype) == accesstype:
            access = True
    return access_denied
    
    
def access_denied():
    return HttpResponse("<p> Access is Denied </p>")()


def validate_booking(room, guest_name, guest_id, date, time, days, advance, use_discount, discount, phone_number):
    msg = ''
    error = True
    # First Check whether input data is valid
    
    if guest_name and guest_id and date and time and phone_number :
        when = datetime.fromisoformat(date+' '+time)
        t_delta = timedelta(days=int(days))
        
        if room.occupied and room.advance:
            msg += 'This room both occupied and booked in advanced.\n'
        
        elif room.occupied and not room.advance:
            if advance == 'on':
                occ_date = room.occupied_when
                occ_delta = datetime.timedelta(days=room.days)
                if occ_date + occ_delta < advance:
                    db_book_room(room, guest_name, guest_id, when, days, True, use_discount, discount, phone_number)
                    error=False
                    msg += 'Room booked successfully in advance. The token number is ' + str(token) + '.\n'
                
                else: msg += 'Room is booked for that period. Please select another date.\n'
                    
            else: msg += 'Room is already occupied.\n'
        
        elif not room.occupied and room.advance:
            if advance == 'on':
                msg += 'Room is already booked in advance.\n'
            
            else:
                adv_date = room.book_when
                if when+t_delta < adv_date:
                    db_book_room(room, guest_name, guest_id, when, days, False, use_discount, discount, phone_number)
                    error=False
                    msg += 'Room booked successfully. The token number is ' + str(token) + '.\n'
                
                else: msg += 'Room is booked for that period. Please change duration. \n'
        else:
            if advance == 'on':
                db_book_room(room, guest_name, guest_id, when, days, True, use_discount, discount, phone_number)
                error=False
                msg += 'Room booked successfully in advance. The token number is ' + str(token) + '.\n'
            
            else:
                db_book_room(room, guest_name, guest_id, when, days, False, use_discount, discount, phone_number)
                error=False
                msg += 'Room booked successfully. The token number is ' + str(token) + '.\n'
        
      
    return error,msg


def get_token(room_number):
    global token
    token = token+1
    return token
    
def db_book_room(room, guest_name, guest_id, when, days, advance, use_discount, discount, phone_number):
    
    token = get_token(room.room_number)
    guest = Guest(token=token, name=guest_name, id=guest_id, discount=discount, phone=phone_number)
    print(when, type(when))
    if advance:
        room.advance = True
        room.book_when = when
        room.book_days = int(days)
        room.token = guest
    else:
        room.occupied = True
        room.occupied_when = when
        room.days = int(days)
        room.occupancy_rate += 1
        room.token = guest
        
    
    guest.save()
    room.save()
    print(room.guest.token)
