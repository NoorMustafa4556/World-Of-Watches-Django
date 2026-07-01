from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Watch, Order, Testimonial, Cart, ManualPaymentMethod
from .services import OrderService, CartService

User = get_user_model()

def index(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    
    watches = Watch.objects.all()
    
    if category:
        watches = watches.filter(category=category)
    if query:
        watches = watches.filter(
            Q(watch_name__icontains=query) | 
            Q(watch_description__icontains=query) |
            Q(category__icontains=query)
        )

    testimonials = Testimonial.objects.all()
    return render(request, 'index.html', {
        'watches': watches, 
        'testimonials': testimonials,
        'query': query,
        'selected_category': category
    })

def about(request):
    return render(request, 'about.html')

def testimonial(request):
    testimonials = Testimonial.objects.all()
    return render(request, 'testimonial.html', {'testimonials': testimonials})

def contact(request):
    return render(request, 'contact.html')

def watch_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    
    watches = Watch.objects.all()
    
    if category:
        watches = watches.filter(category=category)
    if query:
        watches = watches.filter(
            Q(watch_name__icontains=query) | 
            Q(watch_description__icontains=query) |
            Q(category__icontains=query)
        )
        
    return render(request, 'product.html', {
        'watches': watches,
        'query': query,
        'selected_category': category
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.phone = phone
        user.save()

        messages.success(request, "Signup successful! Please login.")
        return redirect('login')

    return render(request, 'login_signup.html', {'page': 'signup'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login_signup.html', {'page': 'login'})

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('index')

@login_required
def place_order(request, watch_id):
    watch = get_object_or_404(Watch, id=watch_id)
    payment_methods = ManualPaymentMethod.objects.filter(is_active=True)

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method', '').strip()
        online_wallet_id = request.POST.get('online_wallet')
        payment_screenshot = request.FILES.get('payment_screenshot')

        if not quantity or not address or not payment_method:
            messages.error(request, "All fields are required.")
            return render(request, 'place_order.html', {'watch': watch, 'payment_methods': payment_methods})

        if payment_method == 'Online Payment' and (not online_wallet_id or not payment_screenshot):
            messages.error(request, "Please select a wallet and upload a payment screenshot.")
            return render(request, 'place_order.html', {'watch': watch, 'payment_methods': payment_methods})

        OrderService.create_single_order(
            request.user, watch_id, quantity, address, payment_method, online_wallet_id, payment_screenshot
        )
        return redirect('order_success') 

    return render(request, 'place_order.html', {'watch': watch, 'payment_methods': payment_methods})

def order_success(request):
    return render(request, 'order_success.html')

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'user_orders.html', {'orders': orders})

def submit_testimonial(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        message = request.POST.get('message')
        image = request.FILES.get('image')
        Testimonial.objects.create(name=name, message=message, image=image)
        return redirect('index')
    return render(request, 'submit_testimonial.html')

@login_required
def my_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        return redirect('index')
    return render(request, 'my_profile.html', {'user': user})

@login_required
def add_to_cart(request, watch_id):
    CartService.add_item(request.user, watch_id)
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'cart.html', {'items': items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    CartService.remove_item(request.user, item_id)
    return redirect('view_cart')

@login_required
def update_quantity(request, item_id):
    if request.method == 'POST':
        CartService.update_quantity(request.user, item_id, request.POST.get('quantity', 1))
    return redirect('view_cart')

@login_required
def place_cart_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    payment_methods = ManualPaymentMethod.objects.filter(is_active=True)

    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('view_cart')

    if request.method == 'POST':
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method', '').strip()
        online_wallet_id = request.POST.get('online_wallet')
        payment_screenshot = request.FILES.get('payment_screenshot')

        if not address or not payment_method:
            messages.error(request, "All fields are required.")
            return render(request, 'checkout_cart.html', {'items': cart.items.all(), 'total': sum(item.total_price() for item in cart.items.all()), 'payment_methods': payment_methods})

        if payment_method == 'Online Payment' and (not online_wallet_id or not payment_screenshot):
            messages.error(request, "Please select a wallet and upload a payment screenshot.")
            return render(request, 'checkout_cart.html', {'items': cart.items.all(), 'total': sum(item.total_price() for item in cart.items.all()), 'payment_methods': payment_methods})

        OrderService.create_cart_order(request.user, address, payment_method, online_wallet_id, payment_screenshot)
        return redirect('order_success')

    return render(request, 'checkout_cart.html', {'items': cart.items.all(), 'total': sum(item.total_price() for item in cart.items.all()), 'payment_methods': payment_methods})
