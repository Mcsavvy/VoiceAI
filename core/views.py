from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"


class LoginUserView(auth_views.LoginView):
    template_name = "pages/login.html"
    next_page = "/"
    redirect_authenticated_user = True
