from django.urls import path
from . import views
from django.conf.urls import include

urlpatterns = [
    path('', views.home, name="home_page"),
    path('registration/', views.Registration, name="registration_page"),
    path('login/', views.Login, name='login_page'),
    path('signout/', views.SignOut, name='sign_out_page'),
    path('dashboard/', views.Dashboard, name='dashboard_page'),
    path('watchlist/', views.Watchlist, name='watchlist_page')

]
