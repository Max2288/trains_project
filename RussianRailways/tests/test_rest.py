"""Tests for CRUD."""

from tickets.models import *
from tickets.serializers import *
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
from datetime import datetime


def create_viewset_tests(
    url: str,
    cls_model: models.Model,
    cls_serializer: serializers.ModelSerializer,
    request_content: dict,
    to_change: dict,
):
    class ViewSetTests(APITestCase):

        def setUp(self):
            self.user = User.objects.create_user(
                is_superuser=True,
                id=1,
                username='test',
                first_name='test',
                last_name='test',
                email='test@mail.ru',
                password='test'
            )
            token = Token.objects.create(user=self.user)
            self.client = APIClient()
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
            self.model = cls_model.objects.create(**request_content)

        def test_create_model(self):
            """Test for creating module."""
            response = self.client.post(url, data=request_content)
            serializer = cls_serializer(data=request_content)
            self.assertTrue(serializer.is_valid())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        def test_get_model(self):
            """Test for getting module."""
            url_to_get = f'{url}{self.model.id}/'
            response = self.client.get(url_to_get)
            serializer = cls_serializer(data=request_content)
            self.assertTrue(serializer.is_valid())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_update_model(self):
            """Test for updating module."""
            url_to_update = f'{url}{self.model.id}/'
            response = self.client.put(
                url_to_update,
                data=json.dumps(to_change),
                content_type='application/json'
            )
            serializer = cls_serializer(data=to_change)
            self.assertTrue(serializer.is_valid())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_delete_model(self):
            """Test for deliting module."""
            url_to_delete = f'{url}{self.model.id}/'
            response = self.client.delete(url_to_delete)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertFalse(
                cls_model.objects.filter(id=self.model.id).exists()
            )

    return ViewSetTests


AdditionalServiceTests = create_viewset_tests(
    '/rest/AdditionalService/',
    AdditionalService,
    AdditionalServiceSerializer,
    {
        "name": "test",
        "price": 1000,
        "description": "test",
    },
    {
        "name": "test1",
        "price": 10,
        "description": "test1",
    },
)

RailwayStationTests = create_viewset_tests(
    '/rest/RailwayStation/',
    RailwayStation,
    RailwayStationSerializer,
    {
        "name": "test",
        "description": "test",
        "location": "Point(5 23)",
    },
    {
        "name": "test2",
        "description": "test2",
        "location": "Point(5 25)",
    },
)

RailwayCarriageTests = create_viewset_tests(
    '/rest/RailwayCarriage/',
    RailwayCarriage,
    RailwayCarriageSerializer,
    {
        "type": "СВ",
        "number_of_seats": 30,
        "seating_plan": "test",
    },
    {
        "type": "Плацкарт",
        "number_of_seats": 39,
        "seating_plan": "test3"
    }
)


class RoutePartTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            is_superuser=True,
            id=1,
            username='test',
            first_name='test',
            last_name='test',
            email='test@mail.ru',
            password='test'
        )
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.request_data = {
            "start": {
                "name": "test",
                "description": "test",
                "location": "Point(5 23)",
            },
            "stop_uuid": {
                "name": "test",
                "description": "test",
                "location": "Point(5 23)",
            },
            "route_uuid": {
                "name": "test",
            },
            "departure": str(datetime.now()),
            "arrival": str(datetime.now()),
            "order": 1
        }
        self.model = RoutePart.objects.create(
            start=RailwayStation.objects.create(
                name="test",
                description="test",
                location="Point(5 23)",
            ),
            stop_uuid=RailwayStation.objects.create(
                name="test",
                description="test",
                location="Point(5 23)",
            ),
            route_uuid=Route.objects.create(name="test"),
            departure=datetime.now(),
            arrival=datetime.now(),
            order=1,
        )
        self.to_change = {
            "departure": str(datetime.now()),
            "arrival": str(datetime.now()),
            "order": 2
        }

    def test_create_model(self):
        """Test for creating module."""
        response = self.client.post(
            '/rest/RoutePart/',
            data=json.dumps(self.request_data),
            content_type='application/json'
        )
        serializer = RoutPartSerializer(data=self.request_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_model(self):
        """Test for getting module."""
        url_to_get = f'/rest/RoutePart/{self.model.id}/'
        response = self.client.get(url_to_get)
        serializer = RoutPartSerializer(data=self.request_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_model(self):
        """Test for updating module."""
        url_to_update = f'/rest/RoutePart/{self.model.id}/'
        response = self.client.patch(
            url_to_update,
            data=json.dumps(
                self.to_change,
            ),
            content_type='application/json'
        )
        serializer = RoutPartSerializer(data=self.to_change, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_model(self):
        """Test for deliting module."""
        url_to_delete = f'/rest/RoutePart/{self.model.id}/'
        response = self.client.delete(url_to_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            RoutePart.objects.filter(id=self.model.id).exists()
        )


class PassangerTest(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            is_superuser=True,
            username='test',
            first_name='test',
            last_name='test',
            email='test@mail.ru',
            password='test'
        )
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.request_data = {
            "user": {
                "username": "MAX2288",
                "first_name": "test1",
                "last_name": "test1",
                "email": "test321211@mail.com",
                "password": "Test1"
            },
            "phone_number": "79103559596",
            "patronymic": "test",
            "passport_data": "4219 531762"
        }
        self.model = Passenger.objects.create(
            user=self.user,
            phone_number='123',
            patronymic='test',
            passport_data='test'
        )
        self.to_change = {
            "phone_number": "79103559569",
            "patronymic": "test1111",
            "passport_data": "4219 531731"
        }

    def test_create_model(self):
        """Test for creating module."""
        serializer = PassengerSerializer(data=self.request_data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        response = self.client.post(
            '/rest/Passenger/',
            data=json.dumps(self.request_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_model(self):
        """Test for getting module."""
        url_to_get = f'/rest/Passenger/{self.model.id}/'
        response = self.client.get(url_to_get)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_model(self):
        """Test for updating module."""
        url_to_update = f'/rest/Passenger/{self.model.id}/'
        response = self.client.patch(
            url_to_update,
            data=json.dumps(
                self.to_change,
            ),
            content_type='application/json'
        )
        serializer = RoutPartSerializer(data=self.to_change, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_model(self):
        """Test for deliting module."""
        url_to_delete = f'/rest/Passenger/{self.model.id}/'
        response = self.client.delete(url_to_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            RoutePart.objects.filter(id=self.model.id).exists()
        )


class HumanTicketTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            is_superuser=True,
            id=1000,
            username='test',
            first_name='test',
            last_name='test',
            email='test@mail.ru',
            password='test'
        )
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.passanger = Passenger.objects.create(
            user=self.user,
            phone_number='123',
            patronymic='test',
            passport_data='test'
        )
        self.request_data = {
            "price": 10000,
            "passenger_info": {"user": {
                "username": "MAX2288",
                "first_name": "test1",
                "last_name": "test1",
                "email": "test321211@mail.com",
                "password": "Test1"
            },
                "phone_number": "79103559596",
                "patronymic": "test",
                "passport_data": "4219 531762",
            },
            "booking_date": str(datetime.now())
        }
        self.model = HumanTicket.objects.create(
            price=10000,
            passenger_info=self.passanger,
            booking_date=datetime.now()
        )
        self.to_change = {
            "price": 10,
        }

    def test_create_model(self):
        """Test for creating module."""
        serializer = HumanTicketSerializer(data=self.request_data)
        self.assertTrue(serializer.is_valid())
        response = self.client.post(
            '/rest/HumanTicket/',
            data=json.dumps(self.request_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_model(self):
        """Test for getting module."""
        url_to_get = f'/rest/HumanTicket/{self.model.id}/'
        response = self.client.get(url_to_get)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_model(self):
        """Test for updating module."""
        url_to_update = f'/rest/HumanTicket/{self.model.id}/'
        response = self.client.patch(
            url_to_update,
            data=json.dumps(
                self.to_change,
            ),
            content_type='application/json'
        )
        serializer = HumanTicketSerializer(data=self.to_change, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_model(self):
        """Test for deliting module."""
        url_to_delete = f'/rest/HumanTicket/{self.model.id}/'
        response = self.client.delete(url_to_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            HumanTicket.objects.filter(id=self.model.id).exists()
        )