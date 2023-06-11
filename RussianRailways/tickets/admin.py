from django.contrib import admin

from tickets import models

admin.site.register(models.AdditionalService)
admin.site.register(models.HumanTicket)
admin.site.register(models.Passenger)
admin.site.register(models.RailwayCarriage)
admin.site.register(models.RailwayStation)
admin.site.register(models.RoutePart)
admin.site.register(models.Route)
admin.site.register(models.Ticket)
