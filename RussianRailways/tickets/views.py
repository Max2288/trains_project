from datetime import datetime, timedelta

import requests
from django.contrib.auth import authenticate, decorators, login, logout
from django.contrib.auth.models import User
from django.db import connection
from django.db import models as d_models
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from rest_framework import permissions, viewsets
from tickets.config import *
from tickets.forms import RegistrationForm, TicketSearchForm, TrainSeatForm
from tickets.models import *
from tickets.serializers import *


@csrf_protect
def index(request):
    find = TicketSearchForm()
    return render(request, 'tickets/index.html', {'form': find})


@csrf_protect
def trip(request):
    form = TrainSeatForm()
    return render(request, 'tickets/trip.html', {'form': form})


def seats(request):
    route = Route.objects.get(id=request.GET.get('route')).id
    start_station = RoutePart.objects.get(
        start=RailwayStation.objects.get(
            name=request.GET.get('departure_station'),
        ).id,
    )
    stop_station = RoutePart.objects.get(
        stop_uuid=RailwayStation.objects.get(
            name=request.GET.get('arrival_station'),
        ).id,
    )
    ordered_tickets = []
    carrige = RailwayCarriage.objects.get(type=request.GET.get('seat_type'))
    for orders in range(start_station.order, stop_station.order + 1):
        route_part = RoutePart.objects.get(order=orders, route_uuid=route)
        tickets_list = Ticket.objects.filter(
            route_part=route_part.id,
            railway_carriage_info_uuid=carrige.id,
        )
        ordered_tickets += [ticket.seat_number for ticket in tickets_list]
    free_seats = [
        seat for seat in range(1, carrige.number_of_seats + 1)
        if seat not in ordered_tickets
    ]

    return render(
        request,
        'tickets/seats.html',
        {
            "image": SEATING_IMAGES[carrige.type],
            "seats": free_seats,
        },
    )


def passenger_info(request):
    passanger_dictionary = {}
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        passenger = Passenger.objects.get(user=user)
        passanger_dictionary = {'passenger': passenger}
    return render(request, 'tickets/passenger_info.html', passanger_dictionary)


def buy_ticket(request):
    user_dictionary = {
        "departure_station": request.GET['departure_station'],
        "arrival_station": request.GET['arrival_station'],
        "seat_type": request.GET['seat_type'],
        "seat": request.GET['seat'],
    }
    return render(request, 'tickets/buy_ticket.html', user_dictionary)


def finally_purchase(request):
    if request.method == 'POST':
        departure_station = RoutePart.objects.get(
            start=RailwayStation.objects.get(
                name=request.GET.get('departure_station'),
            ).id,
        )
        arrival_station = RoutePart.objects.get(
            stop_uuid=RailwayStation.objects.get(
                name=request.GET.get('arrival_station'),
            ).id,
        )
        route = Route.objects.get(id=request.GET.get('route')).id
        carrige = RailwayCarriage.objects.get(
            type=request.GET.get('seat_type'),
        )
        seat = request.GET.get('seat')
        user = User.objects.get(id=request.user.id)
        if Ticket.objects.filter(
            route_part=departure_station,
            railway_carriage_info_uuid=carrige,
            seat_number=int(seat),
        ).exists():
            return redirect('wrong')
        if departure_station and arrival_station and route and carrige and seat:
            passenger = Passenger.objects.get(user=user)
            human_ticket = HumanTicket.objects.create(
                price=RAILWAY_CARRIDGE_PRICES[carrige.type],
                passenger_info_id=passenger.id,
                booking_date=datetime.now(),
            )
            for orders in range(departure_station.order, arrival_station.order + 1):
                route_part = RoutePart.objects.get(
                    order=orders,
                    route_uuid=route,
                )
                Ticket.objects.create(
                    route_part=route_part,
                    railway_carriage_info_uuid=carrige,
                    seat_number=int(seat),
                    status='Booked',
                    human_ticket=human_ticket,
                )
                human_ticket.price += 200
                human_ticket.save()
        response = requests.post(
            url=BOOST_URL,
            headers=BOOST_HEADERS,
            json={
                'recipient': BOOST_ACCOUNT,
                'amount': human_ticket.price,
                'pay_date': f'{timezone.now() + timedelta(minutes=2)}',
                'callback':
                    {
                        'redirect': STATIC_THANKS,
                        'url': BOOST_CALLBACK_URL.format(id=human_ticket.id),
                        'headers': BOOST_CALLBACK_HEADERS,
                    },
            },
        )
        return redirect(BOOST_REDIRECT.format(id=response.json().get('id')))
    return render(request, 'tickets/wrong.html')


def wrong(request):
    return render(request, 'tickets/wrong.html')


def succesessful(request):
    return render(request, 'tickets/succesessful.html')


def tickets(request):
    departure_city = request.GET.get('departure_city')
    arrival_city = request.GET.get('arrival_city')
    departure_date = request.GET.get('departure_date')
    cursor = connection.cursor()
    cursor.execute(
        QUERY_FOR_TRAINS,
        (
            departure_city,
            departure_date,
            arrival_city,
            departure_city,
            arrival_city,
        ),
    )
    columns = [col[0] for col in cursor.description]
    tickets_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return render(request, 'tickets/tickets.html', {'tickets': tickets_list})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            surname = form.cleaned_data.get('surname')
            patronymic = form.cleaned_data.get('patronymic')
            email = form.cleaned_data.get('email')
            number = form.cleaned_data.get('number')
            passport_data = form.cleaned_data.get('passport_data')
            password = form.cleaned_data.get('password1')
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=surname,
                email=email,
                password=password,
            )
            Passenger.objects.create(
                user=user,
                phone_number=number,
                patronymic=patronymic,
                passport_data=passport_data,
            )
            return redirect('login')
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'tickets/register.html', context)


def login_view(request):
    error_msg = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            error_msg = 'Invalid username or password'
    else:
        error_msg = None
    return render(request, 'tickets/login.html', {'error_msg': error_msg})


@decorators.login_required(login_url='login')
def profile(request):
    passenger = Passenger.objects.get(user=request.user)
    return render(
        request,
        'tickets/profile.html',
        {
            'passenger': passenger,
            'tickets': HumanTicket.objects.filter(passenger_info=passenger),
        },
    )


def logout_view(request):
    logout(request)
    return redirect('home')


def contacts(request):
    return render(request, 'tickets/contacts.html')


def query_from_request(request, cls_serializer=None) -> dict:
    if cls_serializer:
        query = {}
        for attr in cls_serializer.Meta.fields:
            request.GET.get(attr, '')
        return query


def create_viewset(cls_model: d_models.Model, serializer, permission, order_field):
    class_name = f"{cls_model.__name__}ViewSet"
    doc = f"API endpoint that allows users to be viewed or edited for {cls_model.__name__}"
    return type(
        class_name,
        (viewsets.ModelViewSet,),
        {
            "__doc__": doc,
            "serializer_class": serializer,
            "queryset": cls_model.objects.all().order_by(order_field),
            "permission classes": [permission],
            "get_queryset": lambda self, *args, **kwargs: cls_model.objects.filter(
                **query_from_request(self.request, serializer),
            ).order_by(order_field),
        },
    )


RoutePartViewSet = create_viewset(
    RoutePart,
    RoutPartSerializer,
    permissions.BasePermission,
    'id',
)

AdditionalServiceViewSet = create_viewset(
    AdditionalService,
    AdditionalServiceSerializer,
    permissions.BasePermission,
    'name',
)

RailwayCarriageViewSet = create_viewset(
    RailwayCarriage,
    RailwayCarriageSerializer,
    permissions.BasePermission,
    'type',
)

RailwayStationViewSet = create_viewset(
    RailwayStation,
    RailwayStationSerializer,
    permissions.BasePermission,
    'name',
)

TicketViewSet = create_viewset(
    Ticket,
    TicketSerializer,
    permissions.BasePermission,
    'id',
)

HumanTicketViewSet = create_viewset(
    HumanTicket,
    HumanTicketSerializer,
    permissions.BasePermission,
    'id',
)

PassengerViewSet = create_viewset(
    Passenger,
    PassengerSerializer,
    permissions.BasePermission,
    'id',
)

UserViewSet = create_viewset(
    User,
    UserSerializer,
    permissions.BasePermission,
    'id',
)
