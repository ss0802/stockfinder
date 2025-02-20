from .views import register, user_login, user_logout
from django.contrib.auth import views as auth_views
from django.urls import path


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

