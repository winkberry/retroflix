from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
# Register your models here.
""
@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    my_fields = (
        (
            ('CustomUserField'),
            {
                'fields':(
                    'birthday', 
                    'gender', 
                    'nickname',
                    'profile_img',
                    'favorite_movies'
                    )
            },
        ),
    )
    list_display = ('username',
        'birthday', 
                    'gender', 
                    'nickname',
                    'profile_img',
                    'login_method',)
    fieldsets = my_fields  + UserAdmin.fieldsets 
    pass