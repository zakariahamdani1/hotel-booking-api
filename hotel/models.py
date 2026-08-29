from django.db import models
from django.contrib.auth.models import User


######################################################
############# Customer ###############################
######################################################

class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer"
    )
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.user.username


######################################################
############# Room ###################################
######################################################

class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite','Suite')
        ]
    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Room {self.room_number}"


######################################################
############# Bookings ###############################
######################################################

class Booking(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="bookings"
    )
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    
    check_in = models.DateField()
    check_out = models.DateField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - Room {self.room.room_number}"

