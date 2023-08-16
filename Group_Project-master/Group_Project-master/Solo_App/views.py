from math import log
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .models import *
from django.contrib import messages
from django.utils import timezone
import datetime

def index(request): 
    return render(request, 'home.html')

def add_to_bookmarked(request):
    text = request.GET.get('text')
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        if text == "Add to Favorites":
            user = User.objects.get(id=request.session['user_id'])
            car_id = int(request.GET.get('id'))
            car = Car.objects.get(id=car_id)
            user.bookmarked.add(car)
            return JsonResponse({'text': text}, status=200)
        if text == "Remove From Favorites":
            user = User.objects.get(id=request.session['user_id'])
            car_id = int(request.GET.get('id'))
            car = Car.objects.get(id=car_id)
            user.bookmarked.remove(car)
            return JsonResponse({'text': text}, status=200)
    return render(request, '/')


def sort_properties(request):
    if int(request.GET.get('sort_id'))== 0:
        sorted_properties = Car.objects.all()
    elif int(request.GET.get('sort_id'))== 1:
        sorted_properties = Car.objects.order_by('-model')
    elif int(request.GET.get('sort_id'))== 2:
        sorted_properties = Car.objects.order_by('model')
    elif int(request.GET.get('sort_id'))== 4:
        sorted_properties = Car.objects.order_by('price')
    elif int(request.GET.get('sort_id'))== 5:
        sorted_properties = Car.objects.order_by('-price')
    else:
        sorted_properties = Car.objects.order_by('color')
    user = User.objects.get(id=request.session['user_id'])
    bookmarked = user.bookmarked.all()
    sorted_properties_data = []
    for property in sorted_properties:
        # Prepare the property data in a dictionary format
        if bookmarked.count():
            for bookmark in bookmarked:
                if property.id == bookmark.id:
                    property_data = {
                        'id': property.id,
                        'name': property.name,
                        'model': property.model,
                        'price': format(property.price, "3,d"),
                        'color': property.color,
                        'fuelType': property.fuelType,
                        'bookmarked': True,
                    }
                    break
                else:
                    property_data = {
                        'id': property.id,
                        'name': property.name,
                        'model': property.model,
                        'price': format(property.price, "3,d"),
                        'color': property.color,
                        'fuelType': property.fuelType,
                        'bookmarked': False,
                        }
        else:
            property_data = {
                'id': property.id,
                'name': property.name,
                'model': property.model,
                'price': format(property.price, "3,d"),
                'color': property.color,
                'fuelType': property.fuelType,
                'bookmarked': False,
                }
        sorted_properties_data.append(property_data)
    return JsonResponse(sorted_properties_data, safe=False)


def regLog(request): 
    return render(request, 'index.html')

def register(request):
    errors = User.objects.regValidator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/regLog')
    else:
        user = User.objects.create(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'])
        user.save()
        #creating a cart when user regisers instead
        Cart.objects.create(
                            user = user,
                        )
        return redirect ('/regLog')

def login(request):
    errors = User.objects.loginValidator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/regLog')
    else:
        this_user = User.objects.get(email=request.POST['email2'])
        request.session['user_id'] = this_user.id
        request.session['username']=this_user.username
        if this_user.isAdmin==1 : 
            return redirect ('/admin') 
        else :
            return redirect('/user')
    
def admin(request): 
    context = {
        'username' : request.session['username'],
        'cars': Car.objects.all(),
    }
    return render(request, 'admin.html', context)
 
def user(request):
    user = User.objects.get(id=request.session['user_id'] ) 
    cars = Car.objects.all()
    p = Paginator(cars, 6)
    page = request.GET.get('page')
    cars = p.get_page(page)
    bookmarked = user.bookmarked.all()
   # bookmarkStatus = False
   # for bookmarked in bookmarked:
     #   for car in cars:
        #    if bookmarked == car:
        #        bookmarkStatus = True
    context = {
        'username' : user,
        'cars': cars,
        'bookmarked': bookmarked,
    }
    return render(request, 'user.html', context) 

def add(request):
    user_id = request.session.get('user_id')
    user =User.objects.get(id=user_id)
    if user.isAdmin == True:
        return render(request, 'add.html')
    else :
        return render(request, 'home.html')

        

def addCar(request):
    
        errors = Car.objects.addValidator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/add')
        else:
        
            Car.objects.create(
                            name = request.POST['name'], 
                            model = request.POST['model'], 
                            color = request.POST['color'],
                            fuelType = request.POST['fuelType'],
                            price = request.POST['price'],
                            user = User.objects.get(id=request.session['user_id']), 
                        )
            return redirect('/admin')

def edit(request, car_id):
    user_id = request.session.get('user_id')
    user =User.objects.get(id=user_id)
    if user.isAdmin == True:
        context = {
            'cars' : Car.objects.get(id=car_id) 
        }
        return render(request,'edit.html',context)
    else :
        return render(request, 'home.html')

def editCar(request, car_id):
    errors = Car.objects.editValidator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f'/edit/{car_id}')
    else:
        selected = Car.objects.get(id=car_id)
        selected.name = request.POST['name']
        selected.model = request.POST['model']
        selected.color = request.POST['color']
        selected.fuelType = request.POST['fuelType']
        selected.price = request.POST['price']
        selected.save()
        return redirect('/admin')

def delete(request, car_id):
    dell = Car.objects.get(id = car_id)
    dell.delete() 
    return redirect('/admin')



def show_favorites(request):
    user_id = request.session.get('user_id')
    user=User.objects.get(id=user_id)
    if user_id:
        context = {
            "user":user.bookmarked.all()
        }
        return render(request, "bookmark.html", context)

def logout(request): 
    request.session.flush()
    return redirect('/')


def view_cart(request,car_id):
    user_id = request.session.get('user_id')
    this_car=Car.objects.get(id=car_id)
    if user_id:
            context = {
                "car":this_car
            }
    return render (request, "add_to_cart.html",context)

def add_to_cart(request,car_id):
    user_id = request.session.get('user_id')
    this_car=Car.objects.get(id=car_id)
    from_date=request.POST['date1']
    to_date=request.POST['date2']
    errors = Cart.objects.dateValidator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f'/addToCart/{car_id}')
    else:
        user=User.objects.get(id=user_id)
        user_cart=Cart.objects.get(user=user)
        if from_date and to_date:
            start_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")
            diff = abs((end_date-start_date).days)
        if user_id:
            
            total_price=int(this_car.price*diff)
        else :
                total_price=this_car.price
        if user_cart:
            user_cart.cars.add(
            Car.objects.get(id=car_id))
            user_cart.total+=total_price
            this_car.rent_days=diff
            this_car.save()
            user_cart.save()

        else:
            this_cart= Cart.objects.create(
                                user = user, 
                                total = total_price,
                            )
            this_cart.cars.add(
                Car.objects.get(id=car_id))
            this_car.rent_days=diff
            this_car.save()

    return redirect('/cart')

def cart(request):
    user_id = request.session.get('user_id')
    user=User.objects.get(id=user_id)
    user_cart=Cart.objects.get(user=user)
    if user_id:
            context = {
                "cart":user_cart
            }

    return render (request, "cart.html",context)

def remove_car_from_cart(request, car_id):
    user_id = request.session.get('user_id')
    user=User.objects.get(id=user_id)
    user_cart=Cart.objects.get(user=user)
    this_car = Car.objects.get(id=car_id)
    user_cart.total-=this_car.rent_days*this_car.price
    user_cart.cars.remove(this_car)
    user_cart.save()
    return redirect('/cart')

def checkout(request):
    if 'user_id' in request.session:
        user=User.objects.get(id=request.session['user_id'])
        user_cart=Cart.objects.get(user=user)
        context = {
                    "cart":user_cart,
                    "cars":user_cart.cars.count()
            }
        return render (request, "checkout.html", context)
    else:
        return redirect('/regLog')
    
def order(request):
    if 'user_id' in request.session:
        errors = Cart.objects.CheckoutValidator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/checkout')
        else:
            user=User.objects.get(id=request.session['user_id'])
            user_cart=Cart.objects.get(user=user)
            order = Order.objects.create(user = user, total= user_cart.total)
            order.created_at = timezone.now()
            order.save()
            for car in user_cart.cars.all():
                order.cars.add(car)

            user_cart.cars.clear()
            user_cart.total = 0
            user_cart.save()
            return redirect('/view_orders')
    else:
        return redirect('/regLog')
    
def view_orders(request):
    if 'user_id' in request.session:
        user=User.objects.get(id=request.session['user_id'])
        print(Order.objects.filter(user=user))
        context = {
                    "orders":Order.objects.filter(user=user)
                }
        return render (request, "orders.html", context)
    else:
        return redirect('/regLog')


def bookmark(request):
    if 'user_id' in request.session:
        user_id = request.session.get('user_id')
        user=User.objects.get(id=user_id)

        context = {
                "user":user.bookmarked.all()
            }
        return render(request, "bookmark.html", context)
    else:
        return redirect('/regLog')
