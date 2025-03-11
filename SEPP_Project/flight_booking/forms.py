from django import forms
from .models import AirlineUser, Booking
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = AirlineUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth']

class FlightSearchForm(forms.Form):
    departure_city = forms.CharField()
    arrival_city = forms.CharField()
    travel_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    price_range = forms.ChoiceField(choices=[
        ('0-500', 'Under $500'),
        ('501-1000', '$501-$1000'),
        ('1001+', 'Over $1000')
    ], required=False)

class BookingForm(forms.ModelForm):
    seat_number = forms.ChoiceField(choices=[], label="Select Seat")

    def __init__(self, *args, flight=None, **kwargs):
        super().__init__(*args, **kwargs)
        if flight:
            available_seats = flight.get_available_seats()
            self.fields['seat_number'].choices = [(seat, seat) for seat in available_seats]

    class Meta:
        model = Booking
        fields = ['seat_number']
class SignUpForm(UserCreationForm):
    class Meta:
        model = AirlineUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']