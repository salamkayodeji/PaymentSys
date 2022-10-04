from django.urls import path
from inventory import views 
from django.contrib import admin

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard", views.dash, name="dash"),
    path("cart", views.cart, name="cart"),
    path("checkout", views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
    path('<str:transaction_id>/', views.verify_payment, name="verify-payment"),
    path('product/create', views.ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>', views.ProductUpdateView.as_view(), name='product-update'),
    path('product/<int:pk>/delete', views.ProductDeleteView.as_view(), name='product-delete'),
    path('filter-price',views.filter_price,name='filter_price'),
    path('filter-data',views.filter_data,name='filter_data'),
    path('filter-text',views.filter_text,name='filter_text'),
    path('card-payment',views.card_payment,name='card_payment'),
    path('history',views.Order_List.as_view(),name='history'),


]