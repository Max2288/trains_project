from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from tickets.models import validate_phone_number, validate_passport_data
from django.utils import timezone


class TicketSearchForm(forms.Form):
    departure_city = forms.CharField(
        label='Откуда',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Откуда'})
    )
    arrival_city = forms.CharField(
        label='Куда',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Куда'})
    )
    departure_date = forms.DateField(
        label='Туда',
        required=True,
        widget=forms.DateInput(attrs={'placeholder': 'Туда', 'onfocus': "(this.type='date')", 'onblur': "(this.type='text')", 'min': timezone.now().strftime('%Y-%m-%d')})
    )
    arrival_date = forms.DateField(
        label='Обратно',
        required=False,
        widget=forms.DateInput(attrs={'placeholder': 'Обратно', 'onfocus': "(this.type='date')", 'onblur': "(this.type='text')", 'min': timezone.now().strftime('%Y-%m-%d')})
    )


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    surname = forms.CharField(max_length=30, required=True)
    patronymic = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    number = forms.CharField(max_length=20, required=True, validators=[validate_phone_number])
    passport_data = forms.CharField(max_length=12, required=True, validators=[validate_passport_data])

    class Meta:
        model = User
        fields = ('username', 'first_name', 'surname', 'patronymic', 'email', 'number', 'passport_data', 'password1', 'password2')


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )


class TrainSeatForm(forms.Form):
    seat_type_kupe = forms.BooleanField(label='Купе', required=False, widget=forms.RadioSelect)
    seat_type_platzkart = forms.BooleanField(label='Плацкарт', required=False, widget=forms.RadioSelect)
    seat_type_sv = forms.BooleanField(label='СВ', required=False, widget=forms.RadioSelect)
