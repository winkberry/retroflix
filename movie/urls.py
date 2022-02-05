from django.urls import path
from . import views


urlpatterns = [
    path('main/', views.main, name='main'),
    path('detail/', views.select_movie_detail, name='select_movie_detail'),
]