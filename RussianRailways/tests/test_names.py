from tickets.models import *
from tickets.serializers import *
from rest_framework.test import APITestCase


def create_viewset_tests(data_to_create, cls_model, field):
    class WrongNameTest(APITestCase):
        def setUp(self):
            self.model = cls_model.objects.create(**data_to_create)

        def test_name(self):
            self.assertEqual(str(self.model), data_to_create[field])

    return WrongNameTest


class WrongNameTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            is_superuser=True,
            username='test',
            first_name='test',
            last_name='test',
            email='test@mail.ru',
            password='test'
        )
        self.passanger = Passenger.objects.create(
            user=self.user,
            phone_number='123',
            patronymic='test',
            passport_data='test'
        )

    def test_names(self):
        self.assertEqual(str(self.passanger), "test test")


RailwayStationViewTest = create_viewset_tests(
    {
        "name": "test",
        "description": "test",
        "location": "Point(5 23)",
    },
    RailwayStation,
    "name"
)


RouteViewTest = create_viewset_tests(
    {
        "name": "test"
    },
    Route,
    "name"
)


AdditionalServiceViewTest = create_viewset_tests(
    {
        "name": "test",
        "price": 1000,
        "description": "test",
    },
    AdditionalService,
    "name"
)
RailwayCarriageViewTest = create_viewset_tests(
    {
        "type": "СВ",
        "number_of_seats": 30,
        "seating_plan": "test",
    },
    RailwayCarriage,
    "type"
)
