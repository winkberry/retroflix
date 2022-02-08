from django.shortcuts import render, redirect, get_object_or_404
from collections import Counter
from .models import Movie, Views
from review.models import Review, cal_age
import datetime
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from django.http import JsonResponse
from django.core import serializers
from decimal import Decimal, getcontext
from django.core.paginator import Paginator

ratings = pd.read_csv('movie/ratings.csv')
movies = pd.read_csv('movie/movie_data.csv')
movies.drop(['Unnamed: 0'], axis=1, inplace=True)

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 300)
# movieId를 기준으로 ratings 와 movies 를 결합함
movie_ratings = pd.merge(ratings, movies, on='movieid')

genre_idx = ['가족', '공포(호러)', '다큐멘터리', '드라마', '멜로/로맨스', '뮤지컬', '미스터리', '범죄', '사극', '서부극(웨스턴)', '성인물(에로)', '스릴러', '애니메이션',
             '액션', '어드벤처', '전쟁', '코미디', '판타지', 'SF', '']


def main(request):
    views_list = list(Views.objects.all().values())
    if request.method == 'GET':

        current_user = request.user.id
        # ----------- top10  --------------
        top_list = []
        for i in views_list:
            name = i['movie_id']
            top_list.append(name)
        rank = Counter(top_list).most_common(10)
        print('top10 rank: ', rank)
        top_10 = []
        for i in rank:
            top_10.append(i[0])
        top10_list = []
        for i in top_10:
            top10_list.append(Movie.objects.get(id=i))

        # ---------------- user 세대 영화  ------------
        # ------ 임의로 user의 출생년도 가지고오기
        user_birthday = datetime.date(1994, 1, 1)

        user_birthday = int(user_birthday.strftime('%Y'))  # '1994'

        if user_birthday < 1990:
            user_birthday = 1990
        elif user_birthday > 2002:
            user_birthday = 2002

        age_list = list(Movie.objects.filter(openDt=user_birthday + 5))

        # ---------- genre --------------
        top_list = []

        for i in views_list:
            name = i['genre']
            top_list.append(name)
        rank = Counter(top_list).most_common(2)
        print('genre rank:  ', rank)
        most_rank = [genre_idx[rank[0][0]], genre_idx[rank[1][0]]]
        genre1_list = list(Movie.objects.filter(genre=rank[0][0]))
        genre2_list = list(Movie.objects.filter(genre=rank[1][0]))

        # -------------------비슷한 유저로 추천 해줌----------------------

        # 유저 기반 협업 필터링
        # user별로 영화에 부여한 rating 값을 볼 수 있도록 pivot table 사용

        title_user = movie_ratings.pivot_table('rating', index='userId', columns='title')
        # 평점을 부여안한 영화는 그냥 0이라고 부여
        title_user = title_user.fillna(0)

        # 유저 1~610 번과 유저 1~610 번 간의 코사인 유사도를 구함
        user_based_collab = cosine_similarity(title_user, title_user)

        # 위는 그냥 numpy 행렬이니까, 이를 데이터프레임으로 변환
        user_based_collab = pd.DataFrame(user_based_collab, index=title_user.index, columns=title_user.index)

        # 1번 유저와 비슷한 유저를 내림차순으로 정렬한 후에, 상위 10개만 뽑음
        ############### 현재 유저와 가장 비슷한 유저를 뽑는다 ################

        # user = user_based_collab['현재 로그인한 유저의 id번호'].sort_values 하셔야 합니다
        user = user_based_collab[current_user].sort_values(ascending=False)[:10].index[1]

        #####collab = 현재유저 위에서 5 그러면 userid 번호가 들어가야함, user = 가장 비슷한유저

        result = title_user.query(f"userId == {user}").sort_values(ascending=False, by=user, axis=1)
        result_list = list(title_user.sort_values(ascending=False, by=user, axis=1))
        # 비슷한유저의 상위 영화 10가지
        movie_result_list = result_list[:10]
        movie_result_list = [Movie.objects.filter(title=movie)[0] for movie in movie_result_list]

        return render(request, 'main/main.html',
                      {'top10_list': top10_list, 'age_list': age_list, 'genre1_list': genre1_list,
                       'genre2_list': genre2_list, 'movie_result_list': movie_result_list, 'most_rank': most_rank})


def select_movie_detail(request, movie_id):
    if request.method == 'GET':
        abc = request.user.id

        #############Movie.objects.get(title = { 여기에 넘겨받은 영화 제목이 들어감 })
        movie_find = Movie.objects.get(id=movie_id)

        ###### 찾은 영화의 .opneDt ex ) .title = 끌로드부인 , .openDt = 1990, 이런 값들에  접근이 가능합니다
        print(movie_find.openDt)
        print(movie_find.title)
        print(genre_idx[movie_find.genre])
        print(movie_find.star)

        # ###### 리뷰 ######
        # reviews = list(Review.objects.filter(movie=movie_find).order_by('-created_date').values())
        # total_reviews = movie_find.reviews.all()
        # total_user_count = total_reviews.count()
        # male_user_count = total_reviews.filter(author__gender__iexact='male').count()

        # # 리뷰 성별 비율
        # if total_user_count > 0:
        #     male_gender_rate = (male_user_count / total_user_count) * 100
        #     female_gender_rate = 100 - male_gender_rate
        #     gender_rate = [male_gender_rate, female_gender_rate]

        #     # 리뷰 연령별 비율  
        #     # user_age = list(map(lambda x : cal_age(x.author.birthday), total_user))
        #     user_age = [cal_age(review.author.birthday) for review in total_reviews]
        #     gen_10 = gen_20 = gen_30 = gen_40 = 0

        #     for age in user_age:
        #         if age >= 40:
        #             gen_40 += 1
        #         elif age >= 30:
        #             gen_30 += 1
        #         elif age >= 20:
        #             gen_20 += 1
        #         else:
        #             gen_10 += 1

        #     generation_count = [gen_10, gen_20, gen_30, gen_40]
        #     generation_rate = [(gen_cnt / total_user_count) * 100 for gen_cnt in generation_count]

        #### 영화와 비슷한 영화 추천 정보 #####

        # user_title = movie_ratings.pivot_table('rating', index='title', columns='userId')
        # user_title = user_title.fillna(0)
        # item_based_collab = cosine_similarity(user_title, user_title)
        # item_based_collab = pd.DataFrame(item_based_collab, index=user_title.index, columns=user_title.index)

        # # 현재영화와 비슷하게 유저들로부터 평점을 부여받은 영화들은?
        # # recommend_movies = item_based_collba[넘겨받은 영화의 제목 넣는 부분].sort_values(ascending=False)[1:11].index
        # recommend_movies = item_based_collab[movie_find.title].sort_values(ascending=False)[1:11].index

        # # 추천 영화를 리스트로 변경 해주는 부분
        # recommend_list = [i for i in recommend_movies]

        # print(recommend_list)
        movie = serializers.serialize('json', [movie_find])
        data = {'movie': movie,
                'genre': genre_idx[movie_find.genre],
                # 'recommend_list': recommend_list,
                # 'reviews': reviews,
                # 'gender_rate': gender_rate,
                # 'generation_rate' : generation_rate 
                }
        return JsonResponse(data, safe=False)


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    total_reviews = movie.reviews.all()
    total_user_count = total_reviews.count()
    male_user_count = total_reviews.filter(author__gender__iexact='male').count()
    ###영화 조회수####
    views_list = list(Views.objects.all().values())
    views_cnt = 0
    for i in views_list:
        if i['movie_id'] == movie_id:
            views_cnt += 1

    #### 영화와 비슷한 영화 추천 정보 #####

    user_title = movie_ratings.pivot_table('rating', index='title', columns='userId')
    user_title = user_title.fillna(0)
    item_based_collab = cosine_similarity(user_title, user_title)
    item_based_collab = pd.DataFrame(item_based_collab, index=user_title.index, columns=user_title.index)

    # 현재영화와 비슷하게 유저들로부터 평점을 부여받은 영화들은?
    # recommend_movies = item_based_collba[넘겨받은 영화의 제목 넣는 부분].sort_values(ascending=False)[1:11].index
    recommend_movies = item_based_collab[movie.title].sort_values(ascending=False)[1:11].index

    # 추천 영화를 리스트로 변경 해주는 부분
    recommend_list = [Movie.objects.filter(title=movie)[0] for movie in recommend_movies]
    print(recommend_list)

    # 소수점 자리 표현

    # 리뷰 성별 비율
    if total_user_count > 0:
        male_gender_rate = (male_user_count / total_user_count) * 100
        female_gender_rate = 100 - male_gender_rate
        gender_rate = [round(male_gender_rate), round(female_gender_rate)]

        # 리뷰 연령별 비율  
        # user_age = list(map(lambda x : cal_age(x.author.birthday), total_user))
        user_age = [cal_age(review.author.birthday) for review in total_reviews]
        gen_10 = gen_20 = gen_30 = gen_40 = 0

        for age in user_age:
            if age >= 40:
                gen_40 += 1
            elif age >= 30:
                gen_30 += 1
            elif age >= 20:
                gen_20 += 1
            else:
                gen_10 += 1

        generation_count = [gen_10, gen_20, gen_30, gen_40]
        generation_rate = [round((gen_cnt / total_user_count) * 100, 1) for gen_cnt in generation_count]

        # 평점표시
        star_rate = (movie.star * 100) / 5
        print(star_rate)
        print(generation_rate)
        print(gender_rate)

        context = {
            'movie': movie,
            'genre': genre_idx[movie.genre],
            'gender_rate': gender_rate,
            'generation_rate': generation_rate,
            'recommend_list': recommend_list,
            'star_rate': star_rate,
            'views_cnt': views_cnt,
        }

    else:
        context = {
            'movie': movie,
            'recommend_list': recommend_list,
            'genre': genre_idx[movie.genre],
            'recommend_list': recommend_list,
            'views_cnt': views_cnt,
        }
    return render(request, 'main/movie_detail.html', context)


def view(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        movie_id = request.POST.get('movie_id')
        genre = request.POST.get('genre')
        views = Views.objects.create(user_id=user_id, movie_id=movie_id, genre=genre)
        views.save()
        return JsonResponse({'msg': 'views 저장!'})


def movie(request):
    views_list = list(Views.objects.all().values())
    if request.method == 'GET':
        top_list = []
        for i in views_list:
            name = i['movie_id']
            top_list.append(name)
        rank = Counter(top_list).most_common()
        top_10 = []
        for i in rank:
            top_10.append(i[0])
        movie_list = []
        for i in top_10:
            movie_list.append(Movie.objects.get(id=i))
        return render(request, 'main/movie.html', {'movie_list': movie_list, 'name':'인기'})


def movie_genre(request, genre_id):
    movie_list = list(Movie.objects.filter(genre=genre_id))
    name = genre_idx[genre_id]
    return render(request, 'main/movie.html', {'movie_list': movie_list, 'name':name})


def search(request):
    page_num = request.GET.get('page')

    kw = request.GET.get('keyword', '')
    qs = Movie.objects.filter()
    filter_args = {}
    if kw in genre_idx:
        filter_args['genre'] = genre_idx.index(kw)
    else:
        filter_args['title__startswith'] = kw
    movies = qs.filter(**filter_args)
    paginater = Paginator(movies, 12)
    movies = paginater.get_page(page_num)
    return render(request, 'main/search.html', {'genres': genre_idx, 'movies': movies, 'kw': kw})
