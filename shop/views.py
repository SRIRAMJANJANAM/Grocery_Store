from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from shop.forms import SignUpForm
from django.contrib import messages
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
import razorpay
import json

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def base_view(request):
    return render(request, 'shop/base.html')

def home(request):
    search_query = request.GET.get('search', '')
    if search_query:
        products = Product.objects.filter(name__istartswith=search_query)
    else:
        products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})

@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == "POST":
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)

        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if action == "add":
            cart_item.quantity += 1
            cart_item.save()
        elif action == "remove":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()  # If quantity is 1, delete item
        elif action == "remove_item":
            cart_item.delete()  # Completely remove item from cart

    return render(request, 'shop/cart.html', {'cart': cart})

@login_required
def order_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    totalprice = float(product.price * cart_item.quantity)  # Convert to float for Razorpay
    
    if request.method == "POST":
        # Create customer entry
        customer = Customer.objects.create(
            user=request.user,
            item=product.name,
            price=product.price,
            quantity=cart_item.quantity,
            totalprice=totalprice,
            cname=request.POST.get("cname"),
            phno=request.POST.get("phno"),
            email=request.POST.get("email"),
            houseno=request.POST.get("houseno"),
            roadno=request.POST.get("roadno"),
            address=request.POST.get("address"),
            pin=request.POST.get("pin"),
            state=request.POST.get("state"),
            country=request.POST.get("country"),
        )
        
        # Store customer ID and order details in session for payment processing
        request.session['pending_customer_id'] = customer.id
        request.session['pending_product_id'] = product.id
        request.session['pending_cart_item_id'] = cart_item.id
        
        # Redirect to payment page
        return redirect('process_payment')

    return render(request, 'shop/order_product.html', {
        'product': product,
        'cart_item': cart_item,
        'total': totalprice,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })

@login_required
def process_payment(request):
    # Get pending order details from session
    customer_id = request.session.get('pending_customer_id')
    product_id = request.session.get('pending_product_id')
    cart_item_id = request.session.get('pending_cart_item_id')
    
    if not all([customer_id, product_id, cart_item_id]):
        messages.error(request, "No pending order found!")
        return redirect('home')
    
    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    # Create Razorpay order
    order_amount = int(customer.totalprice * 100)  # Amount in paise
    order_currency = 'INR'
    order_receipt = f'order_{customer.id}_{product.id}'
    
    # Create order in Razorpay
    razorpay_order = razorpay_client.order.create(
        dict(
            amount=order_amount,
            currency=order_currency,
            receipt=order_receipt,
            payment_capture='0'  # 0 for manual capture, 1 for auto capture
        )
    )
    
    # Store Razorpay order ID in session
    request.session['razorpay_order_id'] = razorpay_order['id']
    
    context = {
        'customer': customer,
        'product': product,
        'cart_item': cart_item,
        'total': customer.totalprice,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'callback_url': request.build_absolute_uri('/payment-callback/'),
        'amount': order_amount,
    }
    
    return render(request, 'shop/payment.html', context)

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            # Get payment details from Razorpay
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            # Verify the payment signature
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Get pending order details from session
            customer_id = request.session.get('pending_customer_id')
            product_id = request.session.get('pending_product_id')
            cart_item_id = request.session.get('pending_cart_item_id')
            
            if all([customer_id, product_id, cart_item_id]):
                customer = Customer.objects.get(id=customer_id)
                product = Product.objects.get(id=product_id)
                cart_item = CartItem.objects.get(id=cart_item_id)
                
                # Capture payment (optional - if you want to capture immediately)
                razorpay_client.payment.capture(payment_id, int(customer.totalprice * 100))
                
                # Create Order
                order = Order.objects.create(
                    customer=customer,
                    total_amount=customer.totalprice,
                    status='Payment Successful'
                )
                
                # Create OrderItem
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity
                )
                
                # Delete cart item
                cart_item.delete()
                
                # Clear session data
                del request.session['pending_customer_id']
                del request.session['pending_product_id']
                del request.session['pending_cart_item_id']
                del request.session['razorpay_order_id']
                
                messages.success(request, "Payment successful! Your order has been placed.")
                return redirect('payment_success', order_id=order.id)
            else:
                messages.error(request, "Session expired. Please try again.")
                return redirect('home')
                
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed!")
            return redirect('payment_failed')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('payment_failed')
    
    return redirect('home')

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    return render(request, 'shop/payment_success.html', {'order': order})

def payment_failed(request):
    return render(request, 'shop/payment_failed.html')

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    total = sum(item.get_total() for item in cart.cartitem_set.all())
    
    if request.method == "POST":
        # Handle checkout logic
        cart.cartitem_set.all().delete()
        return redirect('home')
    
    return render(request, 'shop/checkout.html', {'total': total})

def logout_view(request):
    return render(request, 'shop/logout.html')

def signup_view(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            login(request, user)
            messages.success(request, "Signup successful!")
            return HttpResponseRedirect('/')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'shop/signup.html', {'form': form})

def success_view(request):
    return render(request, 'shop/success.html')

@login_required
def navi_view(request):
    logs = NavigationLog.objects.filter(user=request.user).order_by('-date', '-time')
    
    date_filter = request.GET.get('date')
    if date_filter:
        date_obj = parse_date(date_filter)
        if date_obj:
            logs = logs.filter(date=date_obj)
    
    try:
        per_page = int(request.GET.get('per_page', 25))
        if per_page <= 0:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    paginator = Paginator(logs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    per_page_options = [10, 20, 25, 50, 100]
    
    return render(request, 'shop/nav.html', {
        'page_obj': page_obj,
        'date_filter': date_filter,
        'per_page': per_page,
        'per_page_options': per_page_options,
    })