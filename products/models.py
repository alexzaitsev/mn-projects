from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    pub_date = models.DateTimeField()
    votes_total = models.IntegerField(default=1)
    image = models.ImageField(upload_to='images/')
    icon = models.ImageField(upload_to='images/')
    body = models.TextField()
    hunter = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def pub_date_pretty(self):
        return self.pub_date.strftime('%e %b %Y')
