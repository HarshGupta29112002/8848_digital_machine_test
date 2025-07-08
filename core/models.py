from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    isbn = models.CharField(max_length=10, unique=True, null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True) #Here i have added blank=True, so that the fields can be optional or can be left empty 
    num_pages = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)

class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    total_debt = models.DecimalField(max_digits=8, decimal_places=2, default=0)

class Transaction(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    rent_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(max_length= 10, choices=[('issued','Issued'),('returned','Returned')], default='issued')
    