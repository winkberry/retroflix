from django.urls import path
from . import views


urlpatterns = [
    path('main/', views.main, name='main'),
    path('view/', views.view, name='view'),
    path('detail/<int:movie_id>/', views.select_movie_detail, name='select_movie_detail'),
    path('moviedetail/<int:movie_id>/', views.movie_detail, name='movie_detail'),
]