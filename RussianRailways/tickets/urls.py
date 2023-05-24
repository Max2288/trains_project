from django.urls import path, include
from . import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'RoutePart', views.RoutePartViewSet)
router.register(r'AdditionalService', views.AdditionalServiceViewSet)
router.register(r'RailwayCarriage', views.RailwayCarriageViewSet)
router.register(r'RailwayStation', views.RailwayStationViewSet)
router.register(r'Ticket', views.TicketViewSet)
router.register(r'HumanTicket', views.HumanTicketViewSet)
router.register(r'Passenger', views.PassengerViewSet)
router.register(r'User', views.UserViewSet)


urlpatterns = [
    path('', views.index, name='home'),
    path('trip/class', views.trip, name='trip'),
    path('tickets', views.tickets, name='tickets'),
    path('register', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('profile', views.profile, name='profile'),
    path('logout/',  views.logout_view, name='logout'),
    path('contacts', views.contacts, name='contacts'),
    path('trip/seats', views.seats, name='seats'),
    path('trip/boarding', views.passenger_info, name='ps_inf'),
    path('trip/buy', views.buy_ticket, name='buy_ticket'),
    path('finally_bought', views.finally_purchase, name='finally_purchase'),
    path('succsessfull', views.succsessfull, name='succsessfull'),
    path('wrong', views.wrong, name='wrong'),
    path('rest/', include(router.urls)),
] 
