from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.cache import cache_control
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_UP
from .models import User, Guest, Room, Discount, Catering

# Create your views here.

def login(request):
    error_message= ''
    clear_session(request)
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
            
            elif int(usertype) == User.UserType.CATERING_SERVICE_MANAGER:
                return redirect('/base/catering_service_manager')
            else:
                error_message = 'Invalid User Type'
            
        else :
            error_message = 'Either username or password is invalid'
                 
    return render(request, 'login.html', {'error_message' : error_message})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def catering_service_manager(request):
    
    if check_access(request, User.UserType.CATERING_SERVICE_MANAGER) or check_access(request, User.UserType.ADMINISTRATOR):
        
        if not request.session['retreived']:
            guest_name = ''
            msg = ''
            room_number = ''
            error = True
            token = 0
        else : 
            guest_name = request.session['guest_name']
            error = False
            room_number = request.session['room_number']
            token = request.session['token']
            msg = 'Token Successfully Retreived.'
            
            token = request.session['token']
            
        if request.method == 'POST':
            
            if 'token' in request.POST:
                token = request.POST.get('token', None)
                guest = Guest.objects.filter(id=token)
                if guest.exists():
                    room = Room.objects.filter(token=token)
                    room_number = room[0].room_number
                    guest_name = guest[0].name
                    error = False
                    request.session['room_number'] = room_number
                    request.session['guest_name'] = guest_name
                    request.session['token'] = token
                    request.session['retreived'] = True
                    msg = 'Token successfully retreived.'
                else :
                    error = True
                    msg = 'Invalid Token.'
                    guest_name=''
                    room_number=''
                    request.session['retreived'] = False
                    
            elif not error and 'item1' in request.POST:
                i = 1
                item_id = 'item'+str(i)
                price_id = 'price'+str(i)
                item = request.POST.get(item_id,None)
                price = request.POST.get(price_id, None)
                
                while item and price:
                    Catering(token=token,food_item=item, price=price).save()
                    i += 1
                    item_id = 'item'+str(i)
                    price_id = 'price'+str(i)
                    item = request.POST.get(item_id,None)
                    price = request.POST.get(price_id, None)
                msg = 'Successfully added.'
               
            else :
                error = True
                msg = 'Enter valid token before submitting'
          
        else: token = None
        
        return render(request, 'catering_service_manager.html' , {'guest_name':guest_name, 'error':error, 'message':msg, 'token': token, 'room_number':room_number})
       
    return access_denied()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def receptionist(request):
    if check_access(request, User.UserType.RECEPTIONIST):
        rooms = list(Room.objects.all())
        return render(request, 'receptionist.html', {'rooms':rooms})
        
    return access_denied()
    
     
    
def book_room(request):
    if check_access(request, User.UserType.RECEPTIONIST) or check_access(request, User.UserType.ADMINISTRATOR):
        rooms = list(Room.objects.all())
        error = False
        message = ''
        if request.method == 'POST':
            room_number = int(request.POST.get('room_number', 0))
            guest_name = request.POST.get('guest_name', '')
            guest_id = request.POST.get('guest_id', '')
            date = request.POST.get('date', None)
            time = request.POST.get('time', None)
            days = int(request.POST.get('days', 1))
            advance = request.POST.get('advance', False)
            use_discount = request.POST.get('use_discount', False)
            discount = int(request.POST.get('discount', 0))
            phone_number = request.POST.get('phone_number', '')
            error, message = validate_booking(Room.objects.get(room_number=room_number), guest_name, guest_id, date, time, days, advance, use_discount, discount, phone_number)
        return render(request, 'book_room.html', {'rooms':rooms, 'message':message, 'error':error})
    return access_denied()
    
    
def generate_bill(request):
    if check_access(request, User.UserType.RECEPTIONIST) or check_access(request, User.UserType.ADMINISTRATOR):
        token = request.session['token']
        guests = Guest.objects.filter(id=token)
        if guests.exists():
            rooms = Room.objects.filter(token=token)
            if rooms.exists:
                room = rooms[0]
                guest = guests[0]
                # Get data to generate bill
                guest_name = guest.name
                guest_id = guest.identification
                phone_number = guest.phone
                room_number = room.room_number
                bed = room.bed
                ac = room.ac
                occupied_when_date = room.occupied_when.date()
                occupied_when_time = room.occupied_when.time()
                days = room.days
                checkout_when_date = datetime.today().date()
                checkout_when_time = datetime.today().time()
                discount = guest.discount
                room_charges = Decimal(days * room.price * Decimal(1-discount/100.0))
                room_charges = room_charges.quantize(Decimal('.01'), rounding=ROUND_UP)
                items = Catering.objects.filter(token=token)
                if items.count() == 1:
                    items = [items]
                catering_bill = Decimal(0.0)
                for item in items:
                    catering_bill += item.price
                catering_bill = catering_bill.quantize(Decimal('.01'), rounding=ROUND_UP)
                total_bill = catering_bill + room_charges
                total_bill = total_bill.quantize(Decimal('.01'), rounding=ROUND_UP)
                
                context = {
                'guest_name': guest_name,
                'guest_id': guest_id,
                'phone_number': phone_number,
                'bed': bed,
                'ac': ac,
                'room_number': room_number,
                'occupied_when_date': occupied_when_date,
                'occupied_when_time': occupied_when_time,
                'checkout_when_date': checkout_when_date,
                'checkout_when_time': checkout_when_time,
                'days': days,
                'discount': discount,
                'room_charges': room_charges,
                'items': items,
                'catering_bill': catering_bill,
                'total_bill': total_bill
                }
                items.all().delete()
                room.occupied_when = None
                room.days = 0
                room.token = -1
                room.occupied = False
                room.save()
                guest.delete()
                return render(request, 'generate_bill.html', context)
        
        return HttpResponse('<p>Invalid Token</p>')
    return access_denied()
    

def checkout(request):
    if check_access(request, User.UserType.RECEPTIONIST) or check_access(request, User.UserType.ADMINISTRATOR):
        guest_name = ''
        room_number =  ''
        msg = ''
        error = False
        token = 0
        if request.session['token']:
            token = request.session['token']
        if request.method == 'POST':
            token = int(request.POST.get('token', None))
            guest = Guest.objects.filter(id=token)
            if guest.exists():
                room = Room.objects.filter(token=guest[0].token)
                if room.exists():
                    guest_name = guest[0].name
                    room_number = room[0].room_number
                    request.session['token'] = token
                    msg = 'Token Retreived successfully'
                else:
                    error=True
                    request.session['token'] = None
                    room_number = ''
                    token = None
                    msg = 'Invalid Token'
                
            else :
                error = True
                request.session['token'] = None
                room_number = ''
                token = None
                msg = 'Invalid Token'
        
        return render(request, 'checkout.html' , {'guest_name':guest_name, 'error':error, 'message':msg, 'room_number':room_number, 'token':token})
    return access_denied()


@cache_control(no_cache=True, must_revalidate=True, no_store=True)   
def admin(request):
    return render(request, 'admin.html')
    
    
def check_discount(request):
    if check_access(request, User.UserType.RECEPTIONIST) or check_access(request, User.UserType.ADMINISTRATOR):
        guest_name = ''
        discount =  0
        msg = ''
        error = False
        if request.method == 'POST':
            phone_number = request.POST.get('phone_number', None)
            guest_info = Discount.objects.filter(phone=phone_number)
            if guest_info.exists() :
                guest_name = guest_info[0].name
                discount = guest_info[0].discount
            else :
                error = True
                msg = 'You have not signed up for a discount.'
        return render(request, 'check_discount.html', {'guest_name':guest_name, 'discount':discount, 'error':error, 'message':msg})
    return access_denied()
 
# Non views method

def check_access(request, accesstype):
    access = False
    if 'username' in request.session and 'usertype' in request.session:
        username = request.session['username']
        usertype = request.session['usertype']
        
        if username and usertype and int(usertype) == accesstype:
            access = True
    return access
    
    
def access_denied():
    return HttpResponse("<p> Access is Denied </p>")


def validate_booking(room, guest_name, guest_id, date, time, days, advance, use_discount, discount, phone_number):
    msg = ''
    error = True
    # First Check whether input data is valid
    
    if guest_name and guest_id and date and time and phone_number :
        when = datetime.fromisoformat(date+' '+time)
        t_delta = timedelta(days=days)
        
        if room.occupied and room.advance:
            msg += 'This room both occupied and booked in advanced.\n'
        
        elif room.occupied and not room.advance:
            if advance == 'on':
                occ_date = room.occupied_when
                occ_delta = datetime.timedelta(days=room.days)
                if occ_date + occ_delta < advance:
                    db_book_room(room, guest_name, guest_id, when, days, True, use_discount, discount, phone_number)
                    token = room.token
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
                    token = room.token
                    msg += 'Room booked successfully. The token number is ' + str(token) + '.\n'
                
                else: msg += 'Room is booked for that period. Please change duration. \n'
        else:
            if advance == 'on':
                db_book_room(room, guest_name, guest_id, when, days, True, use_discount, discount, phone_number)
                error=False
                token = room.token
                msg += 'Room booked successfully in advance. The token number is ' + str(token) + '.\n'
            
            else:
                db_book_room(room, guest_name, guest_id, when, days, False, use_discount, discount, phone_number)
                error=False
                token = room.token
                msg += 'Room booked successfully. The token number is ' + str(token) + '.\n'
        
      
    return error,msg

    
def db_book_room(room, guest_name, guest_id, when, days, advance, use_discount, discount, phone_number):
    
    if use_discount == 'on':
        guest_info = Discount.objects.filter(phone=phone_number)
        if guest_info.exists():
            guest_discount = guest_info[0]
            if discount > guest_discount.discount:
                discount = guest_discount.discount
                guest_discount.discount = min(days, 25)
            else : guest_discount.discount = min(guest_discount.discount - discount + days, 25)
            guest_discount.save()
        else:
            Discount(phone=phone_number, name=guest_name, identification=guest_id, discount=days).save()
            discount = 0
    else: discount = 0
        
    guest = Guest(name=guest_name, identification=guest_id, discount=discount, phone=phone_number)
    
    guest.save()
    if advance:
        room.advance = True
        room.book_when = when
        room.book_days = days
        room.token = guest.token
    else:
        room.occupied = True
        room.occupied_when = when
        room.days = days
        room.occupancy_rate += 1
        room.token = guest.token
        
    
    
    room.save()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
    clear_session(request)
    return HttpResponse("<p> You've successfully logged out. Refer to login page</p><a href='/base/login'>here</a>")

def clear_session(request):
    request.session['username'] = None
    request.session['usertype'] = None
    request.session['token'] = None
    request.session['retreived'] = None
    request.session['guest_name'] = None
    request.session['room_number'] = None
    