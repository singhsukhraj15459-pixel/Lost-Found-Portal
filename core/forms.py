from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, label="Full Name")
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=20, required=True, label="Mobile Number")

    class Meta:
        model = User
        fields = ['full_name', 'email', 'mobile_number', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.mobile_number = self.cleaned_data['mobile_number']

        # Split full name into first/last for Django's built-in fields
        name_parts = self.cleaned_data['full_name'].strip().split(' ', 1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''

        # username must be unique; base it on email to avoid a separate field
        user.username = self.cleaned_data['email']

        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput)
from .models import LostItem, FoundItem


class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['title', 'category', 'description', 'date_lost', 'area', 'postcode', 'image']
        widgets = {
            'date_lost': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class FoundItemForm(forms.ModelForm):
    class Meta:
        model = FoundItem
        fields = ['title', 'category', 'description', 'date_found', 'area', 'postcode', 'image']
        widgets = {
            'date_found': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }