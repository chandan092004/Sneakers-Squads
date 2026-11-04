"""
Permanent Authentication & Admin Security Middleware for Sneakers Squad
Guarantees persistent user and admin sessions across all devices (Mobile phones, Tablets, Desktops, PWA)
by pairing Django 10-year session cookies with cryptographically signed permanent authentication tokens:
1. squad_admin_token: Dedicated secure token for verified staff & superuser admin accounts.
2. squad_auth_token: Universal token for persistent customer and member accounts.

Device Behavior:
- Any new device or browser requires username & password on first access.
- Once logged in, the admin or customer remains PERMANENTLY logged in on that system until explicit logout.
- Multi-device independent: Logging in on mobile does not disrupt desktop or tablet sessions.
- On explicit logout, tokens and session on that system are completely erased.
"""
import logging
import urllib.parse
from django.core import signing
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings

logger = logging.getLogger(__name__)

ADMIN_AUTH_SALT = 'squad_admin_permanent_salt_v2'
CUSTOMER_AUTH_SALT = 'squad_permanent_auth_token_salt'
PERMANENT_AUTH_MAX_AGE = 315360000  # 10 years (3650 days) in seconds


def generate_admin_token(user):
    """Generate a tamper-proof cryptographically signed token specifically for admin staff/superusers"""
    if not user or not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return ''
    payload = {
        'user_id': user.id,
        'username': user.username,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'role': 'admin'
    }
    return signing.dumps(payload, salt=ADMIN_AUTH_SALT)


def verify_admin_token(token):
    """Verifies the admin token and returns the corresponding active staff/superuser User, or None"""
    if not token or not isinstance(token, str):
        return None
    token = urllib.parse.unquote(token.strip().strip('"').strip("'"))
    if not token:
        return None
    try:
        payload = signing.loads(token, salt=ADMIN_AUTH_SALT, max_age=PERMANENT_AUTH_MAX_AGE)
        user_id = payload.get('user_id')
        if not user_id:
            return None
        user = User.objects.filter(id=user_id, is_active=True).first()
        if user and (user.is_staff or user.is_superuser):
            return user
    except (signing.BadSignature, signing.SignatureExpired):
        pass
    except Exception as e:
        logger.debug(f"Admin auth token verification error: {e}")
    return None


def generate_permanent_token(user):
    """Generate a tamper-proof cryptographically signed token for permanent customer/user authentication"""
    if not user or not user.is_authenticated:
        return ''
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email or ''
    }
    return signing.dumps(payload, salt=CUSTOMER_AUTH_SALT)


def verify_permanent_token(token):
    """Verifies the signed token and returns the corresponding active User instance, or None"""
    if not token or not isinstance(token, str):
        return None
    token = urllib.parse.unquote(token.strip().strip('"').strip("'"))
    if not token:
        return None
    try:
        payload = signing.loads(token, salt=CUSTOMER_AUTH_SALT, max_age=PERMANENT_AUTH_MAX_AGE)
        user_id = payload.get('user_id')
        if not user_id:
            return None
        user = User.objects.filter(id=user_id, is_active=True).first()
        if user:
            return user
    except (signing.BadSignature, signing.SignatureExpired):
        pass
    except Exception as e:
        logger.debug(f"Permanent auth token verification error: {e}")
    return None


class PermanentAuthMiddleware:
    """
    Middleware that ensures:
    1. Admin panel (/admin/) is strictly restricted to active staff/superuser administrators.
    2. Any device accessing the admin panel requires login on first visit.
    3. Once logged in, the session never auto-expires until explicit manual logout on that system.
    4. Explicit logout cleanly purges tokens on that device.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = (request.path_info or request.path or '').strip()
        is_admin_path = path.startswith('/admin')
        is_logout_request = (
            path in ('/admin/logout', '/admin/logout/', 
                     '/accounts/api/logout', '/accounts/api/logout/',
                     '/accounts/logout', '/accounts/logout/',
                     '/logout', '/logout/')
        )

        # ---------------------------------------------------------------------
        # 1. SESSION RESTORATION (Skip if this is an explicit logout action)
        # ---------------------------------------------------------------------
        if not is_logout_request:
            if is_admin_path:
                # ADMIN PORTAL ROUTING:
                # Check for verified permanent admin token
                admin_token = (
                    request.COOKIES.get('squad_admin_token') or 
                    request.META.get('HTTP_X_SQUAD_ADMIN_TOKEN') or
                    request.GET.get('admin_token')
                )
                verified_admin = verify_admin_token(admin_token) if admin_token else None

                if not verified_admin:
                    # Fallback check on squad_auth_token (if the user is staff/superuser)
                    general_token = (
                        request.COOKIES.get('squad_auth_token') or 
                        request.META.get('HTTP_X_SQUAD_AUTH_TOKEN') or
                        request.GET.get('auth_token') or
                        request.GET.get('squad_auth_token')
                    )
                    if general_token:
                        candidate = verify_permanent_token(general_token)
                        if candidate and candidate.is_active and (candidate.is_staff or candidate.is_superuser):
                            verified_admin = candidate

                # If we have a verified admin user:
                if verified_admin:
                    current_user = getattr(request, 'user', None)
                    # If current request user is unauthenticated OR is currently a non-staff customer,
                    # elevate session to the verified admin user for the admin portal!
                    if not current_user or not current_user.is_authenticated or not (current_user.is_staff or current_user.is_superuser):
                        try:
                            verified_admin.backend = 'django.contrib.auth.backends.ModelBackend'
                            login(request, verified_admin)
                            request.session.set_expiry(PERMANENT_AUTH_MAX_AGE)
                            request.session.modified = True
                        except Exception as e:
                            logger.debug(f"Admin auto-login error in middleware: {e}")

            else:
                # STOREFRONT ROUTING:
                # If unauthenticated, restore session from squad_auth_token or squad_admin_token
                current_user = getattr(request, 'user', None)
                if not current_user or not current_user.is_authenticated:
                    user_to_restore = None
                    general_token = (
                        request.COOKIES.get('squad_auth_token') or 
                        request.META.get('HTTP_X_SQUAD_AUTH_TOKEN') or
                        request.GET.get('auth_token') or
                        request.GET.get('squad_auth_token')
                    )
                    if general_token:
                        user_to_restore = verify_permanent_token(general_token)

                    if not user_to_restore:
                        admin_token = (
                            request.COOKIES.get('squad_admin_token') or
                            request.META.get('HTTP_X_SQUAD_ADMIN_TOKEN') or
                            request.GET.get('admin_token')
                        )
                        if admin_token:
                            user_to_restore = verify_admin_token(admin_token)

                    if user_to_restore and user_to_restore.is_active:
                        try:
                            user_to_restore.backend = 'django.contrib.auth.backends.ModelBackend'
                            login(request, user_to_restore)
                            request.session.set_expiry(PERMANENT_AUTH_MAX_AGE)
                            request.session.modified = True
                        except Exception as e:
                            logger.debug(f"Storefront auto-login error in middleware: {e}")

        # ---------------------------------------------------------------------
        # 2. PROCESS VIEW
        # ---------------------------------------------------------------------
        response = self.get_response(request)

        # ---------------------------------------------------------------------
        # 3. EXPLICIT LOGOUT CLEANUP
        # ---------------------------------------------------------------------
        if is_logout_request:
            # Delete permanent tokens and session cookies specifically on this device
            response.delete_cookie('squad_admin_token', path='/')
            response.delete_cookie('squad_auth_token', path='/')
            session_cookie = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
            response.delete_cookie(session_cookie, path='/')
            try:
                if hasattr(request, 'session'):
                    request.session.flush()
            except Exception:
                pass
            return response

        # ---------------------------------------------------------------------
        # 4. TOKEN MAINTENANCE FOR AUTHENTICATED USERS
        # ---------------------------------------------------------------------
        if getattr(request, 'user', None) and request.user.is_authenticated:
            # Keep session expiry permanently set to 10 years
            try:
                if hasattr(request, 'session'):
                    request.session.set_expiry(PERMANENT_AUTH_MAX_AGE)
            except Exception:
                pass

            # Maintain & renew customer permanent token cookie (10 years sliding window)
            try:
                auth_tok = request.COOKIES.get('squad_auth_token')
                verified_cust = verify_permanent_token(auth_tok) if auth_tok else None
                new_cust_tok = auth_tok if (verified_cust and verified_cust.id == request.user.id) else generate_permanent_token(request.user)
                response.set_cookie(
                    'squad_auth_token',
                    new_cust_tok,
                    max_age=PERMANENT_AUTH_MAX_AGE,
                    path='/',
                    samesite='Lax',
                    httponly=False,
                    secure=False
                )
            except Exception as e:
                logger.debug(f"Error setting squad_auth_token on response: {e}")

            # Maintain & renew staff admin permanent token cookie (10 years)
            if request.user.is_staff or request.user.is_superuser:
                try:
                    admin_tok = request.COOKIES.get('squad_admin_token')
                    verified = verify_admin_token(admin_tok) if admin_tok else None
                    new_admin_tok = admin_tok if (verified and verified.id == request.user.id) else generate_admin_token(request.user)
                    response.set_cookie(
                        'squad_admin_token',
                        new_admin_tok,
                        max_age=PERMANENT_AUTH_MAX_AGE,
                        path='/',
                        samesite='Lax',
                        httponly=True,
                        secure=False
                    )
                except Exception as e:
                    logger.debug(f"Error setting squad_admin_token on response: {e}")

        return response
