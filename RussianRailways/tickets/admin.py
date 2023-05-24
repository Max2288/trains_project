from django.contrib import admin
from .models import AdditionalService, HumanTicket, Passenger, RailwayCarriage, RailwayStation, RoutePart, Route, Ticket


admin.site.register(AdditionalService)
admin.site.register(HumanTicket)
admin.site.register(Passenger)
admin.site.register(RailwayCarriage)
admin.site.register(RailwayStation)
admin.site.register(RoutePart)
admin.site.register(Route)
admin.site.register(Ticket)
