from django.urls import path

from .views import (
    RegisterView,
    CustomerListView,
    CustomerDetailView,
    RoomListCreateView,
    RoomDetailView,
    BookingListCreateView,
    BookingDetailView,
    BookingCancelView,
    BookingCompleteView,
    LoginView,
    AvailableRoomsView
)


urlpatterns = [
    path("customers/", CustomerListView.as_view()),
    path("customers/<int:pk>/", CustomerDetailView.as_view()),

    path("rooms/", RoomListCreateView.as_view()),
    path("rooms/available/", AvailableRoomsView.as_view()),
    path("rooms/<int:pk>/", RoomDetailView.as_view()),

    path("bookings/", BookingListCreateView.as_view()),
    path("bookings/<int:pk>/cancel/", BookingCancelView.as_view()),
    path("bookings/<int:pk>/complete/", BookingCompleteView.as_view()),
    path("bookings/<int:pk>/", BookingDetailView.as_view()),

    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
]