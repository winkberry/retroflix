# Generated by Django 3.2.5 on 2022-02-03 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_remove_customuser_gogo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_img',
            field=models.ImageField(default='https://retroflix.s3.ap-northeast-2.amazonaws.com/profile_img/sparta.png', upload_to='profile_img/'),
        ),
    ]
