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
    voters = models.ManyToManyField(User, through='ProductVote', related_name='product_voters')

    def __str__(self):
        return self.title

    def pub_date_pretty(self):
        return self.pub_date.strftime('%e %b %Y')


class ProductVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username.upper()} voted on '{self.product.title}'"

    @staticmethod
    def is_already_voted(user, product):
        try:
            ProductVote.objects.get(user=user, product=product)
            return True
        except ProductVote.DoesNotExist:
            return False
