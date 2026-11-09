import sys
from django.core.management.base import BaseCommand
from accounts.models import Product


class Command(BaseCommand):
    help = "Detects and purges duplicate product image URLs across the catalog, preserving the initial entry intact."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate duplicate detection without deleting or modifying any database records.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 70))
        self.stdout.write(self.style.MIGRATE_HEADING("  SNEAKER SQUAD: DUPLICATE IMAGE ASSET PURGE & AUDIT TOOL"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 70))

        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️ DRY RUN MODE ACTIVE: No products will be deleted from the database.\n"))

        products = Product.objects.all().order_by('id')
        total_products = products.count()
        
        seen_images = {}
        duplicates_found = []
        purged_count = 0

        for product in products:
            img_target = (product.image_url or product.main_image or product.image or '').strip()
            
            if not img_target:
                continue

            if img_target in seen_images:
                original = seen_images[img_target]
                duplicates_found.append({
                    'duplicate_id': product.id,
                    'duplicate_code': product.code,
                    'duplicate_title': product.title or product.name,
                    'original_id': original.id,
                    'original_code': original.code,
                    'original_title': original.title or original.name,
                    'image': img_target
                })

                if not dry_run:
                    self.stdout.write(self.style.ERROR(
                        f"  ❌ PURGING DUPLICATE: Product #{product.id} [{product.code}] '{product.title or product.name}'"
                    ))
                    self.stdout.write(self.style.NOTICE(
                        f"     ↳ Shares image '{img_target}' with Original #{original.id} [{original.code}] '{original.title or original.name}'"
                    ))
                    product.delete()
                    purged_count += 1
                else:
                    self.stdout.write(self.style.WARNING(
                        f"  🔍 [DRY RUN] Would purge duplicate Product #{product.id} [{product.code}] '{product.title or product.name}'"
                    ))
            else:
                seen_images[img_target] = product
                # Ensure original entry has image_url populated cleanly
                if not dry_run and not product.image_url:
                    try:
                        product.image_url = img_target
                        product.save(update_fields=['image_url'])
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"     ⚠️ Could not set image_url on #{product.id}: {e}"))

        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS("  AUDIT SUMMARY:"))
        self.stdout.write(f"  • Total Products Scanned: {total_products}")
        self.stdout.write(f"  • Unique Product Images Retained: {len(seen_images)}")
        self.stdout.write(f"  • Duplicate Visual Assets Detected: {len(duplicates_found)}")

        if dry_run:
            self.stdout.write(self.style.WARNING(f"  • Products to be Purged: {len(duplicates_found)} (Rerun without --dry-run to purge)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"  • Duplicate Products Safely Purged: {purged_count}"))
            self.stdout.write(self.style.SUCCESS(f"  • Remaining Catalog Volume: {Product.objects.count()} products"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 70 + "\n"))

