from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from sneakerweb import views
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core Pages
    path('', views.home, name='home'),
    path('index.html', views.home, name='index'),
    path('men.html', views.men, name='men'),
    path('women.html', views.women, name='women'),
    path('accessories.html', views.accessories, name='accessories'),
    path('contact.html', views.contact, name='contact'),
    path('contact/', views.contact, name='contact_page'),
    
    # Product Details
    path('product.html', views.product_detail, name='product'),
    path('product-detail.html', views.product_detail, name='product_detail'),
    path('product/<str:code>/', views.product_detail, name='product_by_code'),
    
    # Accounts & Customer Portal
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard.html', account_views.dashboard_view, name='dashboard_html'),
    path('dashboard/', account_views.dashboard_view, name='dashboard_page'),
    path('api/checkout/', account_views.api_checkout, name='root_api_checkout'),
    
    # Dynamic Products Database APIs & JS Sync
    path('api/products/', views.api_products_json, name='api_products_json'),
    path('api/products/data.js', views.dynamic_products_js, name='dynamic_products_js'),

    # Dynamic Admin-Created Category Pages (e.g. /kids.html, /running.html, /category/kids/)
    path('category/<slug:slug>/', views.category_view, name='category_page_slug'),
    path('<slug:slug>.html', views.category_view, name='category_page_html'),
]

# Serve static & media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
