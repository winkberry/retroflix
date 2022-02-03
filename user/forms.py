# from cProfile import label
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from . import models

# class DateInput(forms.DateInput):
#     input_type = 'date'


# class SignUpForm(forms.ModelForm):
#     username = forms.CharField(label='이름',required=True,error_messages={'required':'아이디를 입력해주세요.'})
#     email = forms.EmailField(label='이메일',required=True,error_messages={'required':'이메일을 입력해주세요.'})
#     password1 = models.CharField(label='이메일',required=True,error_messages={'required':'이메일을 입력해주세요.'})
#     nickname = forms.CharField(label='닉네임')
#     birthday = forms.DateField(label='생년월일')
#     gender = forms.CharField(label='성별')
#     profile_img = forms.ImageField(label='프로필 사진')
#     class Meta:
#          model = models.CustomUser
#          fields = ['username','password1','password2','email','birthday','gender','nickname','profile_img']
