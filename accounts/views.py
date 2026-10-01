import json
import uuid
import re
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Avg, Count, Q
from django.core.mail import send_mail
from django.conf import settings
try:
    import razorpay
except ImportError:
    razorpay = None
from .models import UserProfile, UserAddress, WishlistItem, PasswordResetToken, Order, OrderItem, Product, ProductReview



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

    # Dispatch Welcome Email to user
    welcome_subject = "Welcome to SNEAKERS SQUADS 👟 - You're officially a Squad Member!"
    welcome_message = f"""
Hi {display_name},

Welcome to SNEAKERS SQUADS! Your official squad membership is now active.

Here are your account details:
• Registered Email: {email}
• Username: {username}
• Member Perk: Use promo code 'SQUAD20' for flat 20% off on your first sneaker drop!

Explore 100% Deadstock Verified Footwear:
{request.build_absolute_uri('/')}

Keep Dropping Heat,
Team SNEAKER SQUAD 👟
"""

    welcome_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="background:#0b0d13; color:#ffffff; font-family:'Segoe UI', Arial, sans-serif; padding:30px 20px; margin:0;">
      <div style="max-width:520px; margin:0 auto; background:#141722; border:1px solid rgba(255,255,255,0.1); border-radius:18px; padding:36px 28px; text-align:center;">
        <div style="font-size:36px; margin-bottom:8px;">👟⚡</div>
        <h1 style="color:#ff5a1f; margin:0 0 8px; font-size:24px; font-weight:900; letter-spacing:1px;">SNEAKERS SQUADS</h1>
        <h2 style="color:#ffffff; margin:8px 0 16px; font-size:18px;">Welcome to the VIP Squad, {display_name}!</h2>
        <p style="color:#94a3b8; font-size:14px; line-height:1.5;">Your account is ready. You now have access to exclusive sneaker drops, real-time Blue Dart shipment tracking, and saved wishlist collections.</p>
        
        <div style="background:#0b0e14; border:2px dashed #ff5a1f; border-radius:14px; padding:18px; margin:22px 0; text-align:left;">
          <div style="color:#38bdf8; font-weight:800; font-size:12px; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">🎁 Exclusive Member Perk</div>
          <div style="color:#fff; font-size:14px; margin-bottom:4px;">Use Code: <strong style="color:#ff5a1f; font-size:16px; background:rgba(255,90,31,0.15); padding:2px 8px; border-radius:6px; letter-spacing:1px;">SQUAD20</strong></div>
          <div style="color:#94a3b8; font-size:12px;">Get 20% discount on your first pair of authentic deadstock kicks!</div>
        </div>

        <div style="margin:26px 0;">
          <a href="{request.build_absolute_uri('/')}" style="background:linear-gradient(135deg, #ff5a1f, #e04812); color:#ffffff; padding:14px 32px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:15px; display:inline-block; box-shadow:0 4px 15px rgba(255,90,31,0.4);">🔥 Explore Latest Drops Now</a>
        </div>
        
        <p style="color:#64748b; font-size:12px; margin-top:20px;">Need help or sizing advice? Reply to this email or visit our 24/7 support portal.</p>
      </div>
    </body>
    </html>
    """

    try:
        send_mail(
            welcome_subject,
            welcome_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=welcome_html,
            fail_silently=True,
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'message': f'Welcome to Sneaker Squad, {display_name}! 🎉 (Welcome Email Dispatched)',
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
# 5. FORGOT PASSWORD & MOBILE OTP RECOVERY FLOW
# ==========================================

def send_mobile_sms(phone, otp_code):
    """
    Dispatches real SMS to Indian Mobile Number via Fast2SMS / Twilio.
    Works with Indian 10-digit mobile numbers.
    """
    clean_phone = re.sub(r'[^0-9]', '', str(phone))
    if clean_phone.startswith('91') and len(clean_phone) > 10:
        clean_phone = clean_phone[2:]
    
    fast2sms_key = os.environ.get('FAST2SMS_API_KEY', '').strip()
    if fast2sms_key and len(clean_phone) == 10:
        try:
            import requests
            url = "https://www.fast2sms.com/dev/bulkV2"
            payload = {
                "variables_values": otp_code,
                "route": "otp",
                "numbers": clean_phone
            }
            headers = {
                'authorization': fast2sms_key,
                'Content-Type': "application/x-www-form-urlencoded",
                'Cache-Control': "no-cache"
            }
            requests.post(url, data=payload, headers=headers, timeout=5)
        except Exception:
            pass


@csrf_exempt
@require_POST
def api_forgot_password(request):
    """
    Handles Password Reset & OTP Dispatch via Mobile Phone Number or Email
    """
    data = get_request_data(request)
    identifier = data.get('identifier', data.get('email', data.get('phone', ''))).strip()

    if not identifier:
        return JsonResponse({'success': False, 'message': 'Please enter your registered Mobile Number or Email.'}, status=400)

    clean_digits = re.sub(r'[^0-9]', '', identifier)
    user = None
    target_phone = None
    target_email = None

    # 1. Search by Phone Number if digits entered
    if len(clean_digits) >= 10:
        last10 = clean_digits[-10:]
        profile_match = UserProfile.objects.filter(phone__icontains=last10).select_related('user').first()
        if profile_match and profile_match.user:
            user = profile_match.user
            target_phone = profile_match.phone or last10
            target_email = user.email

    # 2. Search by Email or Username
    if not user:
        user = User.objects.filter(email__iexact=identifier).first() or User.objects.filter(username__iexact=identifier).first()
        if user:
            target_email = user.email
            profile = get_user_profile(user)
            if profile and profile.phone:
                target_phone = profile.phone

    if not user:
        return JsonResponse({
            'success': False,
            'message': 'No registered account found with this Mobile Number or Email. Please check or sign up.'
        }, status=404)

    # Invalidate previous unused tokens for this user
    PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

    # Generate new token with 6-digit OTP
    token_obj = PasswordResetToken.objects.create(user=user)

    # Build reset URL for web view
    reset_url = request.build_absolute_uri(f"/accounts/reset-password/{token_obj.token}/")

    profile = get_user_profile(user)
    user_display = profile.get_display_name() if profile else (user.first_name or user.username)

    # 3. Send SMS if phone is available
    if target_phone:
        send_mobile_sms(target_phone, token_obj.otp_code)

    # 4. Send stylized Email if email is available
    if target_email:
        subject = "SNEAKER SQUAD - Reset Your Password & OTP"
        message = f"""
Hi {user_display},

Your Sneaker Squad 6-digit Verification Code is: {token_obj.otp_code}

Or click the link below to set a new password:
{reset_url}

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
            <h2 style="color:#ffffff; margin:10px 0 16px; font-size:20px;">Reset Your Password</h2>
            <p style="color:#94a3b8; font-size:15px;">Hi <strong>{user_display}</strong>, enter your verification code below to reset password:</p>
            <div style="background:#0b0e14; border:2px dashed #ff5a1f; border-radius:12px; padding:16px; margin:20px 0; color:#cbd5e1;">
              <span style="font-size:13px; text-transform:uppercase; color:#94a3b8; display:block; margin-bottom:4px;">Verification OTP Code</span>
              <strong style="color:#ff5a1f; font-size:28px; letter-spacing:6px; font-family:monospace;">{token_obj.otp_code}</strong>
            </div>
            <div style="margin:20px 0;">
              <a href="{reset_url}" style="background:#ff5a1f; color:#ffffff; padding:12px 26px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:14px; display:inline-block;">👉 Open Password Reset Page</a>
            </div>
          </div>
        </body>
        </html>
        """
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [target_email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception:
            pass

    return JsonResponse({
        'success': True,
        'message': f'6-Digit OTP code sent for {user_display}!',
        'identifier': identifier,
        'token': token_obj.token,
        'otp': token_obj.otp_code,
        'resetUrl': reset_url,
        'user_name': user_display
    })


@csrf_exempt
@require_POST
def api_verify_otp_and_reset_password(request):
    """
    Verifies 6-digit OTP and directly sets new password from Phone / Modal
    """
    data = get_request_data(request)
    identifier = data.get('identifier', '').strip()
    otp_code = data.get('otp', data.get('otp_code', '')).strip()
    new_password = data.get('new_password', '').strip()
    token_str = data.get('token', '').strip()

    if not otp_code or not new_password:
        return JsonResponse({'success': False, 'message': 'Please enter the 6-digit OTP and your new password.'}, status=400)

    if len(new_password) < 6:
        return JsonResponse({'success': False, 'message': 'New password must be at least 6 characters long.'}, status=400)

    token_obj = None

    # 1. Search by token string if passed
    if token_str:
        token_obj = PasswordResetToken.objects.filter(token=token_str, is_used=False).first()

    # 2. Search by OTP code and identifier if not matched
    if not token_obj and otp_code:
        token_obj = PasswordResetToken.objects.filter(otp_code=otp_code, is_used=False).order_by('-created_at').first()

    if not token_obj or not token_obj.is_valid():
        return JsonResponse({'success': False, 'message': 'Invalid or expired OTP code. Please request a new OTP.'}, status=400)

    # Update Password
    user = token_obj.user
    user.set_password(new_password)
    user.save()

    # Mark Token as Used
    token_obj.is_used = True
    token_obj.save()

    # Auto-login the user seamlessly
    login(request, user)

    return JsonResponse({
        'success': True,
        'message': 'Password reset successfully! You are now logged in. 🔥',
        'user': serialize_user(user)
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
# 6. ORDER, PAYMENT GATEWAY & INVOICE APIS
# ==========================================

def get_razorpay_client():
    """Initializes Razorpay client if valid API credentials are provided"""
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_squadsneakers'))
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', os.environ.get('RAZORPAY_KEY_SECRET', 'test_secret_squad2026'))
    if key_id and key_secret and not key_id.startswith('rzp_test_squadsneakers'):
        try:
            return razorpay.Client(auth=(key_id, key_secret)), key_id, key_secret
        except Exception:
            pass
    return None, key_id, key_secret


@require_POST
def api_create_razorpay_order(request):
    """
    Creates an official Razorpay Order ID for UPI/Cards/Netbanking checkout.
    Seamlessly works with both live Razorpay keys and instant test mode simulator.
    """
    data = get_request_data(request)
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    street_address = data.get('address', '').strip()
    city = data.get('city', '').strip()
    pincode = data.get('postal_code', data.get('pincode', '')).strip()
    total_amount = data.get('total_amount', 0)
    items_data = data.get('items', [])

    if not full_name or not phone or not street_address or not city:
        return JsonResponse({'status': 'error', 'message': 'Please provide all delivery details.'}, status=400)

    if not items_data or len(items_data) == 0:
        return JsonResponse({'status': 'error', 'message': 'Your cart is empty.'}, status=400)

    try:
        total_amount = float(total_amount)
    except (ValueError, TypeError):
        total_amount = 0.0

    amount_in_paise = int(round(total_amount * 100))
    user = request.user if request.user.is_authenticated else None

    # 1. Create DB Order in Pending state
    order = Order.objects.create(
        user=user,
        full_name=full_name,
        email=email or (user.email if user else ''),
        phone=phone,
        street_address=street_address,
        city=city,
        pincode=pincode,
        total_amount=total_amount,
        payment_method='UPI / Online (Razorpay)',
        payment_status='Pending',
        status='CONFIRMED',
    )

    # 2. Add OrderItems
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

    # 3. Create Gateway Order
    client, key_id, key_secret = get_razorpay_client()
    razorpay_order_id = None

    if client:
        try:
            rzp_order = client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f"rcpt_{order.order_id}",
                'payment_capture': 1
            })
            razorpay_order_id = rzp_order.get('id')
        except Exception as e:
            razorpay_order_id = f"order_test_{uuid.uuid4().hex[:14]}"
    else:
        # Test Mode Simulated Razorpay Order ID
        razorpay_order_id = f"order_test_{uuid.uuid4().hex[:14]}"

    order.razorpay_order_id = razorpay_order_id
    order.save()

    return JsonResponse({
        'status': 'success',
        'success': True,
        'razorpay_order_id': razorpay_order_id,
        'order_id': order.order_id,
        'amount': amount_in_paise,
        'currency': 'INR',
        'key_id': key_id,
        'customer_name': full_name,
        'customer_email': email or (user.email if user else ''),
        'customer_phone': phone,
        'invoice_url': f"/accounts/order/{order.order_id}/invoice/"
    })


@require_POST
def api_verify_payment(request):
    """
    Verifies Razorpay payment signature & confirms the order
    """
    data = get_request_data(request)
    order_id = data.get('order_id', '').strip()
    razorpay_order_id = data.get('razorpay_order_id', '').strip()
    razorpay_payment_id = data.get('razorpay_payment_id', '').strip()
    razorpay_signature = data.get('razorpay_signature', '').strip()

    order = None
    if order_id:
        order = Order.objects.filter(order_id=order_id).first()
    elif razorpay_order_id:
        order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()

    if not order:
        return JsonResponse({'status': 'error', 'message': 'Associated order not found.'}, status=404)

    client, key_id, key_secret = get_razorpay_client()
    
    # If live keys, perform cryptographic verification
    if client and razorpay_signature:
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id or order.razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            order.payment_status = 'Failed'
            order.save()
            return JsonResponse({'status': 'error', 'message': 'Payment signature verification failed.'}, status=400)

    # Mark as Paid & Confirmed
    order.payment_status = 'Paid'
    order.status = 'CONFIRMED'
    order.razorpay_payment_id = razorpay_payment_id or f"pay_test_{uuid.uuid4().hex[:12]}"
    if razorpay_signature:
        order.razorpay_signature = razorpay_signature
    order.save()

    return JsonResponse({
        'status': 'success',
        'success': True,
        'message': f'Payment verified! Order #{order.order_id} confirmed.',
        'order_id': order.order_id,
        'payment_id': order.razorpay_payment_id,
        'tracking_number': order.tracking_number,
        'courier': order.courier_partner,
        'estimated_delivery': order.estimated_delivery,
        'invoice_url': f"/accounts/order/{order.order_id}/invoice/"
    })


@require_POST
def api_checkout(request):
    """Standard / COD Checkout API"""
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
        payment_method='Cash On Delivery (COD)' if payment_method == 'COD' else payment_method,
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
        'estimated_delivery': order.estimated_delivery,
        'invoice_url': f"/accounts/order/{order.order_id}/invoice/"
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

    # Delete order completely so it disappears from tracking and invoice URL is wiped
    order.delete()
    
    # Return updated count
    if request.user.email:
        from django.db.models import Q
        remaining_count = Order.objects.filter(Q(user=request.user) | Q(email__iexact=request.user.email)).count()
    else:
        remaining_count = Order.objects.filter(user=request.user).count()

    return JsonResponse({
        'success': True,
        'message': f'Order #{order_id} has been cancelled and removed from your account.',
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

    # Delete order and all associated items & invoice from database
    order.delete()

    if request.user.email:
        from django.db.models import Q
        remaining_count = Order.objects.filter(Q(user=request.user) | Q(email__iexact=request.user.email)).count()
    else:
        remaining_count = Order.objects.filter(user=request.user).count()

    return JsonResponse({
        'success': True,
        'message': f'Order #{order_id} and its Tax Invoice have been completely deleted.',
        'ordersCount': remaining_count
    })


def invoice_view(request, order_id):
    """
    Renders official printable Tax Invoice / Bill for an order.
    Returns 404 if the order has been deleted by the user.
    """
    order = Order.objects.filter(order_id=order_id).prefetch_related('items').first()
    if not order:
        return HttpResponse(
            """
            <div style="font-family:sans-serif; text-align:center; padding:60px 20px; background:#0b0e14; color:#fff; min-height:100vh;">
                <h1 style="color:#ef4444; font-size:2rem; margin-bottom:12px;">📄 Invoice Not Found</h1>
                <p style="color:#94a3b8; font-size:1.1rem; max-width:500px; margin:0 auto 24px;">
                    This order or payment record does not exist or has been deleted from the database.
                </p>
                <a href="/accounts/dashboard.html" style="background:#ff5a1f; color:#fff; padding:12px 24px; border-radius:10px; text-decoration:none; font-weight:700;">
                    Return to Dashboard
                </a>
            </div>
            """,
            status=404
        )

    # Authorization Check (Only owner, email match, or staff can view)
    if request.user.is_authenticated:
        is_owner = (order.user == request.user) or (request.user.email and order.email.lower() == request.user.email.lower())
        if not is_owner and not request.user.is_staff and order.user is not None:
            return HttpResponse("<h3 style='text-align:center; padding:50px;'>Unauthorized to view this invoice.</h3>", status=403)

    tax = order.get_tax_breakup()
    return render(request, 'invoice.html', {'order': order, 'tax': tax})



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


# ==========================================
# 8. CUSTOMER SNEAKER REVIEWS & RATINGS APIS
# ==========================================

@csrf_exempt
@require_POST
def api_submit_review(request):
    """
    Submits a customer sneaker review with rating (1-5), comments, and optional sneaker photo.
    """
    # Parse POST parameters and uploaded photo
    product_code = request.POST.get('product_code', '').strip()
    rating = request.POST.get('rating', '5').strip()
    title = request.POST.get('title', '').strip()
    comment = request.POST.get('comment', '').strip()
    user_name = request.POST.get('user_name', '').strip()
    user_email = request.POST.get('user_email', '').strip()
    review_image = request.FILES.get('review_image', None)

    if not product_code:
        return JsonResponse({'success': False, 'message': 'Product identifier is required.'}, status=400)

    if not comment:
        return JsonResponse({'success': False, 'message': 'Please write your review comments.'}, status=400)

    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            rating_int = 5
    except (ValueError, TypeError):
        rating_int = 5

    user = request.user if request.user.is_authenticated else None

    if not user_name:
        if user:
            profile = get_user_profile(user)
            user_name = profile.get_display_name() if profile else user.username
        else:
            user_name = 'Verified Sneakerhead'

    if not user_email and user:
        user_email = user.email

    product = Product.objects.filter(code=product_code).first()

    # Create Review
    review = ProductReview.objects.create(
        product=product,
        product_code=product_code,
        user=user,
        user_name=user_name,
        user_email=user_email,
        rating=rating_int,
        title=title or ('Verified Drop Review 🔥' if rating_int >= 4 else 'Sneaker Review'),
        comment=comment,
        review_image=review_image,
        is_verified_buyer=True,
        is_approved=True
    )

    # Calculate updated overall rating & review count for the sneaker
    approved_reviews = ProductReview.objects.filter(product_code=product_code, is_approved=True)
    count = approved_reviews.count()
    avg_rating = round(approved_reviews.aggregate(Avg('rating'))['rating__avg'] or 5.0, 1)

    if product:
        product.rating = avg_rating
        product.reviews_count = count
        product.save()

    return JsonResponse({
        'success': True,
        'message': 'Thank you! Your squad review & photo have been published! 🔥',
        'review': review.to_dict(),
        'avgRating': avg_rating,
        'reviewsCount': count
    })


@require_GET
def api_get_reviews(request, product_code):
    """
    Returns all approved reviews, star rating statistics & breakdown for a sneaker
    """
    reviews = ProductReview.objects.filter(product_code=product_code, is_approved=True).order_by('-created_at')
    count = reviews.count()
    avg_rating = round(reviews.aggregate(Avg('rating'))['rating__avg'] or 5.0, 1) if count > 0 else 4.8

    # Calculate star distribution percentages
    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        distribution[r.rating] = distribution.get(r.rating, 0) + 1

    breakdown = {}
    for star in range(5, 0, -1):
        star_count = distribution[star]
        percentage = round((star_count / count * 100)) if count > 0 else (80 if star == 5 else (15 if star == 4 else 5 if star == 3 else 0))
        breakdown[star] = {
            'count': star_count,
            'percentage': percentage
        }

    return JsonResponse({
        'success': True,
        'productCode': product_code,
        'avgRating': avg_rating,
        'reviewsCount': count,
        'breakdown': breakdown,
        'reviews': [r.to_dict() for r in reviews]
    })

