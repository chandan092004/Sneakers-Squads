import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from accounts.models import Category, Product, ContactMessage

# 1. Home / Landing Page
def home(request):
    featured_kicks = Product.objects.filter(is_active=True, is_featured=True)[:8]
    trending_kicks = Product.objects.filter(is_active=True, is_trending=True)[:8]
    context = {
        'featured_kicks': featured_kicks,
        'trending_kicks': trending_kicks,
    }
    return render(request, 'index.html', context)

# 2. Men's Shoes Collection
def men(request):
    products = Product.objects.filter(gender__in=['men', 'unisex'], is_active=True)
    return render(request, 'men.html', {'products': products, 'products_count': products.count()})

# 3. Women's Shoes Collection
def women(request):
    products = Product.objects.filter(gender__in=['women', 'unisex'], is_active=True)
    return render(request, 'women.html', {'products': products, 'products_count': products.count()})

# 4. Accessories & Sneaker Care
def accessories(request):
    products = Product.objects.filter(gender='accessories', is_active=True)
    return render(request, 'accessories.html', {'products': products, 'products_count': products.count()})

# 5. Product Detail Page
def product_detail(request, code=None):
    product = None
    if code:
        product = Product.objects.filter(code=code, is_active=True).first()
    return render(request, 'product-detail.html', {'product': product})

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


