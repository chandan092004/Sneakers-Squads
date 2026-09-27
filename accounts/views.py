import json
import uuid
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile, UserAddress, WishlistItem, PasswordResetToken, Order, OrderItem

def get_request_data(request):
    """Helper to parse JSON or form data cleanly"""
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8'))
        except Exception:
            return {}
    return request.POST


def get_user_profile(user):
    if not user or not user.is_authenticated and not getattr(user, 'id', None):
        return None
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def serialize_user(user):
    profile = get_user_profile(user)
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'displayName': profile.get_display_name() if profile else user.username,
        'phone': profile.phone if profile else '',
        'avatar': profile.get_avatar_url() if profile else '',
        'gender': profile.gender if profile else '',
        'city': profile.city if profile else '',
        'state': profile.state if profile else '',
        'isSuperuser': user.is_superuser
    }


# ==========================================
# 1. AUTHENTICATION APIS (AJAX)
# ==========================================

@require_POST
def api_register(request):
    data = get_request_data(request)
    email = data.get('email', '').strip().lower()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()
    username = data.get('username', '').strip()

    if not email or not password:
        return JsonResponse({'success': False, 'message': 'Email and password are required.'}, status=400)

    # Basic email format regex
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return JsonResponse({'success': False, 'message': 'Please enter a valid email address.'}, status=400)

    if len(password) < 6:
        return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters long.'}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': 'An account with this email already exists. Please login.'}, status=400)

    # Generate unique username if not provided
    if not username:
        base_username = email.split('@')[0]
        base_username = re.sub(r'[^a-zA-Z0-9_]', '', base_username)
        if not base_username:
            base_username = 'sneakerhead'
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
    elif User.objects.filter(username=username).exists():
        return JsonResponse({'success': False, 'message': 'Username is already taken. Please choose another.'}, status=400)

    # Parse first and last name
    first_name = full_name
    last_name = ''
    if ' ' in full_name:
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1]

    # Create User
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

    # Update Profile
    profile = get_user_profile(user)
    if phone and profile:
        profile.phone = phone
        profile.save()

    # Auto-login the newly registered user
    login(request, user)

    # Fetch initial wishlist
    wishlist_ids = list(WishlistItem.objects.filter(user=user).values_list('product_id', flat=True))

    display_name = profile.get_display_name() if profile else user.username
    return JsonResponse({
        'success': True,
        'message': f'Welcome to Sneaker Squad, {display_name}! 🎉',
        'user': serialize_user(user),
        'wishlist': wishlist_ids
    })


@require_POST
def api_login(request):
    data = get_request_data(request)
    username_or_email = data.get('username', '') or data.get('email', '')
    username_or_email = username_or_email.strip()
    password = data.get('password', '').strip()

    if not username_or_email or not password:
        return JsonResponse({'success': False, 'message': 'Username/Email and password are required.'}, status=400)

    # Support login with either Email OR Username
    user_obj = None
    if '@' in username_or_email:
        user_obj = User.objects.filter(email__iexact=username_or_email).first()
        if user_obj:
            username = user_obj.username
        else:
            username = username_or_email
    else:
        username = username_or_email

    user = authenticate(request, username=username, password=password)

    if user is not None:
        if not user.is_active:
            return JsonResponse({'success': False, 'message': 'Your account is disabled.'}, status=403)
        
        login(request, user)
        wishlist_ids = list(WishlistItem.objects.filter(user=user).values_list('product_id', flat=True))
        profile = get_user_profile(user)
        display_name = profile.get_display_name() if profile else user.username

        return JsonResponse({
            'success': True,
            'message': f'Welcome back, {display_name}! 🔥',
            'user': serialize_user(user),
            'wishlist': wishlist_ids
        })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid email/username or password. Please try again.'}, status=401)


@require_POST
def api_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out successfully.'})


@require_GET
def api_user_state(request):
    """Provides instant hydration data for frontend header and wishlist sync"""
    if request.user.is_authenticated:
        wishlist_ids = list(WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True))
        return JsonResponse({
            'isAuthenticated': True,
            'user': serialize_user(request.user),
            'wishlist': wishlist_ids,
            'wishlistCount': len(wishlist_ids)
        })
    return JsonResponse({
        'isAuthenticated': False,
        'user': None,
        'wishlist': [],
        'wishlistCount': 0
    })


# ==========================================
# 2. WISHLIST APIS
# ==========================================

@require_POST
def api_wishlist_toggle(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'requireLogin': True,
            'message': 'Please login to save items to your permanent squad wishlist!'
        }, status=401)

    data = get_request_data(request)
    product_id = data.get('product_id', '').strip().lower()
    product_name = data.get('product_name', '')
    product_price = data.get('product_price')
    product_image = data.get('product_image', '')

    if not product_id:
        return JsonResponse({'success': False, 'message': 'Product ID is required'}, status=400)

    existing = WishlistItem.objects.filter(user=request.user, product_id=product_id).first()

    if existing:
        existing.delete()
        action = 'removed'
        msg = f'Removed from your wishlist.'
    else:
        WishlistItem.objects.create(
            user=request.user,
            product_id=product_id,
            product_name=product_name,
            product_price=product_price if product_price else None,
            product_image=product_image
        )
        action = 'added'
        msg = f'Added to your squad wishlist! ❤️'

    wishlist_ids = list(WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True))

    return JsonResponse({
        'success': True,
        'action': action,
        'message': msg,
        'wishlist': wishlist_ids,
        'wishlistCount': len(wishlist_ids)
    })


@require_GET
@login_required
def api_wishlist_list(request):
    items = WishlistItem.objects.filter(user=request.user)
    data = []
    for item in items:
        data.append({
            'id': item.id,
            'productId': item.product_id,
            'name': item.product_name or item.product_id,
            'price': float(item.product_price) if item.product_price else 0.0,
            'image': item.product_image or '/static/img/shoe-1.jpg',
            'addedAt': item.added_at.strftime('%d %b %Y')
        })
    return JsonResponse({'success': True, 'items': data, 'count': len(data)})


# ==========================================
# 3. ADDRESS BOOK APIS
# ==========================================

@require_POST
@login_required
def api_address_save(request):
    data = get_request_data(request)
    address_id = data.get('id')
    address_type = data.get('address_type', 'home')
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    street_address = data.get('street_address', '').strip()
    apartment_suite = data.get('apartment_suite', '').strip()
    city = data.get('city', '').strip()
    state = data.get('state', '').strip()
    pincode = data.get('pincode', '').strip()
    is_default = bool(data.get('is_default', False))

    if not full_name or not phone or not street_address or not city or not pincode:
        return JsonResponse({'success': False, 'message': 'Please fill all mandatory address fields.'}, status=400)

    if address_id:
        # Update existing
        addr = get_object_or_404(UserAddress, id=address_id, user=request.user)
        addr.address_type = address_type
        addr.full_name = full_name
        addr.phone = phone
        addr.street_address = street_address
        addr.apartment_suite = apartment_suite
        addr.city = city
        addr.state = state
        addr.pincode = pincode
        addr.is_default = is_default
        addr.save()
        msg = 'Address updated successfully!'
    else:
        # Create new
        addr = UserAddress.objects.create(
            user=request.user,
            address_type=address_type,
            full_name=full_name,
            phone=phone,
            street_address=street_address,
            apartment_suite=apartment_suite,
            city=city,
            state=state,
            pincode=pincode,
            is_default=is_default
        )
        msg = 'New address saved to your address book!'

    # Return all updated addresses
    addresses = get_serialized_addresses(request.user)
    return JsonResponse({'success': True, 'message': msg, 'addresses': addresses})


@require_POST
@login_required
def api_address_delete(request, address_id):
    addr = get_object_or_404(UserAddress, id=address_id, user=request.user)
    addr.delete()
    addresses = get_serialized_addresses(request.user)
    return JsonResponse({'success': True, 'message': 'Address deleted.', 'addresses': addresses})


@require_POST
@login_required
def api_address_set_default(request, address_id):
    addr = get_object_or_404(UserAddress, id=address_id, user=request.user)
    addr.is_default = True
    addr.save()
    addresses = get_serialized_addresses(request.user)
    return JsonResponse({'success': True, 'message': 'Default address updated.', 'addresses': addresses})


def get_serialized_addresses(user):
    addrs = UserAddress.objects.filter(user=user)
    result = []
    for a in addrs:
        result.append({
            'id': a.id,
            'addressType': a.address_type,
            'fullName': a.full_name,
            'phone': a.phone,
            'streetAddress': a.street_address,
            'apartmentSuite': a.apartment_suite,
            'city': a.city,
            'state': a.state,
            'pincode': a.pincode,
            'isDefault': a.is_default
        })
    return result


# ==========================================
# 4. PROFILE UPDATE & SECURITY APIS
# ==========================================

@require_POST
@login_required
def api_profile_update(request):
    data = get_request_data(request)
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    phone = data.get('phone', '').strip()
    gender = data.get('gender', '').strip()
    city = data.get('city', '').strip()
    state = data.get('state', '').strip()

    user = request.user
    if first_name:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    user.save()

    profile = user.profile
    if phone:
        profile.phone = phone
    if gender:
        profile.gender = gender
    if city:
        profile.city = city
    if state:
        profile.state = state

    # Check for avatar file upload
    if 'avatar' in request.FILES:
        profile.avatar = request.FILES['avatar']

    profile.save()

    return JsonResponse({
        'success': True,
        'message': 'Profile details updated successfully! ✨',
        'user': serialize_user(user)
    })


@require_POST
@login_required
def api_change_password(request):
    data = get_request_data(request)
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()

    if not old_password or not new_password:
        return JsonResponse({'success': False, 'message': 'Both old and new passwords are required.'}, status=400)

    if not request.user.check_password(old_password):
        return JsonResponse({'success': False, 'message': 'Current password is incorrect.'}, status=400)

    if len(new_password) < 6:
        return JsonResponse({'success': False, 'message': 'New password must be at least 6 characters long.'}, status=400)

    request.user.set_password(new_password)
    request.user.save()
    # Re-authenticate session so user stays logged in
    login(request, request.user)

    return JsonResponse({'success': True, 'message': 'Password changed successfully!'})


# ==========================================
# 5. FORGOT PASSWORD & RECOVERY FLOW
# ==========================================

@csrf_exempt
@require_POST
def api_forgot_password(request):
    data = get_request_data(request)
    email = data.get('email', '').strip().lower()

    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required.'}, status=400)

    user = User.objects.filter(email=email).first()

    if not user:
        # Security best practice: don't reveal if user exists or not, but return success
        return JsonResponse({
            'success': True,
            'message': 'If this email is registered with Sneaker Squad, password reset instructions have been sent!'
        })

    # Invalidate previous unused tokens
    PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

    # Generate new token
    token_obj = PasswordResetToken.objects.create(user=user)

    # Build reset URL
    reset_url = request.build_absolute_uri(f"/accounts/reset-password/{token_obj.token}/")

    profile = get_user_profile(user)
    user_display = profile.get_display_name() if profile else (user.first_name or user.username)

    # Send stylized email (outputs to console in dev mode or Gmail SMTP if configured)
    subject = "SNEAKER SQUAD - Reset Your Master Password"
    message = f"""
Hi {user_display},

We received a request to reset your password for your Sneaker Squad account.

Click the link below to set a new password:
{reset_url}

Your 6-digit Verification Code: {token_obj.otp_code}

This link is valid for 24 hours. If you did not request this, please ignore this email.

Keep Dropping Heat,
Team SNEAKER SQUAD 👟
"""

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="background:#0b0d13; color:#ffffff; font-family:'Segoe UI', Arial, sans-serif; padding:30px 20px; margin:0;">
      <div style="max-width:500px; margin:0 auto; background:#141722; border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:36px 28px; text-align:center;">
        <h1 style="color:#ff5a1f; margin:0 0 10px; font-size:24px; font-weight:900; letter-spacing:1px;">SNEAKER SQUAD 👟</h1>
        <h2 style="color:#ffffff; margin:10px 0 16px; font-size:20px;">Reset Your Master Password</h2>
        <p style="color:#94a3b8; font-size:15px; line-height:1.5;">Hi <strong>{user_display}</strong>,<br>We received a request to reset the password for your Sneaker Squad account.</p>
        <div style="margin:26px 0;">
          <a href="{reset_url}" style="background:#ff5a1f; color:#ffffff; padding:14px 30px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:15px; display:inline-block;">👉 Reset Password Now</a>
        </div>
        <div style="background:#0b0e14; border:1px dashed rgba(255,90,31,0.4); border-radius:10px; padding:12px; margin:20px 0; color:#cbd5e1; font-size:14px;">
          Verification OTP: <strong style="color:#ff5a1f; font-size:18px; letter-spacing:3px;">{token_obj.otp_code}</strong>
        </div>
        <p style="color:#64748b; font-size:12px; margin-top:24px;">This link is valid for 24 hours. If you did not request this, please ignore this email.</p>
      </div>
    </body>
    </html>
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=True,
    )

    return JsonResponse({
        'success': True,
        'message': f'Password reset link and verification code sent to {email}!',
        'resetUrl': reset_url,
        'otp': token_obj.otp_code
    })


@csrf_exempt
@require_POST
def api_reset_password_submit(request):
    data = get_request_data(request)
    token_str = data.get('token', '').strip()
    new_password = data.get('new_password', '').strip()

    if not token_str or not new_password:
        return JsonResponse({'success': False, 'message': 'Token and new password are required.'}, status=400)

    token_obj = PasswordResetToken.objects.filter(token=token_str).first()

    if not token_obj or not token_obj.is_valid():
        return JsonResponse({'success': False, 'message': 'This reset link has expired or has already been used.'}, status=400)

    if len(new_password) < 6:
        return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters long.'}, status=400)

    user = token_obj.user
    user.set_password(new_password)
    user.save()

    token_obj.is_used = True
    token_obj.save()

    # Auto-login the user with new credentials
    login(request, user)

    return JsonResponse({
        'success': True,
        'message': 'Password reset successfully! You are now logged in. 🔥',
        'user': serialize_user(user)
    })


# ==========================================
# 6. ORDER & CHECKOUT APIS
# ==========================================

@require_POST
def api_checkout(request):
    data = get_request_data(request)
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    street_address = data.get('address', '').strip()
    city = data.get('city', '').strip()
    pincode = data.get('postal_code', data.get('pincode', '')).strip()
    payment_method = data.get('payment_method', 'COD')
    total_amount = data.get('total_amount', 0)
    items_data = data.get('items', [])

    if not full_name or not phone or not street_address or not city:
        return JsonResponse({'status': 'error', 'message': 'Please provide all delivery details.'}, status=400)

    if not items_data or len(items_data) == 0:
        return JsonResponse({'status': 'error', 'message': 'Your cart is empty.'}, status=400)

    user = request.user if request.user.is_authenticated else None

    try:
        total_amount = float(total_amount)
    except (ValueError, TypeError):
        total_amount = 0.0

    order = Order.objects.create(
        user=user,
        full_name=full_name,
        email=email or (user.email if user else ''),
        phone=phone,
        street_address=street_address,
        city=city,
        pincode=pincode,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status='Paid' if payment_method == 'UPI' else 'Pending',
        status='CONFIRMED',
    )

    for it in items_data:
        OrderItem.objects.create(
            order=order,
            product_id=it.get('id', 'item'),
            product_name=it.get('name', it.get('title', 'Sneaker')),
            product_price=float(it.get('price', 0)),
            quantity=int(it.get('quantity', it.get('qty', 1))),
            product_image=it.get('image', ''),
            size=it.get('size', 'UK 8'),
            color=it.get('color', '')
        )

    return JsonResponse({
        'status': 'success',
        'success': True,
        'message': f'Order #{order.order_id} placed successfully!',
        'order_id': order.order_id,
        'tracking_number': order.tracking_number,
        'courier': order.courier_partner,
        'estimated_delivery': order.estimated_delivery
    })


@require_POST
def api_cancel_order(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=401)
    
    order = Order.objects.filter(order_id=order_id).first()
    if not order:
        return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)

    # Allow if matched by user or user email
    is_owner = (order.user == request.user) or (request.user.email and order.email.lower() == request.user.email.lower())
    if not is_owner and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Unauthorized.'}, status=403)

    if order.status in ['SHIPPED', 'OUT_FOR_DELIVERY', 'DELIVERED']:
        return JsonResponse({'success': False, 'message': 'Cannot cancel order once it is shipped or in transit.'}, status=400)

    # Delete order completely on cancellation so it disappears from tracking
    order.delete()
    
    # Return updated count
    if request.user.email:
        from django.db.models import Q
        remaining_count = Order.objects.filter(Q(user=request.user) | Q(email__iexact=request.user.email)).count()
    else:
        remaining_count = Order.objects.filter(user=request.user).count()

    return JsonResponse({
        'success': True,
        'message': f'Order #{order_id} has been cancelled and removed from your tracking list.',
        'ordersCount': remaining_count
    })


@require_POST
def api_delete_order(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=401)
    
    order = Order.objects.filter(order_id=order_id).first()
    if not order:
        return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)

    is_owner = (order.user == request.user) or (request.user.email and order.email.lower() == request.user.email.lower())
    if not is_owner and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Unauthorized.'}, status=403)

    order.delete()

    if request.user.email:
        from django.db.models import Q
        remaining_count = Order.objects.filter(Q(user=request.user) | Q(email__iexact=request.user.email)).count()
    else:
        remaining_count = Order.objects.filter(user=request.user).count()

    return JsonResponse({
        'success': True,
        'message': f'Order #{order_id} removed.',
        'ordersCount': remaining_count
    })


# ==========================================
# 7. HTML PAGE VIEWS (Dashboard & Reset Page)
# ==========================================

@login_required(login_url='/')
def dashboard_view(request):
    user = request.user
    profile = get_user_profile(user)
    addresses = UserAddress.objects.filter(user=user)
    wishlist_items = WishlistItem.objects.filter(user=user)
    
    if user.email:
        from django.db.models import Q
        orders = Order.objects.filter(Q(user=user) | Q(email__iexact=user.email)).prefetch_related('items').distinct().order_by('-created_at')
    else:
        orders = Order.objects.filter(user=user).prefetch_related('items').order_by('-created_at')

    context = {
        'user': user,
        'profile': profile,
        'addresses': addresses,
        'wishlist_items': wishlist_items,
        'orders': orders,
        'wishlist_count': wishlist_items.count(),
        'addresses_count': addresses.count(),
        'orders_count': orders.count()
    }
    return render(request, 'dashboard.html', context)


def reset_password_page_view(request, token):
    token_obj = PasswordResetToken.objects.filter(token=token).first()
    is_valid = token_obj.is_valid() if token_obj else False

    user_name = ''
    if token_obj and is_valid:
        profile = get_user_profile(token_obj.user)
        user_name = profile.get_display_name() if profile else (token_obj.user.first_name or token_obj.user.username)

    context = {
        'token': token,
        'is_valid': is_valid,
        'user_name': user_name
    }
    return render(request, 'reset-password.html', context)
