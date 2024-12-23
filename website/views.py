from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login
from .forms import CustomLoginForm
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime, timedelta, date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count, Sum, Max
from django.core.mail import send_mail
from json import dumps 
from .models import *
from .forms import *
from django.core import serializers
import stripe
import itertools 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

stripe.api_key = ''#set this in console

def home(request):
    faqs            = Faq.objects.all()
    cars            = Car.objects.all()[:4]
    #2 row list under the search
    carLatest       = Car.objects.all()[4:7]
    carLatestSecond = Car.objects.all()[7:10]
    current  = request.user
    featured_vehicles = Car.objects.all()[:6]  # Adjust the limit as needed

    year = Year.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    

    context={
    'cars':cars,
    'featured_vehicles': featured_vehicles,
    'year':year,
    'carLatest':carLatest,
    'carLatestSecond':carLatestSecond,
    'faqs':faqs,
    'current':current}
    return render(request,'home.html', context)



def login_page(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect after successful login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid form submission.')

    else:
        form = CustomLoginForm()

    return render(request, 'auth/login.html', {'form': form})

def registerPage(request):
    # Initialize the form
    forms = createUserForm()

    if request.method == 'POST':
        forms = createUserForm(request.POST)
        if forms.is_valid():
            # Save the user if the form is valid
            forms.save()
            user = forms.cleaned_data.get('username')
            
            # Add a success message and redirect to the login page
            messages.success(request, f'Account was created for {user}, you can now log in!')
            return redirect('login')  # Make sure you have a URL for 'login'

    # Render the registration page with the form
    context = {
        'form': forms
    }
    return render(request, 'auth/register.html', context)


@login_required(login_url='home.html')
def logoutPage(request):
    logout(request)
    return redirect('home')


def loadData(request):
    current   = request.user
    yearData  = request.POST['carYear']
    modelData = request.POST['carModel']

  
    if not modelData and not yearData:
        carDatabase = Car.objects.all()[4:]
    elif not modelData:
        carDatabase = Car.objects.filter(year_id=yearData)
    else:
        carDatabase = Car.objects.filter(year_id=yearData, id=modelData )
    
    context={'modelData':modelData,
    'yearData':yearData,
    'carDatabase':carDatabase,
    'current':current }
    return render(request,'infoGenerated.html',context)


def loadForm(request):
    year_id = request.GET.get('carYear')
    selectedCar = Car.objects.filter(year_id=year_id).order_by('model')

    context={'selectedCar':selectedCar}
    return render(request,'dropList.html',context)


def carPage(request,pk):
    carpage = get_object_or_404(Car, id=pk)
    current = request.user
    related_cars = carpage.get_related_cars()
    
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.car = carpage
            contact_message.save()
            return render(request, 'car.html', {'carpage': carpage, 'current':current, 'form': ContactMessageForm(), 'success': True})
    else:
        form = ContactMessageForm()
        
    context = {'carpage':carpage,'current':current, 'form':form,'related_cars': related_cars, }
    
    return render(request, 'car.html', context)
    

@login_required(login_url='home.html')
def customerPage(request,pk):
    
    current     = request.user
    dataHolder  = Order.objects.filter(customerID=current.id)
    totalPrice  = list(dataHolder.aggregate(Sum('price')).values())[0]
    orderList   = reversed(dataHolder)
    lastOrder   = dataHolder.last()
    favCar      = dataHolder.values('carModel').annotate(car_count=Count('carModel'))
    if not favCar:
        favCarList  = "Rent something ;)"
    else:
        favCarList  = list(favCar.aggregate(Max('carModel')).values())
        favCarList  = favCarList[0].replace("['']",'')

    
    context = {
        'current'    :current,
        'orderList'  :orderList,
        'lastOrder'  :lastOrder,
        'totalPrice' :totalPrice,
        'favCarList' :favCarList,
        'dataHolder' :dataHolder,
    }
    return render(request,'customer.html',context)
@login_required(login_url='home.html')
def updateView(request):
    current       = request.user
    
    if request.method == 'POST':
        updateForm    = CustomerUpdate(request.POST,request.FILES,instance=current.customer)
        if updateForm.is_valid():
            updateForm.save()
            return redirect('home')
    else:
        updateForm    = CustomerUpdate(instance=current.customer)
    context = {
        'current'    :current,
        'updateForm' :updateForm,
    }
    return render(request, 'updateCustomer.html' ,context)



@login_required(login_url='home.html')
def createOrder(request,pk):
    dataHolder  = []
    dataClean   = []
    current     = request.user
    carData     = Car.objects.get(id=pk)
    pickupPlace = Location.objects.all()
    rawData     = Order.objects.filter(automobileId=pk)
    priceOfAddi = Additions.objects.last()
    
    
    #making a list of blocked days for date picker 
    for x in rawData:
        if x.endRent > datetime.now().date():
            sdate = x.startRent
            edate = x.endRent
            delta = edate - sdate
            dataHolder = [ (sdate + timedelta(days=i)) for i in range(delta.days + 1) ]
    
    dataClean = [ x.strftime("%Y/%m/%d") for x in dataHolder]
    dataClean = dumps(dataClean)
  
    context={
        'current':current,
        'carData':carData,
        'dataClean':dataClean,
        'pickupPlace':pickupPlace,
        'priceOfAddi':priceOfAddi 
        }
    return render ( request, 'renting.html', context,)
@login_required(login_url='home.html')
def makeOrder(request, pk):
    car       = Car.objects.get(id=pk)
    startDate = request.POST['startDate']
    endDate   = request.POST['endDate']
    current   = request.user
    
    
    format    = "%Y/%m/%d"
    if (request.method == 'POST' and endDate > startDate):
        additions   = 0 
        priceOfAddi = Additions.objects.last()
        sdate       = datetime.strptime(startDate, format)
        edate       = datetime.strptime(endDate, format)
        daysTotal   = edate - sdate
        days        = int(daysTotal.days)
        place       = Location.objects.get(id=request.POST['pickUpPlace'])
        fuel        = request.POST.get('fuel', '') == 'on'
        insurance   = request.POST.get('insurance', '') == 'on'
        
        
        if ( 'fuel' in request.POST and 'insurance' in request.POST ):
            additions = priceOfAddi.insurance + priceOfAddi.fuel 
        elif 'fuel' in request.POST:
            additions = priceOfAddi.fuel
        elif 'insurance' in request.POST:
            additions = priceOfAddi.insurance
        priceTotal    = (int(car.price)*days+additions)
        

        addingToBase  = Order(customer=current,customerID=current.id,carModel=car.model,automobileId=car.id,price=priceTotal,startRent=sdate ,endRent=edate ,pickUp=place,fullFuel=fuel,insurance=insurance)
        addingToBase.save()
        currentOrder = addingToBase.id
            

    context={
        'car'          :car,
        'fuel'         :fuel, 
        'place'        :place,
        'endDate'      :endDate,
        'current'      :current,
        'insurance'    :insurance,
        'startDate'    :startDate,
        'priceTotal'   :priceTotal,
        'currentOrder' :currentOrder,
        }
    return render ( request, 'confir.html', context,)

@login_required(login_url='home.html')
def payment(request,pk):
    current       = request.user
    phoneAuth     = request.POST['phoneCardAuth']
    emailAuth     = request.POST['emailCardAuth']
    databaseOrder = Order.objects.get(id=pk)
    pricePennies  = (databaseOrder.price * 100)
    
    if (request.method == 'POST' and phoneAuth == current.customer.phone and emailAuth == current.customer.email   ):
        customer = stripe.Customer.create(
            
            email       = current.customer.email,
            phone       = current.customer.phone,
            description = databaseOrder.customerID,
            source      = request.POST['stripeToken']
            )
        charge = stripe.Charge.create(
            customer    = customer,
            amount      = pricePennies,
            currency    ='usd',
            description = pk 
            )
        context={}
        return render ( request, 'succes.html', context,)
    else:
        return redirect('confir.html')

@login_required(login_url='home.html')
def cancelOrder(request,pk):
   
    order           = Order.objects.get(id=pk)
    orderForCancel  = canceledOrders(payed=order.payed,customerID=order.customerID,price=order.price,automobileId=order.automobileId)
    orderForCancel.save()
    order.delete()

   
    return redirect ('home')


# def gallery(request):
#     picList = ['car1', 'car3', 'car5']
#     pictureList = []

#     for x in picList:
#         photo = Car.objects.values_list(x, flat=True)  # Use `flat=True` to simplify list structure
#         pictureList.extend(photo)

#     # Filter out None values and reverse the order
#     data = list(filter(None, pictureList))[::-1]

#     # Define a default `current` object (e.g., the first Car object or another logic)
#     current = Car.objects.first()  # Replace `.first()` with your desired logic to fetch the `current` car

#     context = {
#         'data': data,
#         'current': current,  # Pass `current` to the template
#     }
#     return render ( request, 'gallery.html', context)
from django.core.paginator import Paginator, Page

def gallery(request):
    cars = Car.objects.all()  # Ambil semua mobil
    page_number = request.GET.get('page', 1)
    
    # Menambahkan pagination jika diperlukan
    paginator = Paginator(cars, 6)  # Menampilkan 6 mobil per halaman
    page_obj = paginator.get_page(page_number)
    
    context = {
        'cars': page_obj,  # Kirimkan objek mobil dengan pagination
    }
    return render(request, 'gallery.html', context)

def contact(request):
    return render(request, 'contact.html')

def blog(request):
    return render(request, 'blog.html')
def price(request):
    return render(request, 'price.html')
def about(request):
    return render(request, 'about.html')
def services(request):
    return render(request, 'services.html')