from .models import Category

def global_categories(request):
    """Make active categories available across all templates and navbar"""
    try:
        nav_cats = Category.objects.filter(is_active=True, show_in_navbar=True).order_by('display_order', 'name')
    except Exception:
        nav_cats = []
    return {
        'nav_categories': nav_cats
    }
