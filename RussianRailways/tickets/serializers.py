from rest_framework import serializers
from .models import RoutePart, RailwayStation, AdditionalService, RailwayCarriage, RailwayStation, Ticket, HumanTicket, Passenger, Route
from django.contrib.auth.models import User
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ['id', 'name']


class RailwayStationSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = RailwayStation
        geo_field = 'location'
        fields = ['id', 'name', 'description']


class RoutPartSerializer(serializers.ModelSerializer):
    start = RailwayStationSerializer()
    stop_uuid = RailwayStationSerializer()
    route_uuid = RouteSerializer()

    def create(self, validated_data):
        start = RailwayStation.objects.create(
            name=validated_data['start']['name'],
            description=validated_data['start']['description'],
            location=validated_data['start']['location'],
        )
        stop_uuid = RailwayStation.objects.create(
            name=validated_data['stop_uuid']['name'],
            description=validated_data['stop_uuid']['description'],
            location=validated_data['stop_uuid']['location'],
        )
        route_uuid = Route.objects.create(
            name=validated_data['route_uuid']['name']
        )
        return RoutePart.objects.create(
            start=start,
            stop_uuid=stop_uuid,
            route_uuid=route_uuid,
            departure=validated_data['departure'],
            arrival=validated_data['arrival'],
            order=validated_data['order']
        )

    class Meta:
        model = RoutePart
        fields = ['id', 'start', 'stop_uuid',
                  'route_uuid', 'departure', 'arrival', 'order']


class AdditionalServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdditionalService
        fields = ['id', 'name', 'price', 'description']


class RailwayCarriageSerializer(serializers.ModelSerializer):

    class Meta:
        model = RailwayCarriage
        fields = ['id', 'type', 'number_of_seats', 'seating_plan']


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ['id', 'route_part', 'railway_carriage_info_uuid',
                  'seat_number', 'status', 'human_ticket']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name', 'email', 'password', 'is_superuser']


class PassengerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def create(self, validated_data):
        is_superuser = validated_data.get('user', {}).get('is_superuser', False)
        user = User.objects.create(
            username=validated_data['user']['username'],
            first_name=validated_data['user']['first_name'],
            last_name=validated_data['user']['last_name'],
            email=validated_data['user']['email'],
            password=validated_data['user']['password'],
            is_superuser=is_superuser
        )
        return Passenger.objects.create(
            user=user,
            phone_number=validated_data['phone_number'],
            patronymic=validated_data['patronymic'],
            passport_data=validated_data['passport_data']
        )

    class Meta:
        model = Passenger
        fields = ['id', 'user', 'phone_number', 'patronymic', 'passport_data']



class HumanTicketSerializer(serializers.ModelSerializer):
    passenger_info=PassengerSerializer()

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['passenger_info']['user']['username'],
            first_name=validated_data['passenger_info']['user']['first_name'],
            last_name=validated_data['passenger_info']['user']['last_name'],
            email=validated_data['passenger_info']['user']['email'],
            password=validated_data['passenger_info']['user']['password'],
        )
        passanger = Passenger.objects.create(
            user=user,
            phone_number=validated_data['passenger_info']['phone_number'],
            patronymic=validated_data['passenger_info']['patronymic'],
            passport_data=validated_data['passenger_info']['passport_data']
        )
        return HumanTicket.objects.create(
                price = validated_data['price'],
                passenger_info=passanger,
                booking_date=validated_data['booking_date']
        )
        

    class Meta:
        model = HumanTicket
        fields = ['id', 'price', 'booking_date', 'passenger_info']
