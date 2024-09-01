from django.contrib.auth import views as auth_views


class LoginUserView(auth_views.LoginView):
    template_name = "pages/login.html"
    next_page = "/"
    redirect_authenticated_user = True
