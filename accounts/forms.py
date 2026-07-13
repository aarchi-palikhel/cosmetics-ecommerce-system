from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                'w-full px-4 py-2 border border-gray-300 rounded-lg '
                'focus:outline-none focus:ring-2 focus:ring-purple-500'
            )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username or Email'
        self.fields['username'].widget.attrs['placeholder'] = 'Enter username or email'
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                'w-full px-4 py-2 border border-gray-300 rounded-lg '
                'focus:outline-none focus:ring-2 focus:ring-purple-500'
            )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_class = (
            'w-full px-4 py-2 border border-gray-300 rounded-lg '
            'focus:outline-none focus:ring-2 focus:ring-purple-500'
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', input_class)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This email is already in use.')
        return email
