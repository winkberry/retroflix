from django.shortcuts import render, redirect
from collections import Counter
from .models import Movie
import datetime

import pandas as pd
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, accuracy, Reader
from surprise.model_selection import train_test_split

# 임의로 views 조회수 만들기
views_list = [{'user_id': 1, 'movie_id': 1, 'genre': 1},
              {'user_id': 1, 'movie_id': 2, 'genre': 2},
              {'user_id': 1, 'movie_id': 3, 'genre': 3},
              {'user_id': 1, 'movie_id': 4, 'genre': 1},
              {'user_id': 1, 'movie_id': 5, 'genre': 6},
              {'user_id': 1, 'movie_id': 6, 'genre': 4},
              {'user_id': 1, 'movie_id': 7, 'genre': 7},
              {'user_id': 1, 'movie_id': 8, 'genre': 4},
              {'user_id': 1, 'movie_id': 9, 'genre': 2},
              {'user_id': 1, 'movie_id': 10, 'genre': 5},
              {'user_id': 1, 'movie_id': 11, 'genre': 3},
              {'user_id': 1, 'movie_id': 12, 'genre': 2},
              {'user_id': 1, 'movie_id': 13, 'genre': 7},
              {'user_id': 1, 'movie_id': 14, 'genre': 9},
              {'user_id': 1, 'movie_id': 15, 'genre': 5},
              {'user_id': 1, 'movie_id': 16, 'genre': 3},
              {'user_id': 1, 'movie_id': 17, 'genre': 2},
              {'user_id': 1, 'movie_id': 18, 'genre': 4},
              {'user_id': 1, 'movie_id': 19, 'genre': 1},
              {'user_id': 1, 'movie_id': 20, 'genre': 3},
              {'user_id': 1, 'movie_id': 16, 'genre': 3},
              {'user_id': 1, 'movie_id': 17, 'genre': 2},
              {'user_id': 1, 'movie_id': 18, 'genre': 4},
              {'user_id': 1, 'movie_id': 19, 'genre': 1},
              {'user_id': 1, 'movie_id': 20, 'genre': 3},
              {'user_id': 1, 'movie_id': 5, 'genre': 6},
              {'user_id': 1, 'movie_id': 6, 'genre': 4},
              {'user_id': 1, 'movie_id': 7, 'genre': 7},
              {'user_id': 1, 'movie_id': 8, 'genre': 4},
              {'user_id': 1, 'movie_id': 9, 'genre': 2},
              {'user_id': 1, 'movie_id': 4, 'genre': 1},
              {'user_id': 1, 'movie_id': 5, 'genre': 6},
              {'user_id': 1, 'movie_id': 6, 'genre': 4},
              {'user_id': 1, 'movie_id': 7, 'genre': 7},
              {'user_id': 1, 'movie_id': 8, 'genre': 4},
              {'user_id': 1, 'movie_id': 9, 'genre': 2},
              {'user_id': 1, 'movie_id': 8, 'genre': 4},
              {'user_id': 1, 'movie_id': 9, 'genre': 2},
              {'user_id': 1, 'movie_id': 10, 'genre': 5},
              {'user_id': 1, 'movie_id': 11, 'genre': 3},
              {'user_id': 1, 'movie_id': 12, 'genre': 2},
              {'user_id': 1, 'movie_id': 13, 'genre': 7},
              ]


def main(request):
    if request.method == 'GET':
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
        age_list = []

        if user_birthday < 1990:
            user_birthday = 1990
        elif user_birthday > 2002:
            user_birthday = 2002
        movie = Movie.objects.filter(openDt=user_birthday + 5)
        for n in range(len(movie)):
            age_list.append(movie[n])

        # ---------- genre --------------
        top_list = []
        genre1_list = []
        genre2_list = []
        for i in views_list:
            name = i['genre']
            top_list.append(name)
        rank = Counter(top_list).most_common(2)
        print('genre rank:  ', rank)

        movie_1 = Movie.objects.filter(genre=rank[0][0])
        for i in range(len(movie_1)):
            genre1_list.append(movie_1[i])

        movie_2 = Movie.objects.filter(genre=rank[1][0])
        for i in range(len(movie_2)):
            genre2_list.append(movie_2[i])

        return render(request, 'movie/main.html',
                      {'top10_list': top10_list, 'age_list': age_list, 'genre1_list': genre1_list,
                       'genre2_list': genre2_list})


def test(request):
    ratings = pd.read_csv('movie/ratings.csv')
    movies = pd.read_csv('movie/movie_data.csv')
    movies.drop(['Unnamed: 0'], axis=1, inplace=True)

    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 300)
    # movieId를 기준으로 ratings 와 movies 를 결합함
    movie_ratings = pd.merge(ratings, movies, on='movieid')

    ############################비슷한 유저로 추천 해줌#############################################
    ###############################################################################################

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
    user = user_based_collab[5].sort_values(ascending=False)[:10].index[1]
    #####collab = 현재유저 위에서 5 그러면 userid 번호가 들어가야함, user = 가장 비슷한유저

    result = title_user.query(f"userId == {user}").sort_values(ascending=False, by=user, axis=1)

    result_list = list(title_user.sort_values(ascending=False, by=user, axis=1))
    # 비슷한유저의 상위 영화 10가지
    movie_result_list = result_list[:10]

    print(user)
    print(movie_result_list)

    return render(request, 'movie/main.html', {'test': movie_result_list})



