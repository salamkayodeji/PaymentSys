from multiprocessing import context
from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Max,Min,Count,Avg
from django.template.loader import render_to_string
from django.conf import settings
import requests
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    min_price=Product.objects.aggregate(Min('price'))
    max_price=Product.objects.aggregate(Max('price'))
    minMaxPrice=Product.objects.aggregate(Min('price'),Max('price'))



    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems, 'min_price':min_price, 'max_price':max_price, 'minMaxPrice':minMaxPrice, }
    return render(request, 'inventory/home.html', context)

@login_required
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'inventory/cart.html', context)

@login_required
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    cards = Card_Details.objects.filter(customer = request.user)

    context = {'items':items, 'order':order, 'cartItems':cartItems, 'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY, 'cards':cards}
    return render(request, 'inventory/checkout.html', context)

@login_required
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)
        
@login_required
def verify_payment(request: HttpRequest, transaction_id:str) -> HttpResponse:
    order = get_object_or_404(Order, transaction_id=transaction_id)
    complete, result = order.verify_payment()
    card_detail, _ = Card_Details.objects.get_or_create(last_4 = result["authorization"]["last4"], authorization_code = result["authorization"]["authorization_code"],
                                             customer = order.customer, order = order, bin_no = result["authorization"]["bin"],
                                             exp_month = result["authorization"]["exp_month"],exp_year = result["authorization"]["exp_year"], 
                                             brand = result["authorization"]["brand"],
                                             card_type = result["authorization"]["card_type"])
    if card_detail:
        messages.success(request, 'Card Saved successful')
    else:
        messages.error(request, 'Error.')        
    if complete:
        messages.success(request, 'Verification successful')
    else:
        messages.error(request, 'Verification failed.')
    return redirect("home")

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ["name", "price"]
        
    def test_func(self):
        product = self.get_object()
        if self.request.user == product.customer or self.request.user.is_superuser:
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    success_url = '/'

    def test_func(self):
        product = self.get_object()
        if self.request.user == product.customer or self.request.user.is_superuser:
            return True
        return False

@login_required
def dash(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'inventory/dashboard.html', context)


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name','price']

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)

class Order_List(LoginRequiredMixin, ListView):
    model = Order    
    template_name = 'inventory/transaction_history.html'
    context_object_name= 'transactions'
    
    def get_context_data(self, **kwargs):
        context = super(Order_List, self).get_context_data(**kwargs)
        status = Order.objects.order_by("-status_message").values_list("status_message")

        history_status = []
        for t in status:
            if t[0] in history_status:
                continue
            history_status.append(t[0])
        context['status'] = history_status
        return context

        # And so on for more models
        return context



def search(request):
    q=request.GET['q']
    data=Product.objects.filter(title__icontains=q).order_by('-id')
    return render(request,'search.html',{'data':data})

# Filter Data
def filter_price(request):
    data = cartData(request)

    cartItems = data['cartItems']
    minPrice=request.GET['minPrice']
    maxPrice=request.GET['maxPrice']
    print("minPrice: ", minPrice, "maxPrice: ", maxPrice)
    allProducts=Product.objects.all().order_by('-id').distinct()
    allProducts=allProducts.filter(price__gte=minPrice)
    allProducts=allProducts.filter(price__lte=maxPrice)
    products=render_to_string('inventory/pages/items.html',{'products':allProducts, 'cartItems':cartItems})
    print(products)
    output_data = {'products': products}
   
    return JsonResponse(output_data)

def filter_data(request):
    status=request.GET.getlist('status[]')
    print(status)
    allOrders=Order.objects.all().order_by('-id').distinct()
    if len(status)>0:
        allOrders=allOrders.filter(status_message__in=status).distinct()
    status=render_to_string('inventory/pages/transactions.html',{'transactions':allOrders})
    output_data = {'status':status}
   
    return JsonResponse(output_data)


def filter_text(request):
    search_text = request.GET["search_text"]
    allOrders=Order.objects.all().order_by('-id').distinct()
    allOrders = allOrders.filter(transaction_id__icontains=search_text).order_by("-id")
    search_text=render_to_string('inventory/pages/transactions.html',{'transactions':allOrders})
    output_data = {'search_text':search_text}
    print(output_data)
    return JsonResponse(output_data)

@login_required
def card_payment(request):   
    authorization = request.POST.get("card")
    amount = request.POST.get("amount")
    transaction_id = request.POST.get("transaction_id")
    base_url = "https://api.paystack.co/transaction/charge_authorization"
    headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            'Content-Type' : 'application/json'
        }
    payloads = {"email": request.user.email, "amount": amount, "authorization_code": authorization, "reference":transaction_id,
                "currency": "NGN", }
    response = requests.post(base_url, json=payloads, headers=headers)  
    print(response)
    if response.status_code == 200:
        response_data = response.json()
        Order.objects.filter(transaction_id=transaction_id).update(customer = request.user, complete = True, transaction_id = response_data["data"]["reference"],
                                               amount= response_data["data"]["amount"], status = response_data["status"], email = request.user.email,
                                               status_message = response_data["data"]["gateway_response"], channel = response_data["data"]["channel"],
                                               paid_on=response_data["data"]["transaction_date"])   
        messages.success(request, 'Verification successful')
        return redirect(home)
    else:
        messages.error(request, 'Verification failed.')
    return render(request,'coinmac/home.html', {'messages':messages})


     
    