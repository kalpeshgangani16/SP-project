from datetime import timedelta

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from .forms import LoginForm, ProfileUpdateForm, FlightSearchForm, BookingForm, SignUpForm, PaymentForm
from .models import Booking, Flight, Payment


# def index(request):
#     return render(request, 'index.html')
def index(request):
    flights = None  # No flights shown for logged-out users
    if request.user.is_authenticated:
        flights = Flight.objects.all().order_by('departure_time')

    return render(request, 'index.html', {'flights': flights})



def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user and not user.account_locked:
                login(request, user)
                user.failed_login_attempts = 0
                user.save()
                return redirect('flight_booking:home')
            else:
                if user:
                    user.failed_login_attempts += 1
                    if user.failed_login_attempts >= 3:
                        user.account_locked = True
                        user.locked_until = timezone.now() + timedelta(minutes=30)
                    user.save()
    return render(request, 'login.html', {'form': form})


@login_required
def profile_update(request):
    form = ProfileUpdateForm(instance=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('flight_booking:home')
    return render(request, 'profile.html', {'form': form})


def flight_search(request):
    form = FlightSearchForm()
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            flights = Flight.objects.filter(
                departure_city=form.cleaned_data['departure_city'],
                arrival_city=form.cleaned_data['arrival_city'],
                departure_time__date=form.cleaned_data['travel_date']
            )
            return render(request, 'flight_list.html', {'flights': flights})
    return render(request, 'search.html', {'form': form})


@login_required
def create_booking(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    available_seats = flight.get_available_seats()
    
    if request.method == 'POST':
        form = BookingForm(request.POST,flight=flight)
        if form.is_valid():
            seat_number = form.cleaned_data['seat_number']
            if seat_number not in available_seats:
                messages.error(request, f"Seat {seat_number} is already booked. Please choose another.")
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.flight = flight
                booking.save()
                flight.available_seats-=1
                flight.save()
                messages.success(request, f"Booking successful! Seat {seat_number} reserved.")
                return redirect('flight_booking:payment', booking_id=booking.id)
    else:
        form = BookingForm(flight=flight)
    
    return render(request, 'booking_form.html', {'form': form, 'flight': flight, 'available_seats': available_seats})

#logout view
def logout_view(request):
    logout(request)
    return redirect('flight_booking:home')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('flight_booking:home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def booking_confirmation(request):
    return render(request, 'booking_confirmation.html')


@login_required
def ticket_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'ticket_details.html', {'booking': booking})


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'ticket_details.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.user = request.user
            payment.amount = booking.flight.price
            payment.payment_status = 'completed'
            payment.save()
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()
            return redirect('flight_booking:payment_success', booking_id=booking.id)
    else:
        form = PaymentForm()
    
    return render(request, 'payment.html', {'form': form, 'booking': booking})


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'payment_success.html', {'booking': booking})
