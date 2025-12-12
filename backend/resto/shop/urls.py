from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.meal_list, name='meal_list'),
    path('category/<slug:category_slug>/', views.meal_list, name='meal_list_by_category'),
    path('meal/<slug:slug>/', views.meal_detail, name='meal_detail'),

    path('cart/add/<int:meal_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:meal_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),

    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.profile, name='profile'),

    # === Debug Storage ===
    path('debug/storage/', views.debug_storage, name='debug_storage'),
]
