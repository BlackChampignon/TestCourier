from django.urls import path
from . import views

urlpatterns = [
    # To delete:
    path('products/', views.product_list, name='product_list'),
    path('deliveries/', views.delivery_list, name='delivery_list'),

    # Authorization and login
    path('register/', views.register, name='register'),
    path('register/success/', views.registration_success, name='registration_success'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Courier urls
    path('courier/dashboard/', views.courier_dashboard, name='courier_dashboard'),
    path('available_orders/', views.available_orders, name='available_orders'),
    path('take_order/<int:order_id>/', views.take_order, name='take_order'),
    path('complete_order/<int:order_id>/', views.complete_order, name='complete_order'),

    # Store urls
    path('store/dashboard/', views.store_dashboard, name='store_dashboard'),
    path('create_order/', views.create_order, name='create_order'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/success/<int:delivery_id>/', views.order_success, name='order_success'),
    path('store/orders/', views.store_orders, name='store_orders'),
    path('order/<int:delivery_id>/mark_delivered/', views.mark_delivered, name='mark_delivered'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]
