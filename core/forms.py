from django import forms
from django.contrib.auth.models import User, Group

# Форма для реєстрації
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            group = Group.objects.get_or_create(name='users')[0]
            user.groups.add(group)
        return user