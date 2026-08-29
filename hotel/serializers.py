from rest_framework import serializers
from .models import Customer, Room, Booking
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


######################################################
############# CustomerSerializer #####################
######################################################

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["user"]


######################################################
############# RoomSerializer #########################
######################################################

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


######################################################
############# BookingSerializer ######################
######################################################

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["customer", "created_at", "total_price", "status"]

    def validate(self, data):
        room = data.get("room", self.instance.room if self.instance else None)
        check_in = data.get("check_in",self.instance.check_in if self.instance else None)
        check_out = data.get("check_out",self.instance.check_out if self.instance else None)

        if check_in >= check_out:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )

        overlapping_bookings = Booking.objects.filter(
            room=room,
            status="confirmed",
            check_in__lt=check_out,
            check_out__gt=check_in)

        if self.instance:
            overlapping_bookings = overlapping_bookings.exclude(
                pk=self.instance.pk
            )

        if overlapping_bookings.exists():
            raise serializers.ValidationError(
                "This room is already booked for the selected dates."
            )

        return data

    def create(self, validated_data):
        room = validated_data["room"]
        check_in = validated_data["check_in"]
        check_out = validated_data["check_out"]

        nights = (check_out - check_in).days
        total_price = nights * room.price

        validated_data["total_price"] = total_price

        return Booking.objects.create(**validated_data)

    def update(self, instance, validated_data):
        room = validated_data.get("room", instance.room)
        check_in = validated_data.get("check_in", instance.check_in)
        check_out = validated_data.get("check_out", instance.check_out)

        nights = (check_out - check_in).days
        total_price = nights * room.price

        validated_data["total_price"] = total_price

        return super().update(instance, validated_data)
######################################################
############# RegisterSerializer #####################
######################################################

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    phone = serializers.CharField()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
        )

        customer = Customer.objects.create(
            user=user,
            email=validated_data["email"],
            phone=validated_data["phone"],
        )

        return {
            "username": user.username,
            "email": user.email,
            "phone": customer.phone,
        }

######################################################
############# LoginSerializer ########################
######################################################

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username = data["username"],
            password = data["password"]
            )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        token, created = Token.objects.get_or_create(user=user)

        return {
            "username": user.username,
            "token": token.key,
        }