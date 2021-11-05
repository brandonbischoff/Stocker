from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import TheStocks
from django.contrib.auth.models import User


class ChooseSource(forms.Form):

    source_choices = TheStocks.objects.values_list(
        'source', 'source').distinct()

    date_choices = TheStocks.objects.values_list(
        'purchase_date', 'purchase_date').distinct().order_by(
        'purchase_date__month', 'purchase_date__day')

    source = forms.ChoiceField(label='',
                               choices=source_choices,
                               widget=forms.Select(attrs={'class': 'btn btn-outline-secondary dropdown-toggle'}))

    date = forms.ChoiceField(label='',
                             choices=date_choices,
                             widget=forms.Select(attrs={'class': 'btn btn-outline-secondary dropdown-toggle'}))


class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email Adress'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Re-enter Password'


class LoginForm(forms.Form):

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'}))
