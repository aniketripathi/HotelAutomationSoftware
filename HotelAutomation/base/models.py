from django.db import models
from django.core.validators import MinLengthValidator
# Create your models here.


# Stores the login information of the users
class User(models.Model):
    class UserType(models.IntegerChoices):
        ADMINISTRATOR = 0, 'Administrator'
        RECEPTIONIST = 1, 'Receptionist'
        CATERING_SERVICE_MANAGER = 2, 'Catering Service Manager'
    
    class Meta:
        db_table = 'users'
        
    username = models.CharField(max_length=16, primary_key=True)
    password = models.CharField(max_length=16)
    usertype = models.IntegerField(default=UserType.RECEPTIONIST, choices=UserType.choices)


# Stores information about guest who booked the rooms
class Guest(models.Model):
    
    class Meta:
        db_table = 'guests'
    @property
    def token(self):
        return self.id
    name = models.CharField(max_length=32)
    identification = models.CharField(max_length=16,null=True)
    discount = models.IntegerField(default=0)
    phone = models.CharField(max_length=10,validators=[MinLengthValidator(10)],null=True)

# Stores information about room

class Room(models.Model):
    
    class Bed(models.TextChoices):
        SINGLE = 'single'
        DOUBLE = 'double'    
    
    class Meta:
        db_table = 'rooms'
    
    # basic
    room_number = models.IntegerField(primary_key=True)
    bed = models.CharField(max_length=6, default=Bed.SINGLE, choices=Bed.choices)
    ac = models.BooleanField(default=False)
    token = models.IntegerField(default=-1)
    # Occupied
    occupied = models.BooleanField(default=False)
    occupied_when = models.DateTimeField(default=None, null=True)
    days = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    # advance booking
    advance = models.BooleanField(default=False)
    book_when = models.DateTimeField(default=None, null=True)
    book_days = models.IntegerField(default=0)
    advance_price = models.DecimalField(max_digits=16, decimal_places=2)
    occupancy_rate = models.DecimalField(default=0, max_digits=16, decimal_places=2)
    


# Stores information about guest who volunteer for discount
class Discount(models.Model):
    
    class Meta:
        db_table = 'discount'
        
    name = models.CharField(max_length=32)
    identification = models.CharField(max_length=16, null=True)
    discount = models.IntegerField(default=0)
    phone = models.CharField(max_length=10, primary_key=True, validators=[MinLengthValidator(10)])


class Catering(models.Model):
    
    class Meta:
        db_table = 'catering'
    
    token = models.IntegerField(default=-1)
    food_item = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=16, decimal_places=2)
  