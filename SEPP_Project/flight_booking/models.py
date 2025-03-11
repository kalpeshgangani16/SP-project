from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from SEPP_Project import settings

class AirlineUser(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"

class Flight(models.Model):
    airline = models.CharField(max_length=100)
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats = models.IntegerField(default=50)
    available_seats = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.available_seats == 0:  # Set available seats only if it's 0
            self.available_seats = self.total_seats
        super().save(*args, **kwargs)

    def get_available_seats(self):
        booked_seats = Booking.objects.filter(flight=self).values_list('seat_number', flat=True)
        return [str(seat) for seat in range(1, self.total_seats + 1) if str(seat) not in booked_seats]

    def available_seat_count(self):
        return len(self.get_available_seats())

    def __str__(self):
        return f"{self.airline} - {self.departure_city} to {self.arrival_city} ({self.available_seat_count()} seats left)"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(AirlineUser, on_delete=models.CASCADE, related_name='bookings')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    seat_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('flight', 'seat_number')

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} ({self.flight})"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    user = models.ForeignKey(AirlineUser, on_delete=models.CASCADE)
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
