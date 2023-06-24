from django.db import models
from accounts.models import Account
from orders.models import Product

# Create your models here.

class Chat(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    user = models.ForeignKey(Account, on_delete= models.CASCADE)
    subject = models.CharField(max_length= 200, blank= True)
    review = models.TextField(max_length=600, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
