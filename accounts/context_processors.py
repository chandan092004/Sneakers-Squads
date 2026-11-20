from .models import Category

def global_categories(request):
    """Make active categories available across all templates and navbar (excluding core static pages)"""
    try:
        nav_cats = Category.objects.filter(
            is_active=True,
            show_in_navbar=True
        ).exclude(
            slug__in=['men', 'women', 'accessories', 'unisex', 'home', 'contact']
        ).order_by('display_order', 'name')
    except Exception:
        nav_cats = []
    return {
        'nav_categories': nav_cats
    }
