from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, LoginForm
from .models import Product, Delivery, User, ToBeDelivered, ProductDelivery
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def product_list(request):
    products = Product.objects.all()
    return render(request, 'courier/product_list.html', {'products': products})


def delivery_list(request):
    deliveries = Delivery.objects.all().select_related('courier', 'store')

    # Статистика
    delivered_count = deliveries.filter(delivered=True).count()
    pending_count = deliveries.filter(delivered=False).count()

    context = {
        'deliveries': deliveries,
        'delivered_count': delivered_count,
        'pending_count': pending_count,
    }

    return render(request, 'courier/delivery_list.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registration_success')
    else:
        form = RegistrationForm()

    return render(request, 'courier/register.html', {'form': form})


def registration_success(request):
    return render(request, 'courier/registration_success.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            request.session['user_type'] = user.user_type

            if user.user_type == 'courier':
                return redirect('courier_dashboard')
            elif user.user_type == "store":
                return redirect('store_dashboard')
    else:
        form = LoginForm()

    return render(request, 'courier/login.html', {'form': form})


def logout_view(request):
    request.session.flush()
    return redirect('register')


def courier_dashboard(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'courier':
        return redirect('login')

    courier = get_object_or_404(User, id=request.session['user_id'])

    active_orders = Delivery.objects.filter(courier=courier, delivered=False)

    completed_orders = Delivery.objects.filter(courier=courier, delivered=True)

    available_orders = Delivery.objects.filter(courier__isnull=True, delivered=False)

    context = {
        'user': {
            'name': request.session['user_name'],
            'type': request.session['user_type']
        },
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'available_count': available_orders.count(),
    }
    return render(request, 'courier/courier_dashboard.html', context)


def store_dashboard(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'store':
        return redirect('login')

    user_id = request.session['user_id']
    products = Product.objects.all()

    context = {
        'user': {
            'name': request.session['user_name'],
            'type': request.session['user_type']
        },
        'products': products
    }
    return render(request, 'courier/store_dashboard.html', context)


def create_order(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'store':
        return redirect('login')

    store = get_object_or_404(User, id=request.session['user_id'])
    cart_items = request.session.get('cart', [])

    if request.method == 'POST' and cart_items:
        delivery = Delivery.objects.create(store=store)

        for item in cart_items:
            product = get_object_or_404(Product, id=item['product_id'])

            to_be_delivered = ToBeDelivered.objects.create(
                product=product,
                quantity=item['quantity'],
                price=product.price
            )

            ProductDelivery.objects.create(
                items=to_be_delivered,
                delivery=delivery
            )

            product.quantity -= item['quantity']
            product.save()

        request.session['cart'] = []

        return redirect('order_success', delivery_id=delivery.id)

    products = Product.objects.filter(quantity__gt=0)

    cart_total = sum(item['total'] for item in cart_items) if cart_items else 0

    return render(request, 'courier/create_order.html', {
        'products': products,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'user': {'name': request.session['user_name']}
    })


def order_detail(request, order_id):
    if 'user_id' not in request.session:
        return redirect('login')

    delivery = get_object_or_404(Delivery, id=order_id)

    user_id = request.session['user_id']
    user_type = request.session['user_type']

    if user_type == 'store' and delivery.store.id != user_id:
        return redirect('store_orders')
    elif user_type == 'courier' and delivery.courier and delivery.courier.id != user_id:
        return redirect('courier_dashboard')

    product_deliveries = ProductDelivery.objects.filter(delivery=delivery)
    items = [pd.items for pd in product_deliveries]

    total_amount = delivery.get_total_amount()

    return render(request, 'courier/order_detail.html', {
        'delivery': delivery,
        'items': items,
        'total_amount': total_amount,
        'user': {
            'name': request.session['user_name'],
            'type': user_type
        }
    })


@csrf_exempt
def add_to_cart(request):
    if 'user_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'Не авторизован'})

    if request.method == 'POST':
        try:
            product_id = int(request.POST.get('product_id'))
            quantity = int(request.POST.get('quantity', 1))

            product = get_object_or_404(Product, id=product_id)

            if quantity > product.quantity:
                return JsonResponse(
                    {'success': False, 'error': f'Недостаточно товара. Доступно: {product.quantity} шт.'})

            cart = request.session.get('cart', [])

            item_found = False
            for item in cart:
                if item['product_id'] == product_id:
                    new_quantity = item['quantity'] + quantity
                    if new_quantity > product.quantity:
                        return JsonResponse(
                            {'success': False, 'error': f'Нельзя добавить больше {product.quantity} шт.'})
                    item['quantity'] = new_quantity
                    item['total'] = float(product.price * new_quantity)
                    item_found = True
                    break

            if not item_found:
                cart.append({
                    'product_id': product_id,
                    'product_name': product.name,
                    'quantity': quantity,
                    'price': float(product.price),
                    'total': float(product.price * quantity)
                })

            request.session['cart'] = cart
            request.session.modified = True

            cart_total = sum(item['total'] for item in cart)
            cart_count = len(cart)

            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'cart_total': cart_total,
                'message': f'{product.name} добавлен в корзину!'
            })

        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Неверные данные'})

    return JsonResponse({'success': False, 'error': 'Неверный запрос'})


def remove_from_cart(request, product_id):
    if 'user_id' not in request.session:
        return redirect('login')

    try:
        cart = request.session.get('cart', [])
        new_cart = [item for item in cart if item['product_id'] != product_id]

        request.session['cart'] = new_cart
        request.session.modified = True

        return redirect('create_order')

    except Exception as e:
        return redirect('create_order')


def order_success(request, delivery_id):
    if 'user_id' not in request.session:
        return redirect('login')

    delivery = get_object_or_404(Delivery, id=delivery_id)

    if request.session['user_type'] == 'store' and delivery.store.id != request.session['user_id']:
        return redirect('store_orders')

    product_deliveries = ProductDelivery.objects.filter(delivery=delivery)
    items = [pd.items for pd in product_deliveries]

    return render(request, 'courier/order_success.html', {
        'delivery': delivery,
        'items': items,
        'user': {'name': request.session['user_name']}
    })


def store_orders(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'store':
        return redirect('login')

    store = get_object_or_404(User, id=request.session['user_id'])
    orders = Delivery.objects.filter(store=store).order_by('-time_created')

    total_orders = orders.count()
    delivered_orders = orders.filter(delivered=True).count()
    pending_orders = orders.filter(delivered=False).count()

    total_spent = 0
    for order in orders:
        total_spent += order.get_total_amount()

    return render(request, 'courier/store_orders.html', {
        'orders': orders,
        'user': {'name': request.session['user_name']},
        'stats': {
            'total_orders': total_orders,
            'delivered_orders': delivered_orders,
            'pending_orders': pending_orders,
            'total_spent': total_spent
        }
    })


def mark_delivered(request, delivery_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'courier':
        return redirect('login')

    delivery = get_object_or_404(Delivery, id=delivery_id)

    if delivery.courier and delivery.courier.id == request.session['user_id'] and not delivery.delivered:
        delivery.delivered = True
        delivery.time_delivered = timezone.now()
        delivery.save()

    return redirect('order_detail', order_id=delivery_id)


def available_orders(request):
    if 'user_id' not in request.session or request.session['user_type'] != 'courier':
        return redirect('login')

    available_orders = Delivery.objects.filter(
        courier__isnull=True,
        delivered=False
    ).order_by('-time_created')

    return render(request, 'courier/available_orders.html', {
        'available_orders': available_orders,
        'user': {'name': request.session['user_name']}
    })


def take_order(request, order_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'courier':
        return redirect('login')

    delivery = get_object_or_404(Delivery, id=order_id)
    courier = get_object_or_404(User, id=request.session['user_id'])

    if delivery.courier is None and not delivery.delivered:
        delivery.courier = courier
        delivery.save()
        return redirect('courier_dashboard')

    return redirect('available_orders')


def complete_order(request, order_id):
    if 'user_id' not in request.session or request.session['user_type'] != 'courier':
        return redirect('login')

    delivery = get_object_or_404(Delivery, id=order_id)
    courier = get_object_or_404(User, id=request.session['user_id'])

    if delivery.courier and delivery.courier.id == courier.id and not delivery.delivered:
        delivery.delivered = True
        delivery.time_delivered = timezone.now()
        delivery.save()

    return redirect('courier_dashboard')
