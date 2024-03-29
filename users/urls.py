from django.urls import path
from users import views as user_views
from django.contrib import admin
from django.contrib.auth import views as auth_views

app_name = "users"
urlpatterns = [
    path('signup/', user_views.signup, name= 'signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name= 'login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name= 'logout'),
]