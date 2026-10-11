from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from sneakerweb import views
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Core Store Pages (Clean URLs & slash support)
    path('', views.home, name='home'),
    path('index', views.home, name='index'),
    path('index/', views.home),
    path('men', views.men, name='men'),
    path('men/', views.men),
    path('women', views.women, name='women'),
    path('women/', views.women),
    path('accessories', views.accessories, name='accessories'),
    path('accessories/', views.accessories),
    path('contact', views.contact, name='contact'),
    path('contact/', views.contact),
    
    # Backward compatibility with .html paths
    path('index.html', views.home),
    path('men.html', views.men),
    path('women.html', views.women),
    path('accessories.html', views.accessories),
    path('contact.html', views.contact),
    
    # Product Details (Clean URLs, .html compatibility, and slug/code routing)
    path('product-detail', views.product_detail, name='product_detail'),
    path('product-detail/', views.product_detail, name='product_detail_slash'),
    path('product-detail.html', views.product_detail, name='product_detail_html'),
    path('product', views.product_detail, name='product'),
    path('product/', views.product_detail, name='product_slash'),
    path('product.html', views.product_detail, name='product_html'),
    path('product/<str:code>/', views.product_detail, name='product_by_code'),
    path('product/<str:code>', views.product_detail, name='product_by_code_noslash'),
    path('product-detail/<str:code>/', views.product_detail, name='product_detail_by_code'),
    path('product-detail/<str:code>', views.product_detail, name='product_detail_by_code_noslash'),
    
    # Accounts & Customer Portal
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard', account_views.dashboard_view, name='dashboard'),
    path('dashboard/', account_views.dashboard_view, name='dashboard_slash'),
    path('dashboard.html', account_views.dashboard_view, name='dashboard_html'),
    path('accounts/dashboard', account_views.dashboard_view),
    path('accounts/dashboard.html', account_views.dashboard_view),
    path('reset-password/<str:token>/', account_views.reset_password_page_view, name='root_reset_password_page'),
    path('reset-password/<str:token>', account_views.reset_password_page_view),
    path('order/<str:order_id>/invoice/', account_views.invoice_view, name='root_order_invoice'),
    path('order/<str:order_id>/invoice', account_views.invoice_view),
    
    # Checkout & Payment APIs
    path('api/checkout/', account_views.api_checkout, name='root_api_checkout'),
    path('api/payment/create-order/', account_views.api_create_razorpay_order, name='root_api_create_razorpay_order'),
    path('api/payment/verify/', account_views.api_verify_payment, name='root_api_verify_payment'),
    path('api/reviews/submit/', account_views.api_submit_review, name='root_api_submit_review'),
    path('api/reviews/<str:product_code>/', account_views.api_get_reviews, name='root_api_get_reviews'),
    
    # Dynamic Products Database APIs & JS Sync
    path('api/products/', views.api_products_json, name='api_products_json'),
    path('api/products/data.js', views.dynamic_products_js, name='dynamic_products_js'),

    # Dynamic Category Pages (e.g. /category/kids/ or /kids)
    path('category/<slug:slug>/', views.category_view, name='category_page_slug'),
    path('<slug:slug>', views.category_view, name='category_page'),

    # PWA Manifest & Service Worker Root Routes
    path('manifest.json', views.pwa_manifest, name='pwa_manifest'),
    path('sw.js', views.pwa_service_worker, name='pwa_service_worker'),
]

# Serve static & media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
