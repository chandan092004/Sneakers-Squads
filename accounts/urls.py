from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Page Views
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard.html', views.dashboard_view, name='dashboard_html'),
    path('reset-password/<str:token>/', views.reset_password_page_view, name='reset_password_page'),
    
    # Auth APIs (AJAX)
    path('api/register/', views.api_register, name='api_register'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/user-state/', views.api_user_state, name='api_user_state'),
    
    # Wishlist APIs
    path('api/wishlist/toggle/', views.api_wishlist_toggle, name='api_wishlist_toggle'),
    path('api/wishlist/list/', views.api_wishlist_list, name='api_wishlist_list'),
    
    # Address Book APIs
    path('api/address/save/', views.api_address_save, name='api_address_save'),
    path('api/address/<int:address_id>/delete/', views.api_address_delete, name='api_address_delete'),
    path('api/address/<int:address_id>/set-default/', views.api_address_set_default, name='api_address_set_default'),
    
    # Profile & Password APIs
    path('api/profile/update/', views.api_profile_update, name='api_profile_update'),
    path('api/change-password/', views.api_change_password, name='api_change_password'),
    path('api/forgot-password/', views.api_forgot_password, name='api_forgot_password'),
    path('api/verify-otp-reset/', views.api_verify_otp_and_reset_password, name='api_verify_otp_reset'),
    path('api/reset-password/submit/', views.api_reset_password_submit, name='api_reset_password_submit'),


    # Checkout & Orders APIs
    path('api/checkout/', views.api_checkout, name='api_checkout'),
    path('api/payment/create-order/', views.api_create_razorpay_order, name='api_create_razorpay_order'),
    path('api/payment/verify/', views.api_verify_payment, name='api_verify_payment'),
    path('order/<str:order_id>/invoice/', views.invoice_view, name='order_invoice'),
    path('api/order/<str:order_id>/cancel/', views.api_cancel_order, name='api_cancel_order'),
    path('api/order/<str:order_id>/delete/', views.api_delete_order, name='api_delete_order'),

    # Product Reviews & Ratings APIs
    path('api/reviews/submit/', views.api_submit_review, name='api_submit_review'),
    path('api/reviews/<str:product_code>/', views.api_get_reviews, name='api_get_reviews'),


]
