import json
import random
import string
from random import randint
from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect, reverse
from .models import  CustomUser
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from . import models
from django.core.mail import send_mail

# Create your views here.
def base(request):
    user = request.user.is_authenticated
    # True, False반환
    if not user:
        return render(request, 'landing.html')
        # return redirect('/sign-in')
    return redirect('/main')

@login_required
def main(request):
    print('ho')
    return render(request, 'main/main.html' )

certify = False
def sign_up_view(request):
    print('인증번호')
    global certify
    if request.method == 'GET':
        is_user = request.user.is_authenticated
        if is_user:
            return redirect('/')

        return render(request, 'user/signup.html')

    elif request.method == 'POST':
        global certify_num
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']
        nickname = data['nickname']
        email = data['email']
        birthday = data['birthday']
        gender = data['gender']
        err_msg = ''

        if username == '' or password1 == '':
            err_msg = '아이디 및 패스워드를 확인해주세요'
        if nickname == '':
            err_msg = '닉네임을 적어주세요.'
        if email == '':
            err_msg = '이메일을 적어주세요.'
        if birthday == '':
            err_msg = '생년월일을 적어주세요.'
        if gender == '1':
            err_msg = '성별을 적어주세요.'
        if password1 != password2:
            err_msg = '비밀번호가 일치하지 않습니다.'
        if not certify:
            err_msg = '이메일을 인증해주세요.'
        is_it = get_user_model().objects.filter(username=username)
        is_it2 = get_user_model().objects.filter(email=email)
        if is_it:
            err_msg = '사용자가 존재합니다.'
        if is_it2:
            err_msg = '이메일이 중복됩니다.'
        context = {'error':err_msg}
        if len(err_msg) > 1:
            return JsonResponse(context)

        get_user_model().objects.create_user(username=username,password=password1,birthday=birthday,email=email,gender=gender,nickname=nickname )
        context = {'ok':'회원가입완료'}
        return JsonResponse(context)


def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        me = auth.authenticate(request, username=username, password=password)
        if not me:
            return render(request, 'user/signin.html', {'error':'아이디 혹은 비밀번호가 틀렸습니다.'})
        auth.login(request, me)
        return redirect('/main')
    else:
        is_user = request.user.is_authenticated
        if is_user:
            return redirect('/main')
        return render(request, 'user/signin.html')

@login_required
def log_out(request):
    auth.logout(request)
    return redirect('/')

@login_required
def user_view(request):
    if request.method == 'GET':
        user_list = CustomUser.objects.all().exclude(username=request.user.username)
        return render(request, 'user/user_list.html', {'user_list':user_list})


def to_github(request):
    GITHUB_ID = 'aaf2060f1a6656e3ea85'
    GITHUB_SECRET = '9a8990c7e4bd8980f8d9fd6d98f7dc011c11ed70'
    REDIRECT_URI = 'http://localhost:8000/github/callback'
    return redirect(f'https://github.com/login/oauth/authorize?client_id={GITHUB_ID}&redirect_uri={REDIRECT_URI}&scope=read:user user:email')

def from_github(request):
    GITHUB_ID = 'aaf2060f1a6656e3ea85'
    GITHUB_SECRET = '9a8990c7e4bd8980f8d9fd6d98f7dc011c11ed70'
    REDIRECT_URI = 'http://localhost:8000/github/callback'
    code = request.GET.get('code')
    if code is None:
        return redirect('/')
    headers = {'Accept': 'application/json'}
    get_token = requests.post(f'https://github.com/login/oauth/access_token?client_id={GITHUB_ID}&client_secret={GITHUB_SECRET}&code={code}',headers=headers)
    err = get_token.json().get('error',None)
    if err is not None:
        return redirect('/')
    token = get_token.json()['access_token']
    headers = {'Authorization': f'token {token}'}
    get_info = requests.get(f'https://api.github.com/user',headers=headers)
    info = get_info.json()
    if info.get('login',None) is None:
        return redirect('/')
    profile_img = info['avatar_url']
    username = info['name'] if info['name'] else info['login']
    nickname = info['login']

    get_emails = requests.get(f'https://api.github.com/user/emails',headers=headers)
    email = ''
    for e in get_emails.json():
        if e['primary'] and e['verified']:
            email = e['email']

    try:
        user = get_user_model().objects.get(email=email)
        if user.login_method != models.CustomUser.LOGIN_GITHUB:
            print('깃허브로로 가입하지 않은 다른 아이디가 존재함')
            return redirect('/')

            
    except:
        user = models.CustomUser.objects.create(username=username,nickname=nickname,profile_img=profile_img,email=email,login_method=models.CustomUser.LOGIN_GITHUB)
        user.set_unusable_password()
        user.save()

    
    auth.login(request, user)
    return redirect('/mypage')
    

def to_kakao(request):
    REST_API_KEY = 'c26d6d939a034f9c2c805d751f046260'
    REDIRECT_URI = 'http://localhost:8000/kakao/callback'
    return redirect(f'https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code')

def from_kakao(request):
    REST_API_KEY = 'c26d6d939a034f9c2c805d751f046260'
    REDIRECT_URI = 'http://localhost:8000/kakao/callback'
    code = request.GET.get('code','None')
    if code is None:
        # 코드 발급 x
        return redirect('/')
    headers = {'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'}
    get_token = requests.post(f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&code={code}', headers=headers)
    get_token = get_token.json()
    if get_token.get('error',None) is not None:
        # 에러발생
        return redirect('/')
    token = get_token.get('access_token',None)

    headers = {'Authorization': f'Bearer {token}'}
    get_info = requests.post(f'https://kapi.kakao.com/v2/user/me', headers=headers)
    info = get_info.json()
    properties = info.get('properties')
    username = properties.get('nickname',None)
    nickname = username
    kakao_account = info.get('kakao_account')
    profile_img = properties.get('profile_image',None)
    gender = kakao_account.get('gender',None)
    email = kakao_account.get('email',None)
    if email is None:
        # 이메일 동의 안하면 로그인 불가 처리..
        return redirect('/sign-in')
    try:
        user = get_user_model().objects.get(email=email)

        if user.login_method != models.CustomUser.LOGIN_KAKAO:
            print('카카오로 가입하지 않은 다른 아이디가 존재함')
            return redirect('/')

            
    except:
        user = models.CustomUser.objects.create(username=username,nickname=nickname,profile_img=profile_img,email=email,login_method=models.CustomUser.LOGIN_KAKAO,gender=gender)
        user.set_unusable_password()
        user.save()

    
    auth.login(request, user)
    return redirect('/mypage')

@login_required
def my_page(request):
    if request.method == 'POST':
        pass

    else :
        user = request.user
        movie_list = user.favorite_movies.all()
        err = False
        if user.login_method != 'email' and (user.birthday == None or user.gender == None):
            err = '깃허브/카카오톡으로 로그인 하신 경우에는 반드시 생일, 성별을 설정해주세요 !'
        return render(request,'user/mypage.html', {'movie_list':movie_list, 'err':err} )

@login_required
def pw_change(request):
    if request.method == 'POST':
        pw1 = request.POST.get('password1',None)
        pw2 = request.POST.get('password2',None)
        if pw1 != pw2:
            return render(request,'user/pwchange.html',{'error':'비밀번호가 일치하지 않습니다.'} )
        user = request.user
        user.set_password(pw2)
        user.save()
        auth.logout(request)
        return redirect('/')
        
    else:
        if request.user.login_method != 'email':
            return redirect('/mypage')
        return render(request,'user/pwchange.html' )

certify_num = ''
def email_ajax(request):
    global certify_num
    if request.method =='POST':
        print('hi')
        certify_num = randint(10000,99999)

        email = json.loads(request.body)
        print(email)
        send_mail('레트로 플릭스 회원가입 인증 메일입니다.',
        f'안녕하세요 아래의 인증번호를 입력해주세요\n\n인증번호 : {certify_num}','taehyeki123@gmail.com',[email],fail_silently=False)
        context = {
            'result': '인증번호 발송이 완료되었습니다.',
        }

    return JsonResponse(context)

def certify_ajax(request):
    global certify
    if request.method =='POST':
        num = json.loads(request.body)
        result_msg = ''
        if num == str(certify_num):
            result_msg = '인증번호가 일치합니다.'
            certify = True
        else:
            result_msg = '인증번호가 다릅니다.'
        
        context = {
            'result': result_msg,
        }
    return JsonResponse(context)

def is_id(request):
    data = json.loads(request.body)
    try:
        # 아이디 유무 확인
        user = get_user_model().objects.get(username=data)
        # 깃허브 카카오로 회원가입 한 경우 안 됨
        if user.login_method != 'email':
            context = {'result':'깃허브 혹은 카카오로 로그인해주세요.','sns':'sns'}
            return JsonResponse(context)
        email = user.email
        # 임시 비밀번호 생성
        temp_pw = ''
        for _ in range(15):
            temp_pw += str(random.choice(string.ascii_lowercase + string.digits))
        user.set_password(temp_pw)
        user.save()
        # 임시 비밀번호 발송
        send_mail('레트로 플릭스 임시 비밀번호 메일입니다.',
        f'아래의 임시 비밀번호를 사용하여 로그인 해주세요.\n로그인 후 반드시 비밀번호를 변경 해주세요.\n\n임시 비밀번호 : {temp_pw}','taehyeki123@naver.com',[email],fail_silently=False)
        context = {
            'result': '등록된 이메일로 임시 비밀번호가 발송되었습니다.','ok':'ok'
        }
        return JsonResponse(context)
    except:
        context = {'result':'등록된 아이디가 존재하지 않습니다.'}
    
    
    return JsonResponse(context)
    
import datetime
def my_modify(request):
    if request.method == 'POST':
        img_file = request.FILES['file']
        ex = img_file.name.split('.')[-1]
        user = request.user
        url = 'https://retroflix.s3.ap-northeast-2.amazonaws.com/profile_img/'
        img_file.name = 'image-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+ '.'+ex
        user.profile_img = img_file
        user.save()
        user.profile_img = url + str(img_file)
        user.save()
    return redirect('/mypage')

def id_change(request):
    if request.method == 'POST':
        id = request.POST.get('id','')
        if id == '':
            return redirect('/mypage')
        if len(CustomUser.objects.filter(username=id)) >= 1:

            return redirect('/mypage')
        user = request.user
        user.username = id
        user.save()
    return redirect('/mypage')


def birth_change(request):
    if request.method == 'POST':
        birth = request.POST.get('birth','')
        if id == '':
            return redirect('/mypage')
        user = request.user
        user.birthday = birth
        user.save()
    return redirect('/mypage')


def gender_change(request):
    if request.method == 'POST':
        gender = request.POST.get('gender','')
        if gender == '1':
            return redirect('/mypage')

        user = request.user
        user.gender = gender
        user.save()
    return redirect('/mypage')
