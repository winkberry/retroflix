from django.contrib import admin
from .models import Review

# Register your models here.

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author', 'created_date', 'star']
    list_filter = ['created_date', 'star']

admin.site.register(Review, ReviewAdmin)