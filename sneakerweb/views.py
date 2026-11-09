import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from accounts.models import Category, SubCategory, Product, ContactMessage

# 1. Home / Landing Page
def home(request):
    featured_kicks = Product.objects.filter(is_active=True, is_featured=True)[:8]
    trending_kicks = Product.objects.filter(is_active=True, is_trending=True)[:8]
    context = {
        'featured_kicks': featured_kicks,
        'trending_kicks': trending_kicks,
    }
    return render(request, 'index.html', context)

# 2. Men's Catalog Controller (Dynamic Subcategory Filtering & Distinct Queryset)
def men_view(request):
    """
    Men's Collection View:
    - Relational Category filtering (slug='men')
    - URL subcategory filtering (?type=shoes, ?type=apparel)
    - Enforces .distinct() to guarantee zero duplicate product cards
    """
    cat_obj = Category.objects.filter(slug='men').first()
    queryset = Product.objects.filter(is_active=True)
    if cat_obj:
        queryset = queryset.filter(Q(category=cat_obj) | Q(gender__in=['men', 'unisex'], category__isnull=True))
    else:
        queryset = queryset.filter(gender__in=['men', 'unisex'])

    # Subcategory Filter via URL param ?type=
    subcat_filter = request.GET.get('type', '').strip().lower()
    active_filter = 'all'
    if subcat_filter and subcat_filter != 'all':
        active_filter = subcat_filter
        queryset = queryset.filter(
            Q(subcategory__slug=subcat_filter) |
            Q(subcategory__name__iexact=subcat_filter) |
            Q(tag__icontains=subcat_filter)
        )

    products = queryset.distinct()
    subcategories = SubCategory.objects.filter(category=cat_obj) if cat_obj else []

    context = {
        'products': products,
        'products_count': products.count(),
        'page_title': "Men's Footwear & Streetwear",
        'active_filter': active_filter,
        'subcategories': subcategories,
    }
    return render(request, 'men.html', context)


# 3. Women's Catalog Controller (Dynamic Subcategory Filtering & Distinct Queryset)
def women_view(request):
    """
    Women's Collection View:
    - Relational Category filtering (slug='women')
    - URL subcategory filtering (?type=sneakers, ?type=heels)
    - Enforces .distinct() to guarantee zero duplicate product cards
    """
    cat_obj = Category.objects.filter(slug='women').first()
    queryset = Product.objects.filter(is_active=True)
    if cat_obj:
        queryset = queryset.filter(Q(category=cat_obj) | Q(gender__in=['women', 'unisex'], category__isnull=True))
    else:
        queryset = queryset.filter(gender__in=['women', 'unisex'])

    # Subcategory Filter via URL param ?type=
    subcat_filter = request.GET.get('type', '').strip().lower()
    active_filter = 'all'
    if subcat_filter and subcat_filter != 'all':
        active_filter = subcat_filter
        queryset = queryset.filter(
            Q(subcategory__slug=subcat_filter) |
            Q(subcategory__name__iexact=subcat_filter) |
            Q(tag__icontains=subcat_filter)
        )

    products = queryset.distinct()
    subcategories = SubCategory.objects.filter(category=cat_obj) if cat_obj else []

    context = {
        'products': products,
        'products_count': products.count(),
        'page_title': "Women's Designer Sneaker & Footwear Collection",
        'active_filter': active_filter,
        'subcategories': subcategories,
    }
    return render(request, 'women.html', context)


# 4. Accessories Catalog Controller (Dynamic Subcategory Filtering & Distinct Queryset)
def accessories_view(request):
    """
    Accessories Collection View:
    - Relational Category filtering (slug='accessories')
    - URL subcategory filtering (?type=watches, ?type=bags)
    - Enforces .distinct() to guarantee zero duplicate product cards
    """
    cat_obj = Category.objects.filter(slug='accessories').first()
    queryset = Product.objects.filter(is_active=True)
    if cat_obj:
        queryset = queryset.filter(category=cat_obj)
    else:
        queryset = queryset.filter(tag__in=['watches', 'bags', 'care', 'laces'])

    # Subcategory Filter via URL param ?type=
    subcat_filter = request.GET.get('type', '').strip().lower()
    active_filter = 'all'
    if subcat_filter and subcat_filter != 'all':
        active_filter = subcat_filter
        queryset = queryset.filter(
            Q(subcategory__slug=subcat_filter) |
            Q(subcategory__name__iexact=subcat_filter) |
            Q(tag__icontains=subcat_filter)
        )

    products = queryset.distinct()
    subcategories = SubCategory.objects.filter(category=cat_obj) if cat_obj else []

    context = {
        'products': products,
        'products_count': products.count(),
        'page_title': "Accessories, Timepieces & Carry Packs",
        'active_filter': active_filter,
        'subcategories': subcategories,
    }
    return render(request, 'accessories.html', context)


# Exact aliases for backward compatibility across all legacy routes
man = men_view
men = men_view
woman = women_view
women = women_view
accessory = accessories_view
accessories = accessories_view

# 5. Product Detail Page
def product_detail(request, code=None):
    product = None
    target_code = code or request.GET.get('id') or request.GET.get('code')
    if target_code:
        product = Product.objects.filter(code=target_code, is_active=True).first()
    return render(request, 'product-detail.html', {
        'product': product,
        'product_code': target_code or ''
    })

# 6. Contact & Customer Support Page
def contact(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json' or 'application/json' in request.META.get('HTTP_ACCEPT', '') or request.POST.get('ajax') == '1'
        
        # Support both form-data and json payload
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except Exception:
                data = {}
        else:
            data = request.POST

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        order_id = data.get('order_id', '').strip()
        issue_type = data.get('issue_type', 'order_status')
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        # Validation
        if not name or not email or not message:
            error_msg = "Please fill in all required fields (Name, Email, and Message)."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            return render(request, 'contact.html', {'error': error_msg, 'submitted_data': data})

        # Save to database
        contact_obj = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            order_id=order_id,
            issue_type=issue_type,
            subject=subject or f"{dict(ContactMessage.ISSUE_TYPE_CHOICES).get(issue_type, 'Inquiry')} - {name}",
            message=message,
            user=request.user if request.user.is_authenticated else None,
            status='NEW'
        )

        success_msg = f"Thank you, {name}! Your inquiry has been received (Ticket #{contact_obj.id}). Our support squad will review it and reply within 24 hours."
        
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': success_msg,
                'ticket_id': contact_obj.id
            })

        return render(request, 'contact.html', {'success': success_msg})

    # GET Request: Pre-fill user data if authenticated
    initial_data = {}
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        initial_data = {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': profile.phone if profile and profile.phone else ''
        }

    return render(request, 'contact.html', {'initial_data': initial_data})


# 7. Dynamic Category Page Handler (Auto-generates page for any admin-created category)
def category_view(request, slug):
    clean_slug = slug.lower().replace('.html', '').strip()
    category = get_object_or_404(Category, slug=clean_slug, is_active=True)
    
    # Query products assigned to this category or tagged with slug
    products = Product.objects.filter(category=category, is_active=True)
    if not products.exists():
        products = Product.objects.filter(tag__icontains=clean_slug, is_active=True)
    
    context = {
        'category': category,
        'products': products,
        'products_count': products.count(),
        'page_title': category.name,
    }
    return render(request, 'category-page.html', context)

# 8. Dynamic Products JSON & JavaScript Engine (Syncs DB products to live frontend)
def api_products_json(request):
    products = Product.objects.filter(is_active=True)
    data = {p.code: p.to_dict() for p in products}
    return JsonResponse(data)

def dynamic_products_js(request):
    products = Product.objects.filter(is_active=True)
    data = {p.code: p.to_dict() for p in products}
    js_content = f"window.PRODUCTS_DATA = Object.assign(window.PRODUCTS_DATA || {{}}, {json.dumps(data)});"
    return HttpResponse(js_content, content_type="application/javascript")


# 9. PWA Manifest & Service Worker Endpoints
def pwa_manifest(request):
    import os
    from django.conf import settings
    manifest_path = os.path.join(settings.STATICFILES_DIRS[0], 'manifest.json')
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type="application/manifest+json")
    return JsonResponse({"name": "SNEAKERS SQUAD", "display": "standalone"})


def pwa_service_worker(request):
    import os
    from django.conf import settings
    sw_path = os.path.join(settings.STATICFILES_DIRS[0], 'sw.js')
    if os.path.exists(sw_path):
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type="application/javascript")
    return HttpResponse("// sw.js empty", content_type="application/javascript")


