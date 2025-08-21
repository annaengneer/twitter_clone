from django import forms
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form__input'}))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form__input'}))
    phone_number = forms.CharField(label="電話番号", required=False, widget=forms.TextInput(attrs={'class': 'form__input'}))
    birth_date = forms.DateField(label="生年月日", required=False, widget=forms.DateInput(attrs={'class': 'form__input', 'type': 'date'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form__input'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form__input'}))

    class Meta:
        model = User
        fields = ("email", "username", "phone_number", "birth_date", "password1", "password2")
    
    def signup(self, request, user):
        user.phone_number = self.cleaned_data.get("phone_number")
        user.birth_date = self.cleaned_data.get("birth_date")
        user.email = self.cleaned_data.get("email", user.email)
        user.save()
        return user
