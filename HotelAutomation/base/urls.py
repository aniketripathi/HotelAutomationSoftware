from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('base/login', views.login, name='login'),
    path('base/receptionist', views.receptionist, name='receptionist'),
    path('base/admin', views.admin, name='admin'),
    path('base/catering_service_manager', views.catering_service_manager, name='catering_service_manager'),
    path('base/book_room', views.book_room, name='book_room'),
    path('base/checkout', views.checkout, name='checkout'),
    path('base/check_discount', views.check_discount, name='check_discount'),
    path('base/generate_bill', views.generate_bill, name='generate_bill'),
    path('base/logout', views.logout, name='logout'),
    path('', RedirectView.as_view(url='base/login', permanent=True)),
    
    
]
