from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from movie.models import Movie
from django.db.models import Count, Avg
from django.contrib.auth.decorators import login_required
# from .forms import ReviewForm
from review.models import Review, cal_age

# Create your views here.



# Form이 제 역할을 못하면 쓸 기능입니다.
@login_required
def review_create(request, movie_id):
    
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        content = request.POST.get('review-content')
        star = request.POST.get('review-star')
        Review.objects.create(movie=movie, author=request.user, content=content, star=star).save()
        movie.star = round(movie.reviews.all().aggregate(Avg('star')).get('star__avg'), 2)
        movie.save()
        return redirect('movie_detail', movie_id = movie.id)
        
@login_required
def review_delete(request, review_id):
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        review = get_object_or_404(Review, id = review_id)
        movie = get_object_or_404(Movie, id = review.movie.id)
        review.delete()
        if movie.reviews.all().count() > 0:
            movie.star = round(movie.reviews.all().aggregate(Avg('star')).get('star__avg'), 2)
        else:
            movie.star = 0
        movie.save()
        return JsonResponse({'msg':'done'})

