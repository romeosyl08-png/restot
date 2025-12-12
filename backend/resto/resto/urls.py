from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from shop import views as shop_views
from django.conf.urls.static import static


urlpatterns = [
    # Dashboard + action pour marquer livré
    path('admin/dashboard/', shop_views.admin_dashboard, name='admin_dashboard'),
    path(
        'admin/order/<int:order_id>/delivered/',
        shop_views.mark_order_delivered,
        name='mark_order_delivered',
    ),
    path('admin/meals/', shop_views.admin_meal_list, name='admin_meal_list'),
    path('admin/meals/add/', shop_views.admin_meal_add, name='admin_meal_add'),
    path('admin/meals/<int:meal_id>/edit/', shop_views.admin_meal_edit, name='admin_meal_edit'),
    path('admin/meals/<int:meal_id>/delete/', shop_views.admin_meal_delete, name='admin_meal_delete'),

    path('admin/users/<int:user_id>/', shop_views.admin_user_detail, name='admin_user_detail'),

    # Admin Django classique
    path('admin/', admin.site.urls),

    # Auth utilisateur (login / logout / password reset)
    path('accounts/signup/', shop_views.signup, name='signup'),

    path('logout/', shop_views.logout_view, name='logout_custom'),
    
    path('accounts/', include('django.contrib.auth.urls')),

    # Site public (toutes les URLs de l’app shop)
    path('', include('shop.urls', namespace='shop')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
