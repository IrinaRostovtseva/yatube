from django.views.generic import CreateView
from django.core.mail import send_mail

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = '/auth/login/'
    template_name = 'signup.html'

    def send_mail_after_registartion(self, email):
        send_mail("Регистрации на Yatube",
                  "Вы зарегистрировались в социальной сети Yatube.",
                  "admin@yatube.ru", [email], fail_silently=False)

    def form_valid(self, form):
        form.save(commit=False)
        email = form.cleaned_data["email"]
        self.send_mail_after_registartion(email)
        form.save()
        return super().form_valid(form)
