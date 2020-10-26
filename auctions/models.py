from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"



class Item(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    
    image_url = models.URLField(blank=True)
    category = models.ForeignKey('Category', related_name='items', on_delete=models.SET_DEFAULT, default=1)

    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='items')
    created_at = models.DateField(auto_now=True)
    open = models.BooleanField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.title}"


class User(AbstractUser):
    watchlist = models.ManyToManyField('Item', blank=True, related_name="watched_by")


class Bid(models.Model):
    item = models.OneToOneField('Item', on_delete=models.CASCADE)
    bidder = models.ForeignKey('User', on_delete=models.CASCADE, related_name='bids')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"bid for {self.item.title}"


class Comment(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='comments')
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateField(auto_now=True)
    text = models.TextField()


