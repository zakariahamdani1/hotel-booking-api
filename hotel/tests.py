from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from .models import Customer, Room


# *********************************************
# ************* Register **********************
# *********************************************

class RegisterAPITest(APITestCase):

    def test_register_customer(self):

        response = self.client.post(
            "/register/",
            {
                "username": "testuser",
                "password": "TestPassword123!",
                "email": "test@example.com",
                "phone": "0550000000",
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data["username"], "testuser")

        self.assertEqual(response.data["email"], "test@example.com")

        self.assertEqual(response.data["phone"], "0550000000")


# *********************************************
# ************* Login *************************
# *********************************************

class LoginAPITest(APITestCase):

    def setUp(self):

        self.client.post(
            "/register/",
            {
                "username": "testuser",
                "password": "TestPassword123!",
                "email": "test@example.com",
                "phone": "0550000000",
            },
            format="json"
        )

    def test_login(self):

        response = self.client.post(
            "/login/",
            {
                "username": "testuser",
                "password": "TestPassword123!",
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["username"], "testuser")

        self.assertIn("token", response.data)


# *********************************************
# ************* Authentication ****************
# *********************************************

class AuthenticationAPITest(APITestCase):

    def setUp(self):

        self.client.post(
            "/register/",
            {
                "username": "authuser",
                "password": "TestPassword123!",
                "email": "auth@example.com",
                "phone": "0551111111",
            },
            format="json"
        )

    def test_authenticated_user_can_access_customers(self):

        login_response = self.client.post(
            "/login/",
            {
                "username": "authuser",
                "password": "TestPassword123!",
            },
            format="json"
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.get("/customers/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_access_customers(self):

        response = self.client.get("/customers/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# *********************************************
# ************* Rooms *************************
# *********************************************

class RoomAPITest(APITestCase):

    def test_anyone_can_list_rooms(self):

        response = self.client.get("/rooms/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_create_room(self):

        self.client.post(
            "/register/",
            {
                "username": "customer1",
                "password": "TestPassword123!",
                "email": "customer1@example.com",
                "phone": "0552222222",
            },
            format="json"
        )

        login_response = self.client.post(
            "/login/",
            {
                "username": "customer1",
                "password": "TestPassword123!",
            },
            format="json"
        )

        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.post(
            "/rooms/",
            {
                "room_number": "301",
                "room_type": "single",
                "price": "5000.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_room(self):

        manager = User.objects.create_user(
            username="manager",
            password="ManagerPassword123!",
            is_staff=True
        )

        self.client.force_authenticate(
            user=manager
        )

        response = self.client.post(
            "/rooms/",
            {
                "room_number": "302",
                "room_type": "double",
                "price": "7000.00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# *********************************************
# ************* Bookings **********************
# *********************************************

class BookingAPITest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="customer",
            password="TestPassword123!"
        )

        self.customer = Customer.objects.create(
            user=self.user,
            email="customer@example.com",
            phone="0553333333"
        )

        self.room = Room.objects.create(
            room_number="401",
            room_type="single",
            price="5000.00"
        )

        self.client.force_authenticate(
            user=self.user
        )

    def create_booking(self, check_in, check_out):

        return self.client.post(
            "/bookings/",
            {
                "room": self.room.id,
                "check_in": check_in,
                "check_out": check_out
            },
            format="json"
        )

    def test_create_booking_calculates_total_price(self):

        response = self.create_booking(
            "2026-09-01",
            "2026-09-06"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data["total_price"], "25000.00")

        self.assertEqual(response.data["status"], "confirmed")

    def test_cannot_book_room_with_overlapping_dates(self):

        first_response = self.create_booking(
            "2026-09-01",
            "2026-09-06"
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED
        )

        second_response = self.create_booking(
            "2026-09-03",
            "2026-09-05"
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "This room is already booked for the selected dates.",
            str(second_response.data)
        )

    def test_can_book_room_when_dates_do_not_overlap(self):

        first_response = self.create_booking(
            "2026-09-01",
            "2026-09-06"
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED
        )

        second_response = self.create_booking(
            "2026-09-06",
            "2026-09-10"
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED
        )

    def test_customer_cannot_see_another_customer_booking(self):

        booking_response = self.create_booking(
            "2026-10-01",
            "2026-10-05"
        )

        self.assertEqual(
            booking_response.status_code,
            status.HTTP_201_CREATED
        )

        booking_id = booking_response.data["id"]

        other_user = User.objects.create_user(
            username="othercustomer",
            password="OtherPassword123!"
        )

        Customer.objects.create(
            user=other_user,
            email="other@example.com",
            phone="0554444444"
        )

        self.client.force_authenticate(
            user=other_user
        )

        response = self.client.get(
            f"/bookings/{booking_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_customer_can_cancel_booking(self):

        booking_response = self.create_booking(
            "2026-11-01",
            "2026-11-05"
        )

        self.assertEqual(
            booking_response.status_code,
            status.HTTP_201_CREATED
        )

        booking_id = booking_response.data["id"]

        response = self.client.post(
            f"/bookings/{booking_id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["status"],
            "cancelled"
        )

    def test_cancelled_booking_allows_room_to_be_booked_again(self):

        first_response = self.create_booking(
            "2026-12-01",
            "2026-12-05"
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED
        )

        booking_id = first_response.data["id"]

        cancel_response = self.client.post(
            f"/bookings/{booking_id}/cancel/"
        )

        self.assertEqual(
            cancel_response.status_code,
            status.HTTP_200_OK
        )

        second_response = self.create_booking(
            "2026-12-01",
            "2026-12-05"
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED
        )

    def test_manager_can_complete_booking_after_checkout(self):

        booking_response = self.create_booking(
            "2026-01-01",
            "2026-01-05"
        )

        self.assertEqual(
            booking_response.status_code,
            status.HTTP_201_CREATED
        )

        booking_id = booking_response.data["id"]

        manager = User.objects.create_user(
            username="manager",
            password="ManagerPassword123!",
            is_staff=True
        )

        self.client.force_authenticate(
            user=manager
        )

        response = self.client.post(
            f"/bookings/{booking_id}/complete/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["status"],
            "completed"
        )

    def test_manager_cannot_complete_booking_before_checkout(self):

        booking_response = self.create_booking(
            "2028-01-01",
            "2028-01-05"
        )

        self.assertEqual(
            booking_response.status_code,
            status.HTTP_201_CREATED
        )

        booking_id = booking_response.data["id"]

        manager = User.objects.create_user(
            username="manager2",
            password="ManagerPassword123!",
            is_staff=True
        )

        self.client.force_authenticate(
            user=manager
        )

        response = self.client.post(
            f"/bookings/{booking_id}/complete/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data["detail"],
            "Booking cannot be completed before check-out date."
        )

    def test_customer_cannot_complete_booking(self):

        booking_response = self.create_booking(
            "2026-01-01",
            "2026-01-05"
        )

        self.assertEqual(
            booking_response.status_code,
            status.HTTP_201_CREATED
        )

        booking_id = booking_response.data["id"]

        response = self.client.post(
            f"/bookings/{booking_id}/complete/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            response.data["detail"],
            "Only managers can complete bookings."
        )
