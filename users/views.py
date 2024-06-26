from typing import Any
from django.db.models.query import QuerySet
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from books.models import Book


class LandingPageView(generic.TemplateView):
    template_name = 'landing.html'


class SignupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return reverse('login')


class AccountView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dashboard/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Book.objects.filter(user=self.request.user)
        context['ebook_projects'] = queryset
        return context


class UserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = User
    template_name = 'dashboard/user_confirm_delete.html'
    # Po usunięciu konta przekierowanie na stronę główną
    success_url = reverse_lazy('landing')
    context_object_name = 'user'

    def get_object(self):
        # Zwracamy aktualnie zalogowanego użytkownika
        return self.request.user
