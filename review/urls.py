from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
   path('detail/<int:movie_id>/reviews/create/', views.review_create, name='review_create'),
   # path('detail/<int:movie_id>/', views.review_list, name='review_list')
]
