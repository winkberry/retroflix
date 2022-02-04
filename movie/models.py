from django.db import models 
class Movie(models.Model): 
    class Meta: db_table = 'movies'

    title = models.CharField(max_length=45, null=False) 
    openDt = models.IntegerField() 
    clip = models.CharField(max_length=100, default='') 
    star = models.FloatField() 
    genre = models.IntegerField()

    def __str__(self):
        return self.title