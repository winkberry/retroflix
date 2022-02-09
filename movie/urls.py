from django.urls import path
from . import views


urlpatterns = [
    path('main/', views.main, name='main'),
    path('view/', views.view, name='view'),
    path('detail/<int:movie_id>/', views.select_movie_detail, name='select_movie_detail'),
    path('moviedetail/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/', views.movie, name='movie'),
    path('movie/<int:genre_id>/', views.movie_genre, name='movie_genre'),
    path('stream/', views.stream, name='stream'),
    path('audio/', views.audio, name='audio'),
    path('search/',views.search, name='search'),
]