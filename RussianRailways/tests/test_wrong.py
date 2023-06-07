from tickets.models import *
from tickets.serializers import *
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class WrongPriceTest(APITestCase):

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
        self.data = {
            "name": "test",
            "price": 1000,
            "description": "test",
        }
        self.wrong_data = {
            "name": "test",
            "price": -10,
            "description": "test",
        }
        self.model = AdditionalService.objects.create(**self.data)

    def test_create_model(self):
        """Test for creating module."""
        self.client.post('/rest/AdditionalService/', data=self.wrong_data)
        serializer = AdditionalServiceSerializer(data=self.wrong_data)
        self.assertFalse(serializer.is_valid())


class WrongRailwayCarriageTest(APITestCase):

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
        self.data = {
            "type": "СВ",
            "number_of_seats": 30,
            "seating_plan": "test",
        }
        self.wrong_data = {
            "type": "СВ",
            "number_of_seats": 50000,
            "seating_plan": "test",
        }
        self.model = RailwayCarriage.objects.create(**self.data)

    def test_create_model(self):
        """Test for creating module."""
        self.client.post('/rest/AdditionalService/', data=self.wrong_data)
        serializer = RailwayCarriageSerializer(data=self.wrong_data)
        self.assertFalse(serializer.is_valid())

