from django.urls import path
from api.views import *


urlpatterns = [  
  path('getWeatherInfo/', getWeatherInfo, name='getWeatherInfo'),
  path('getLocationByIP/', getLocationByIP, name='getLocationByIP'),
  path('register/', register, name='register'),
  path('logout/', logout, name='logout'),
]