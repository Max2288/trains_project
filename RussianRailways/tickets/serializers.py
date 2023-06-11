from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from tickets import models


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Route
        fields = ['id', 'name']


class RailwayStationSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = models.RailwayStation
        geo_field = 'location'
        fields = ['id', 'name', 'description']


class RoutPartSerializer(serializers.ModelSerializer):
    start = RailwayStationSerializer()
    stop_uuid = RailwayStationSerializer()
    route_uuid = RouteSerializer()

    def create(self, validated_data):
        start = models.RailwayStation.objects.create(
            name=validated_data['start']['name'],
            description=validated_data['start']['description'],
            location=validated_data['start']['location'],
        )
        stop_uuid = models.RailwayStation.objects.create(
            name=validated_data['stop_uuid']['name'],
            description=validated_data['stop_uuid']['description'],
            location=validated_data['stop_uuid']['location'],
        )
        route_uuid = models.Route.objects.create(
            name=validated_data['route_uuid']['name'],
        )
        return models.RoutePart.objects.create(
            start=start,
            stop_uuid=stop_uuid,
            route_uuid=route_uuid,
            departure=validated_data['departure'],
            arrival=validated_data['arrival'],
            order=validated_data['order'],
        )

    class Meta:
        model = models.RoutePart
        fields = [
            'id',
            'start',
            'stop_uuid',
            'route_uuid',
            'departure',
            'arrival',
            'order',
        ]


class AdditionalServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AdditionalService
        fields = ['id', 'name', 'price', 'description']


class RailwayCarriageSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RailwayCarriage
        fields = ['id', 'type', 'number_of_seats', 'seating_plan']


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ticket
        fields = [
            'id',
            'route_part',
            'railway_carriage_info_uuid',
            'seat_number',
            'status',
            'human_ticket',
        ]


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'is_superuser',
        ]


class PassengerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def create(self, validated_data):
        is_superuser = validated_data.get(
            'user',
            {},
        ).get('is_superuser', False)
        user_params = validated_data['user']
        user = User.objects.create(
            username=user_params['username'],
            first_name=user_params['first_name'],
            last_name=user_params['last_name'],
            email=user_params['email'],
            password=user_params['password'],
            is_superuser=is_superuser,
        )
        return models.Passenger.objects.create(
            user=user,
            phone_number=validated_data['phone_number'],
            patronymic=validated_data['patronymic'],
            passport_data=validated_data['passport_data'],
        )

    class Meta:
        model = models.Passenger
        fields = ['id', 'user', 'phone_number', 'patronymic', 'passport_data']


class HumanTicketSerializer(serializers.ModelSerializer):
    passenger_info = PassengerSerializer()

    def create(self, validated_data):
        user_params = validated_data['passenger_info']['user']
        user = User.objects.create(
            username=user_params['username'],
            first_name=user_params['first_name'],
            last_name=user_params['last_name'],
            email=user_params['email'],
            password=user_params['password'],
        )
        passanger = models.Passenger.objects.create(
            user=user,
            phone_number=validated_data['passenger_info']['phone_number'],
            patronymic=validated_data['passenger_info']['patronymic'],
            passport_data=validated_data['passenger_info']['passport_data'],
        )
        return models.HumanTicket.objects.create(
            price=validated_data['price'],
            passenger_info=passanger,
            booking_date=validated_data['booking_date'],
        )

    class Meta:
        model = models.HumanTicket
        fields = ['id', 'price', 'booking_date', 'passenger_info']
