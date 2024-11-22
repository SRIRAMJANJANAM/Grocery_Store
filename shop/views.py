from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def base_view(request):
    search_query = request.GET.get('search', '')
    if search_query:
        products = Product.objects.filter(name__istartswith=search_query)
    else:
        products = Product.objects.all()
    return render(request,'shop/base.html')



def home(request):
    search_query = request.GET.get('search', '')
    if search_query:
        products = Product.objects.filter(name__istartswith=search_query)
    else:
        products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})

stripe.api_key = settings.STRIPE_SECRET_KEY


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
@login_required
def order_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)  # Get or create the user's cart
    cart_item = CartItem.objects.get(cart=cart, product=product)
    total_cart_value = cart.get_cart_total() 

    totalprice = product.price * cart_item.quantity

    if request.method == "POST":
        # Create a new customer entry for this order
        customer_data = {
            "user": request.user,  # Associate customer with the logged-in user
            "item": product.name,
            "price": product.price,
            "quantity": cart_item.quantity,
            "totalprice": totalprice,
            "cname": request.POST.get("cname"),
            "phno": request.POST.get("phno"),
            "email": request.POST.get("email"),
            "houseno": request.POST.get("houseno"),
            "roadno": request.POST.get("roadno"),
            "address": request.POST.get("address"),
            "pin": request.POST.get("pin"),
            "state": request.POST.get("state"),
            "country": request.POST.get("country"),
        }

        # Create a new customer entry each time the user places an order
        Customer.objects.create(**customer_data)

        cart_item.delete()  # Remove the cart item after placing the order
        return redirect('success')

    return render(request, 'shop/order_product.html', {
        'product': product,
        'cart_item': cart_item,
        'total': totalprice,  # Display product total based on quantity
        'cart_total': total_cart_value,  # Add cart total to context
    })


@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    total = sum(item.get_total() for item in cart.cartitem_set.all())
    
    if request.method == "POST":
        stripe.PaymentIntent.create(
            amount=int(total * 100),  # Convert to cents
            currency="ind",
            payment_method_types=["card"],
        )
        cart.cartitem_set.all().delete()  # Clear cart after payment
        return redirect('home')
    
    return render(request, 'shop/checkout.html', {'total': total})


def logout_view(request):
    return render(request,'shop/logout.html')


from shop.forms import SignUpForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login

def signup_view(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)  # Hash the password
            user.save()

            # Automatically log in the user after signup
            login(request, user)
            messages.success(request, "Signup successful!")
            return HttpResponseRedirect('/')
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'shop/signup.html', {'form': form})


def success_view(request):
    return render(request,'shop/success.html')
