from django.db import models

# Create your models here.
class Review(models.Model):
    GENRE_CHOICES = [
        ('SF', 'SF'),
        ('액션', '액션'),
        ('코미디', '코미디'),
        ('드라마', '드라마'),
        ('공포', '공포'),
        ('애니메이션', '애니메이션'),
        ('로맨스', '로맨스'),
        ('스릴러', '스릴러'),
        ('미스터리', '미스터리'),
        ('판타지', '판타지'),
    ]
    title = models.CharField(max_length=100)
    director = models.CharField(max_length=50)
    actor = models.CharField(max_length=100)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    openyear = models.IntegerField()
    starpoint = models.FloatField()
    runningtime = models.IntegerField()
    reviewcontent = models.TextField()

    def __str__(self):
        return self.title