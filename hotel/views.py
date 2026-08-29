from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .permissions import IsManagerOrReadOnly
from datetime import datetime
from django.utils import timezone

from .models import Customer, Room, Booking
from .serializers import (
    CustomerSerializer,
    RoomSerializer,
    BookingSerializer,
    RegisterSerializer,
    LoginSerializer
)

# *********************************************
# ************* Customer **********************
# *********************************************

class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()

        return Customer.objects.filter(
            user=self.request.user
        )

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()

        return Customer.objects.filter(
            user=self.request.user
        )


# *********************************************
# ************* Rooms *************************
# *********************************************

class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsManagerOrReadOnly]

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsManagerOrReadOnly]

class AvailableRoomsView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        check_in = self.request.query_params.get("check_in")
        check_out = self.request.query_params.get("check_out")

        try:
            check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return Room.objects.none()

        if check_in >= check_out:
            return Room.objects.none()

        booked_rooms = Booking.objects.filter(
            status="confirmed",
            check_in__lt=check_out,
            check_out__gt=check_in
            ).values_list("room_id", flat=True)

        return Room.objects.exclude(id__in=booked_rooms)

# *********************************************
# ************* Booking ***********************
# *********************************************

class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()

        return Booking.objects.filter(
            customer__user=self.request.user
        )

    def perform_create(self, serializer):
        customer = self.request.user.customer
        serializer.save(customer=customer)

class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()

        return Booking.objects.filter(
            customer__user=self.request.user
        )

class BookingCancelView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()

        return Booking.objects.filter(
            customer__user=self.request.user
        )

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = "cancelled"
        booking.save(update_fields=["status"])

        serializer = self.get_serializer(booking)

        return Response(serializer.data)

class BookingCompleteView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()

        return Booking.objects.filter(
            customer__user=self.request.user
        )

    def post(self, request, *args, **kwargs):

        if not request.user.is_staff:
            return Response(
                {"detail": "Only managers can complete bookings."},
                status=403
            )
        booking = self.get_object()

        if booking.check_out > timezone.now().date():
            return Response(
                {"detail": "Booking cannot be completed before check-out date."},
                status=400
            )

        booking.status = "completed"
        booking.save(update_fields=["status"])

        serializer = self.get_serializer(booking)

        return Response(serializer.data)

# *********************************************
# ************* Register **********************
# *********************************************

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# *********************************************
# ************* Login *************************
# *********************************************

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)

