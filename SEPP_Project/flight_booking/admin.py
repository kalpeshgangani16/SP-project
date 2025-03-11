from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AirlineUser, Flight, Booking

@admin.register(AirlineUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'account_locked')
    list_filter = ('account_locked', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'address', 'date_of_birth',
                                      'failed_login_attempts', 'account_locked', 'locked_until')}),  
    )

@admin.register(Flight)  # ✅ Avoids duplicate registration issues
class FlightAdmin(admin.ModelAdmin):
    list_display = ('airline', 'departure_city', 'arrival_city', 'departure_time', 'arrival_time', 'price', 'available_seat_count')  
    list_filter = ('airline', 'departure_city', 'arrival_city')
    search_fields = ('airline', 'departure_city', 'arrival_city')
    ordering = ('departure_time',)
    date_hierarchy = 'departure_time'

    def available_seat_count(self, obj):
        """Dynamically displays the available seats in the admin panel."""
        return obj.available_seat_count()
    available_seat_count.short_description = "Available Seats"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'flight', 'booking_date', 'seat_number', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'booking_date')
    search_fields = ('user__username', 'flight__airline', 'seat_number')
    date_hierarchy = 'booking_date'
    raw_id_fields = ('user', 'flight')
