from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from tickets.config import RAILWAY_CARRIDGE_CHOICES
from django.core.validators import MinValueValidator
from django.utils import timezone


def validate_number(number):
    if number <= 0:
        raise ValidationError(
            gettext_lazy("Number is lower or equal than 0!"),
            params={"number": number}
        )


def validate_phone_number(number):
    cleaned_value = ''.join(filter(str.isdigit, number))
    if len(cleaned_value) != 11 or not cleaned_value.startswith(('7', '8')):
        raise ValidationError(
            gettext_lazy('Invalid phone number!'),
            params={"number": number}
        )


def validate_passport_data(passport_data):
    cleaned_value = ''.join(filter(str.isdigit, passport_data))
    if len(cleaned_value) != 10:
        raise ValidationError(
            gettext_lazy('Invalid passport data!'),
            params={"passport_data": passport_data}
        )
    region_codes = [
        '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
        '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
        '31', '32', '33', '34', '35', '36', '37', '38', '39', '40',
        '41', '42', '43', '44', '45', '46', '47', '48', '49', '50',
        '51', '52', '53', '54', '55', '56', '57', '58', '59', '60',
        '61', '62', '63', '64', '65', '66', '67', '68', '69', '70',
        '71', '72', '73', '74', '75', '76', '77', '78', '79', '83',
        '86', '87', '89', '92', '94', '95', '96', '97', '98', '99'
    ]
    if cleaned_value[:2] not in region_codes:
        raise ValidationError(
            gettext_lazy('Invalid passport data!'),
            params={"passport_data": passport_data}
        )


def validate_seat_number(seat_number):
    
    if not 0 <= seat_number < 40:
        raise ValidationError(
            gettext_lazy("Seat_number should be between 1 to 39"),
            params={"seat_number": seat_number}
        )


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class NameMixin(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True


class PriceMixin(models.Model):
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_number],
    )

    class Meta:
        abstract = True


class DescriptionMixin(models.Model):
    description = models.CharField(
        blank=True, null=True, max_length=200, db_column="description")

    class Meta:
        abstract = True


class AdditionalService(UUIDMixin, PriceMixin, NameMixin, DescriptionMixin):

    class Meta:
        db_table = 'additional_service'

    def __str__(self) -> str:
        return self.name


class HumanTicket(UUIDMixin, PriceMixin):
    passenger_info = models.ForeignKey(
        'Passenger',
        models.DO_NOTHING,
        db_column='passenger_info_uuid'
    )
    booking_date = models.DateTimeField(
        blank=True,
        null=True,
        validators=[MinValueValidator(timezone.now())], help_text='date and time must be grater than now'
    )
    

    class Meta:
        db_table = 'human_ticket'


class Passenger(UUIDMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.TextField(null=True, validators=[validate_phone_number])
    patronymic = models.CharField(null=False, max_length=20)
    passport_data = models.TextField(
        null=False,
        validators=[validate_passport_data]
    )

    class Meta:
        db_table = 'passenger'

    def __str__(self) -> str:
        return f"{self.user.username} {self.user.last_name}"


class RailwayCarriage(UUIDMixin):
    type = models.CharField(choices=RAILWAY_CARRIDGE_CHOICES, max_length=8)
    number_of_seats = models.IntegerField(
        validators=[validate_seat_number])
    seating_plan = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'railway_carriage'

    def __str__(self) -> str:
        return self.type


class RailwayStation(UUIDMixin, NameMixin, DescriptionMixin):
    location = PointField(blank=True, null=True)

    class Meta:
        db_table = 'railway_station'

    def __str__(self) -> str:
        return self.name


class Route(UUIDMixin, NameMixin):

    class Meta:
        db_table = 'route'

    def __str__(self) -> str:
        return self.name


class RoutePart(UUIDMixin):
    start = models.ForeignKey(
        RailwayStation,
        on_delete=models.CASCADE,
        related_name='start_route_parts'
    )
    stop_uuid = models.ForeignKey(
        RailwayStation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stop_route_parts'
    )
    route_uuid = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure = models.DateTimeField(validators=[MinValueValidator(timezone.now())], help_text='date and time must be grater than now')
    arrival = models.DateTimeField(validators=[MinValueValidator(timezone.now())], help_text='date and time must be grater than now')
    order = models.IntegerField(validators=[validate_number])

    class Meta:
        db_table = 'route_part'


ticket_statues = (
    ('Booked', 'Booked'),
    ('Confirmed', 'Confirmed'),
    ('Cancelled', 'Cancelled')
)


class Ticket(UUIDMixin):
    route_part = models.ForeignKey(RoutePart, models.DO_NOTHING)
    railway_carriage_info_uuid = models.ForeignKey(
        RailwayCarriage,
        models.DO_NOTHING,
        db_column='railway_carriage_info_uuid'
    )
    seat_number = models.IntegerField(validators=[validate_seat_number])
    status = models.CharField(choices=ticket_statues, default='Booked', blank=True, null=False, max_length=10)
    human_ticket = models.ForeignKey(
        HumanTicket,
        on_delete=models.CASCADE,
        db_column='human_ticket_info'
    )

    class Meta:
        db_table = 'ticket'


class TicketToAddService(UUIDMixin):
    add = models.ForeignKey(
        AdditionalService,
        models.DO_NOTHING
    )
    ticket = models.ForeignKey(Ticket, models.DO_NOTHING)

    class Meta:
        db_table = 'ticket_to_add_service'
