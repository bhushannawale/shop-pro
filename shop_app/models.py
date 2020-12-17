from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MaxValueValidator
from datetime import datetime
from django.utils.timezone import now

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)

    # extra fields
    ShopName=models.CharField(max_length=100)

    def __str__(self):
        return self.ShopName
class Medicine(models.Model):
    Shop=models.ForeignKey(Profile,related_name="medicines",on_delete=models.CASCADE)
    Name=models.CharField(max_length=100)
    Salt=models.CharField(max_length=100,blank= True,null=True)
    Company=models.CharField(max_length=100,blank= True,null=True)
    MRP=models.PositiveIntegerField()
    MFD = models.CharField(max_length=20)
    Expiry = models.CharField(max_length=20)
    Publish_date=models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.Name
    def get_absolute_url(self):
        return reverse("shop_app:StockDetail",kwargs={'pk':self.pk})


class Cart(models.Model):
    user = models.ForeignKey("Profile", on_delete=models.CASCADE)
    medicine = models.ForeignKey("Medicine", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Orders(models.Model):
    user = models.ForeignKey("Profile", on_delete=models.CASCADE)
    medicine = models.ForeignKey("Medicine", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    time = models.DateTimeField(default=now)