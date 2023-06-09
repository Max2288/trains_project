from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tickets.models import *
from django.urls import reverse
from rest_framework.status import HTTP_200_OK as OK
from django.contrib.auth.models import User
from django.test.client import Client
from string import ascii_lowercase as letters
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from datetime import datetime
from tickets.config import SELENIUM_EXPEREMENTAL_OPTIONS, SELENIUM_OPTIONS
from selenium.webdriver.chrome.options import Options
import pytz

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
            username=default,
            password=default
        )
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


class MainLogicTests(StaticLiveServerTestCase):

    def setUp(self):
        self.name = 'Max'
        self.email = 'test@yandex.ru'
        self.password = '321Gbnmlaop9!'
        self.number = '79102884597'
        self.passport_data = '4219 874120'
        self.route = Route.objects.create(name='Тестовая поездка')
        self.timezone = pytz.timezone('Europe/Moscow')
        self.railwaycarriage = RailwayCarriage.objects.create(
            type='Купе',
            number_of_seats=20,
            seating_plan='test'
        )
        self.first_station = RailwayStation.objects.create(
            name='test1',
            description='test',
            location='Point(5 23)'
        )
        self.second_station = RailwayStation.objects.create(
            name='test2',
            description='test',
            location='Point(5 23)'
        )
        self.route_part = RoutePart.objects.create(
            start=self.first_station,
            stop_uuid=self.second_station,
            route_uuid=self.route,
            departure=datetime.now(tz=self.timezone),
            arrival=datetime.now(tz=self.timezone),
            order=1
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        for option in SELENIUM_OPTIONS:
            options.add_argument(option)
        for option in SELENIUM_EXPEREMENTAL_OPTIONS:
            options.add_experimental_option(*option)
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.maximize_window()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    @staticmethod
    def try_click(driver, by, locator):
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((by, locator))
        )
        driver.execute_script("arguments[0].click();", btn)

    def check_register(self, name, email, number, passport_data, password):
        self.selenium.get(f"{self.live_server_url}/register")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys(name)
        first_name_input = self.selenium.find_element(By.NAME, "first_name")
        first_name_input.send_keys(name)
        surname_input = self.selenium.find_element(By.NAME, "surname")
        surname_input.send_keys(name)
        patronymic_input = self.selenium.find_element(By.NAME, "patronymic")
        patronymic_input.send_keys(name)
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys(email)
        number_input = self.selenium.find_element(By.NAME, "number")
        number_input.send_keys(number)
        passport_data_input = self.selenium.find_element(
            By.NAME, "passport_data")
        passport_data_input.send_keys(passport_data)
        password1_input = self.selenium.find_element(By.NAME, "password1")
        password1_input.send_keys(password)
        password2_input = self.selenium.find_element(By.NAME, "password2")
        password2_input.send_keys(password)
        self.selenium.find_element(By.CLASS_NAME, 'btn').click()

    def check_login(self, username, password):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys(password)
        self.selenium.find_element(By.CLASS_NAME, 'btn').click()

    def test_main_logic(self):
        self.check_register(self.name,
                            self.email,
                            self.number,
                            self.passport_data,
                            self.password,
                            )
        self.check_login('231321231', '321321321')
        self.check_login(self.name, self.password)
        self.try_click(
            self.selenium,
            By.CSS_SELECTOR,
            'body > header > div.logo > a > img'
        )
        departure_city_input = self.selenium.find_element(
            By.CSS_SELECTOR,
            "#id_departure_city"
        )
        departure_city_input.send_keys(self.first_station.name)
        arrival_city_input = self.selenium.find_element(
            By.CSS_SELECTOR,
            "#id_arrival_city"
        )
        arrival_city_input.send_keys(self.second_station.name)
        departure_date_input = self.selenium.find_element(
            By.CSS_SELECTOR,
            '#id_departure_date'
        )
        departure_date_input.click()
        departure_date_input.send_keys(datetime.now(tz=self.timezone).strftime('%m%d%Y'))
        self.try_click(
            self.selenium,
            By.CSS_SELECTOR,
            "#find_routes"
        )
        self.try_click(
            self.selenium,
            By.ID,
            "choose_btn"
        )
        self.try_click(
            self.selenium,
            By.ID,
            "seat_type_kupe"
        )
        self.try_click(
            self.selenium,
            By.CSS_SELECTOR,
            "#seat-form > div.button-wrapper > button"
        )
        self.try_click(
            self.selenium,
            By.CLASS_NAME,
            "checkoption"
        )
        self.try_click(
            self.selenium,
            By.CLASS_NAME,
            "choose-btn"
        )
        self.try_click(
            self.selenium,
            By.CLASS_NAME,
            "choose-btn"
        )
        self.try_click(
            self.selenium,
            By.CLASS_NAME,
            "choose-btn"
        )
        url_to_post = f'{self.live_server_url}/trip/buy?route={self.route.id}&departure_station={self.first_station.name}&arrival_station={self.second_station.name}&seat_type={self.railwaycarriage.type}&seat=1'
        self.selenium.get(url_to_post)
        self.selenium.find_element(
            By.CLASS_NAME,
            "choose-btn"
        ).click()
        ticket = Ticket.objects.all()[0]
        ticket.status = 'Cancelled'
        ticket.save()
        self.selenium.get(f"{self.live_server_url}/finally_bought")
        self.selenium.get(f"{self.live_server_url}/profile")
        self.try_click(
            self.selenium,
            By.CLASS_NAME,
            'btn'
        )
        self.check_register(
            self.name,
            self.email,
            '321321',
            '321321',
            self.password
        )
        self.check_register(
            self.name,
            self.email,
            '321321',
            '8080808080',
            self.password
        )
