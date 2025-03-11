from django.urls import path
from . import views
from .views import TicketDetailView, payment_view, ticket_view

app_name = 'flight_booking'

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_update, name='profile'),
    path('search/', views.flight_search, name='search'),
    path('signup/', views.signup_view, name='signup'),
    path('booking/<int:flight_id>/', views.create_booking, name='create_booking'),
    path('booking/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='ticket_details'),  
    path('ticket/view/<int:booking_id>/', ticket_view, name='ticket_view'),
    path('payment/<int:booking_id>/', views.payment_view, name='payment'),
    path('payment/success/<int:booking_id>/', views.payment_success, name='payment_success'),
    
]