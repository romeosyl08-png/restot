from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Meal, Category, Order, OrderItem
from .cart import Cart
from .forms import CheckoutForm, ProfileForm, SignupForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, UserProfile , Meal  # + Meal
from django.contrib.auth import login
from django.contrib.auth import logout

from django.shortcuts import redirect
from django.views.decorators.http import require_POST


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

    qty = int(request.POST.get("quantity", 1))
    qty = max(1, min(qty, 20))  # borne 1..20 (tu ajustes)

    cart.add(meal_id=meal_id, quantity=qty)
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
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # connexion directe après inscription
            return redirect("shop:meal_list")
    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {"form": form})



def logout_view(request):
    """
    Déconnecte l'utilisateur puis le renvoie vers la page du menu.
    """
    logout(request)
    return redirect('shop:meal_list')






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

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Meal, Order, OrderItem
from .forms import MealForm

@staff_member_required
def admin_meal_list(request):
    meals = Meal.objects.select_related("category").order_by("category__name", "name")
    return render(request, "admin/meals_list.html", {"meals": meals})

@staff_member_required
def admin_meal_add(request):
    if request.method == "POST":
        form = MealForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Plat ajouté.")
            return redirect("admin_meal_list")
    else:
        form = MealForm()
    return render(request, "admin/meal_form.html", {"form": form, "mode": "add"})

@staff_member_required
def admin_meal_edit(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    if request.method == "POST":
        form = MealForm(request.POST, request.FILES, instance=meal)
        if form.is_valid():
            form.save()
            messages.success(request, "Plat modifié.")
            return redirect("admin_meal_list")
    else:
        form = MealForm(instance=meal)
    return render(request, "admin/meal_form.html", {"form": form, "mode": "edit", "meal": meal})

@staff_member_required
def admin_meal_delete(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    if request.method == "POST":
        meal.delete()
        messages.success(request, "Plat supprimé.")
        return redirect("admin_meal_list")
    return render(request, "admin/meal_confirm_delete.html", {"meal": meal})







@staff_member_required
@require_POST
def mark_order_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'delivered'
    order.save()
    return redirect('admin_dashboard')


from django.contrib.auth import get_user_model
User = get_user_model()


@staff_member_required
def admin_user_list(request):
    users = (
        User.objects
        .all()
        .order_by("-date_joined")
    )
    return render(request, "admin/user_list.html", {
        "users": users,
    })

@staff_member_required
def admin_user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Si tu as un modèle Profile lié (OneToOne), récupère-le prudemment
    profile = getattr(user, "profile", None)

    orders = Order.objects.filter(user=user).order_by("-created_at")[:50]

    return render(request, "admin/user_detail.html", {
        "u": user,
        "profile": profile,
        "orders": orders,
    })




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


from django.conf import settings
from django.http import HttpResponse

def debug_storage(request):
    return HttpResponse(
        f"<h3>DEFAULT_FILE_STORAGE = {settings.DEFAULT_FILE_STORAGE}</h3>"
        f"<p>CLOUDINARY_URL = {repr(getattr(settings, 'CLOUDINARY_URL', None))}</p>"
    )
