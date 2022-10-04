from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User
from .paystack import PayStack
import uuid
import secrets
from django.urls import reverse



# Create your models here.
class Product(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    price = models.FloatField()
    
    
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse("home")

    
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)

    transaction_id = models.CharField(max_length=200)
    email = models.EmailField(null = True)
    amount = models.FloatField(null = True)
    status = models.BooleanField(default=False)
    status_message = models.CharField(max_length=200, null = True)
    channel = models.CharField(max_length=200, null = True)
    paid_on = models.DateTimeField(null = True)

    
    class Meta:
        ordering = ('-date_ordered',)

    def __str__(self):
        return str(self.id)
    
    def save(self, *args, **kwargs):
        while not self.transaction_id:
            transaction_id = secrets.token_urlsafe(20)
            object_with_similar_Ref = Order.objects.filter(transaction_id = transaction_id)
            if not object_with_similar_Ref:
                self.transaction_id = transaction_id
        super().save(*args, **kwargs)
    
    
    
    
    def verify_payment(self):
        paystack = PayStack()
        info, result = paystack.verify_payment(self.transaction_id, self.amount)
        if info:
            self.complete = True
            if result['status'] == "failed":
                self.status = False
            else:
                self.status = info
            self.amount = result['amount'] / 100
            self.email = result['customer']['email']
            self.channel = result['channel']
            self.status_message = result['gateway_response']
            self.paid_on = result['paid_at']
            self.save()
        else:
            self.status = info
            self.amount = 0.0   
            self.complete = True   
            self.channel = None   
            self.status_message = result['message']
            self.save()
        if self.complete:
            return True, result
        return False


        
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total 
    

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total 

 

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
#    amount = models.PositiveIntegerField()

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class Card_Details(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    authorization_code = models.CharField(max_length = 200)
    bin_no = models.CharField(max_length = 10)
    last_4 = models.CharField(max_length = 5)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    brand = models.CharField(max_length = 20)
    card_type = models.CharField(max_length = 100)
    
    class Meta:
        unique_together = ['bin_no', 'last_4']

    
    
     