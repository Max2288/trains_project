from django.test import TestCase
from tickets.models import *
from django.urls import reverse
from rest_framework.status import HTTP_200_OK as OK
from django.contrib.auth.models import User
from django.test.client import Client
from string import ascii_lowercase as letters


def create_view_tests(url, page_name, template):
    class ViewTests(TestCase):

        def setUp(self):
            self.client = Client()
            default = letters[:10]
            self.user = User.objects.create_user(
                username=default,
                password=default
            )
            self.client.login(username=default, password=default)

        def test_view_exists_at_url(self):
            self.assertEqual(self.client.get(url).status_code, OK)

        def test_view_exists_by_name(self):
            self.assertEqual(self.client.get(
                reverse(page_name)).status_code, OK)

        def test_view_uses_template(self):
            resp = self.client.get(reverse(page_name))
            self.assertEqual(resp.status_code, OK)
            self.assertTemplateUsed(resp, template)
            self.assertTemplateUsed(resp, 'tickets/base.html')

    return ViewTests


ContactsViewTests = create_view_tests(
    '/contacts',
    'contacts',
    'tickets/contacts.html'
)

HomeViewTests = create_view_tests(
    '/',
    'home',
    'tickets/index.html'
)

WrongViewTests = create_view_tests(
    '/wrong',
    'wrong',
    'tickets/wrong.html'
)

SuccesessfulViewTests = create_view_tests(
    '/succesessful',
    'succesessful',
    'tickets/succesessful.html'
)


class ProfileTests(TestCase):

    def setUp(self):
        self.client = Client()
        default = letters[:10]
        self.user = User.objects.create_user(
            username=default, password=default)
        self.client.login(username=default, password=default)
        self.model = Passenger.objects.create(
            user=self.user,
            phone_number='123',
            patronymic='test',
            passport_data='test'
        )
        self.url = '/profile'
        self.page_name = 'profile'
        self.template = 'tickets/profile.html'

    def test_view_exists_at_url(self):
        self.assertEqual(self.client.get(self.url).status_code, OK)

    def test_view_exists_by_name(self):
        self.assertEqual(self.client.get(
            reverse(self.page_name)).status_code, OK)

    def test_view_uses_template(self):
        resp = self.client.get(reverse(self.page_name))
        self.assertEqual(resp.status_code, OK)
        self.assertTemplateUsed(resp, self.template)
        self.assertTemplateUsed(resp, 'tickets/base.html')
