from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Meal, Category, Order, OrderItem
from .cart import Cart
from .forms import CheckoutForm, ProfileForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .models import Order, OrderItem, UserProfile , Meal  # + Meal



def meal_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    meals = Meal.objects.filter(is_active=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        meals = meals.filter(category=category)

    return render(request, 'shop/meal_list.html', {
        'category': category,
        'categories': categories,
        'meals': meals,
    })


def meal_detail(request, slug):
    meal = get_object_or_404(Meal, slug=slug, is_active=True)
    return render(request, 'shop/meal_detail.html', {'meal': meal})


@require_POST
def cart_add(request, meal_id):
    cart = Cart(request)
    cart.add(meal_id=meal_id, quantity=1)
    return redirect('shop:cart_detail')


def cart_remove(request, meal_id):
    cart = Cart(request)
    cart.remove(meal_id)
    return redirect('shop:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})


@login_required(login_url='login')
def checkout(request):
    cart = Cart(request)
    if not list(cart):
        return redirect('shop:meal_list')

    # Toujours avoir un profil disponible
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Mettre à jour le profil
            profile.full_name = form.cleaned_data['customer_name']
            profile.phone = form.cleaned_data['phone']
            profile.address = form.cleaned_data['address']
            profile.save()

            # Créer la commande
            order = Order.objects.create(
                user=request.user,
                customer_name=profile.full_name,
                phone=profile.phone,
                address=profile.address,
                total=cart.get_total_price(),
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    meal=item['meal'],
                    quantity=item['quantity'],
                    unit_price=item['meal'].price
                )

            cart.clear()
            return render(request, 'shop/checkout_success.html', {'order': order})
    else:
        form = CheckoutForm(initial={
            'customer_name': profile.full_name,
            'phone': profile.phone,
            'address': profile.address,
        })

    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'form': form,
    })








def signup(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from .models import UserProfile
            UserProfile.objects.create(user=user)
            auth_login(request, user)
            return redirect(next_url)
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form, 'next': next_url})







@staff_member_required
def admin_dashboard(request):
    today = timezone.localdate()

    orders_today = Order.objects.filter(created_at__date=today)
    orders_count_today = orders_today.count()
    total_sales_today = orders_today.aggregate(total=Sum('total'))['total'] or 0

    pending_orders_count = Order.objects.filter(status='pending').count()

    top_meals = (
        OrderItem.objects
        .filter(order__created_at__date=today)
        .values('meal__name')
        .annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('unit_price')),
        )
        .order_by('-quantity_sold')[:5]
    )

    meals = Meal.objects.all().order_by('category__name', 'name')  # ← liste des plats

    context = {
        'today': today,
        'orders_count_today': orders_count_today,
        'total_sales_today': total_sales_today,
        'pending_orders_count': pending_orders_count,
        'top_meals': top_meals,
        'orders_today': orders_today,
        'meals': meals,  # ← on envoie au template
    }
    return render(request, 'admin/dashboard.html', context)





@staff_member_required
@require_POST
def mark_order_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'delivered'
    order.save()
    return redirect('admin_dashboard')



@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=profile)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'shop/profile.html', {
        'form': form,
        'orders': orders,
    })


