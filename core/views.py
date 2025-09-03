from django.views.generic import FormView
from django.contrib.auth import login
from .forms import RegistrationForm

# View для реєстрації
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = '/'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)