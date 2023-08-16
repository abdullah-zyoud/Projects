from django.db import models
import re
from django.utils import timezone
from datetime import datetime



class UserManager(models.Manager):
    def regValidator(self, postData):
        errors = {}
        if len(postData['username']) < 2:
            errors['username'] = "First Name should atleast be 2 charecters"
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):                
            errors['email'] = "Invalid email address!"
        if User.objects.filter(email=postData['email']).exists():
            errors['email'] = "This email is already registered!"
        if len(postData['password'] or postData['password_conf']) < 8:
            errors['password_len'] = "Password should atleast be 8 charecters"
        if postData['password'] != postData['password_conf']:
            errors['password_match'] = "Passwords do not match"
        return errors 

    def loginValidator(self, postData):
        errors = {}  
        if not (User.objects.filter(email=postData['email2']) and User.objects.filter(password=postData['password2'])):
            errors['login'] = "Login failed! Check email and password"

        return errors 
    def addValidator(self, postData):
        errors = {}
        if len(postData['name']) < 1:
            errors['name'] = "Name is required"
        if len(postData['model']) < 1:
            errors['model'] = "Model is required"
        elif not postData['model'].isdigit():
            errors['model'] = "Model must be a number"
        if len(postData['color']) < 1:
            errors['color'] = "Color is required"
        if len(postData['fuelType']) < 1:
            errors['fuelType'] = "Fuel Type is required"
        if len(postData['price']) < 1:
            errors['price'] = "Price is required"
        elif not postData['price'].isdigit():
            errors['price'] = "Price must be a number"
        return errors 
    def editValidator(self, postData):
        errors = {}
        if len(postData['name']) < 1:
            errors['name'] = "Name is required"
        if len(postData['model']) < 1:
            errors['model'] = "Model is required"
        elif not postData['model'].isdigit():
            errors['model'] = "Model must be a number"
        if len(postData['color']) < 1:
            errors['color'] = "Color is required"
        if len(postData['fuelType']) < 1:
            errors['fuelType'] = "Fuel Type is required"
        if len(postData['price']) < 1:
            errors['price'] = "Price is required"
        elif not postData['price'].isdigit():
            errors['price'] = "Price must be a number"
        return errors 
    def dateValidator(self, postData):
        errors = {}
        from_date = postData.get('date1')
        to_date = postData.get('date2')
        if from_date or to_date:
            from_date_format = datetime.strptime(
                from_date, '%Y-%m-%d').date()
            to_date_format = datetime.strptime(
                to_date, '%Y-%m-%d').date()
            current_date = timezone.now().date()
            if from_date_format < current_date or to_date_format < current_date:
                errors["date"] = "from/to date must be in the Future"
            if from_date_format > to_date_format:
                errors["date1"] = "The to_date must be greater than the from_date"
        return errors

    def CheckoutValidator(self, postData):
        errors = {}
        card_num = postData.get('card-num')
        exp = postData.get('exp')
        cvv = postData.get('cvv')
        print(cvv,"hello")
        print(card_num)
        if len(cvv) !=3:
            errors['cvv'] = "cvv must be 3 number"
        if len(card_num) !=16:
            errors['card-num'] = "Card Number must be 16 number"
        if exp :
            try:
                input_date = datetime.strptime(exp, "%m/%y")
                current_date = datetime.now()
                if input_date < current_date:
                     errors['exp'] =("Card is expired,try another one")
            except ValueError:
                 errors['exp1'] =("Invalid date format. Please use 'mm/yy' format.")
        return errors 


class User(models.Model):
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    isAdmin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()   
    
class Car(models.Model): 
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    fuelType = models.CharField(max_length=255)
    price = models.IntegerField()
    rent_days = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    bookmarked = models.ManyToManyField(User,related_name="bookmarked")
    user = models.ForeignKey(User, related_name="users", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = UserManager()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key=True)
    cars = models.ManyToManyField(Car,related_name="cart_cars")
    total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager() 

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cars = models.ManyToManyField(Car,related_name="order_car")
    total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)