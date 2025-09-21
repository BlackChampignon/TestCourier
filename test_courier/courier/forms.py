from django import forms
from .models import User


class RegistrationForm(forms.ModelForm):
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat password'}),
        label='Confirm password'
    )

    class Meta:
        model = User
        fields = ['name', 'password', 'user_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Your password'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Name',
            'password': 'Password',
            'user_type': 'User type',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords dont match!')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
        label='Name'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label='Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        password = cleaned_data.get('password')

        if name and password:
            try:
                user = User.objects.get(name=name)
                if user.password != password:
                    raise forms.ValidationError('Incorrect password!')
                cleaned_data['user'] = user
            except User.DoesNotExist:
                raise forms.ValidationError('User name does not exist')

        return cleaned_data