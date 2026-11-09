from django.core.management.base import BaseCommand
from accounts.models import Product

class Command(BaseCommand):
    help = "Validates that every product has a valid category ('sneaker' or 'accessory') and valid gender ('men', 'women', 'unisex')."

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix wrong or missing category and gender fields based on product title and tags.',
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        self.stdout.write(self.style.MIGRATE_HEADING("=== SNEAKER SQUAD: PRODUCT DATA INTEGRITY CHECK ==="))
        
        products = Product.objects.all()
        invalid_products = []
        
        valid_categories = ['sneaker', 'accessory']
        valid_genders = ['men', 'women', 'unisex']
        
        accessory_keywords = [
            'lace', 'laces', 'kit', 'care', 'brush', 'shield', 'repellent',
            'pen', 'duffel', 'booties', 'dryer', 'cleaner', 'foam', 'whitener',
            'display', 'sock', 'socks', 'insole', 'insoles', 'shoe bag'
        ]

        for p in products:
            issues = []
            
            # Check Category
            if not p.category or p.category not in valid_categories:
                issues.append(f"Invalid category: '{p.category}' (Must be 'sneaker' or 'accessory')")
                
            # Check Gender
            if not p.gender or p.gender not in valid_genders:
                issues.append(f"Invalid gender: '{p.gender}' (Must be 'men', 'women', or 'unisex')")
                
            # Check Accessory Consistency
            is_acc_name = any(k in p.name.lower() or k in (p.tag or '').lower() for k in accessory_keywords)
            if is_acc_name and p.category != 'accessory':
                issues.append("Product appears to be an accessory but is categorized as sneaker")
            elif not is_acc_name and p.category == 'accessory':
                issues.append("Product appears to be a sneaker but is categorized as accessory")
                
            # Check Image
            if not p.image and not p.main_image:
                issues.append("Missing product image path")

            if issues:
                invalid_products.append((p, issues))
                if fix_mode:
                    if is_acc_name:
                        p.category = 'accessory'
                        p.gender = 'unisex'
                    else:
                        p.category = 'sneaker'
                        if p.gender not in ['men', 'women', 'unisex']:
                            p.gender = 'unisex' if 'unisex' in (p.tag or '').lower() else 'men'
                    if not p.image:
                        p.image = p.main_image or '/static/img/shoe-1.jpg'
                    p.save()

        if not invalid_products:
            self.stdout.write(self.style.SUCCESS(f"✔ All {products.count()} products have 100% valid category and gender! No issues found."))
        else:
            if fix_mode:
                self.stdout.write(self.style.SUCCESS(f"✔ Successfully auto-fixed {len(invalid_products)} products!"))
            else:
                self.stdout.write(self.style.WARNING(f"Found {len(invalid_products)} products with wrong or missing category/gender data:"))
                for p, issues in invalid_products:
                    self.stdout.write(f"- [ID: {p.id}] {p.name} (Cat: '{p.category}', Gen: '{p.gender}')")
                    for iss in issues:
                        self.stdout.write(f"    ↳ {iss}")
                self.stdout.write(self.style.NOTICE("\nRun 'python manage.py validate_products --fix' to auto-resolve these issues."))
