import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import Category, SubCategory, Product


class Command(BaseCommand):
    help = "Seeds the e-commerce catalog with exactly 60 balanced products (multiples of 4) across Men, Women, and Accessories with 100% unique studio images."

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Wipe existing catalog products before seeding to guarantee the exact balanced catalog counts.',
        )

    def handle(self, *args, **options):
        flush = options.get('flush', False)

        self.stdout.write(self.style.MIGRATE_HEADING("=" * 75))
        self.stdout.write(self.style.MIGRATE_HEADING("  SNEAKER SQUAD: RELATIONAL CATALOG DATA SEEDER"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 75))

        if flush:
            self.stdout.write(self.style.WARNING("⚠️ Flushing existing Product catalog as requested (--flush)..."))
            deleted_count, _ = Product.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Purged {deleted_count} legacy products.\n"))

        # ----------------------------------------------------------------------
        # 1. SETUP CATEGORIES
        # ----------------------------------------------------------------------
        categories_meta = {
            'men': {'name': 'men', 'slug': 'men', 'desc': "Men's performance sneakers and streetwear apparel.", 'icon': 'fa-shoe-prints'},
            'women': {'name': 'women', 'slug': 'women', 'desc': "Women's designer kicks, pastels, and elegant footwear.", 'icon': 'fa-gem'},
            'accessories': {'name': 'accessories', 'slug': 'accessories', 'desc': "Curated luxury watches, utility packs, and sneaker care.", 'icon': 'fa-clock'},
        }

        category_objs = {}
        for key, meta in categories_meta.items():
            cat, created = Category.objects.get_or_create(
                slug=meta['slug'],
                defaults={
                    'name': meta['name'],
                    'description': meta['desc'],
                    'icon_class': meta['icon'],
                    'is_active': True,
                    'show_in_navbar': True
                }
            )
            # Ensure name matches choice
            if cat.name != meta['name']:
                cat.name = meta['name']
                cat.save()
            category_objs[key] = cat
            status = "Created" if created else "Retained"
            self.stdout.write(self.style.SUCCESS(f"  ✓ Category [{key}] {status}: {cat.get_name_display()}"))

        # ----------------------------------------------------------------------
        # 2. SETUP SUBCATEGORIES
        # ----------------------------------------------------------------------
        subcategories_meta = [
            ('men', 'shoes', 'Shoes Only', 'High-performance men basketball, running, and retro kicks'),
            ('men', 'apparel', 'Apparel', 'Streetwear hoodies, utility cargo pants, and vintage tees'),
            ('women', 'sneakers', 'Sneakers / Casuals', 'Pastel running silhouettes, platform runners, and court shoes'),
            ('women', 'heels', 'Heels & Flats', 'Classic pointed stilettos, Mary Janes, and penny loafers'),
            ('accessories', 'watches', 'Luxury Watches', 'Chronographs, automatic timepieces, and tactical steel watches'),
            ('accessories', 'bags', 'Bags & Backpacks', 'Waterproof sneaker commuter packs, duffels, and utility slings'),
        ]

        subcat_objs = {}
        for cat_key, sub_slug, sub_name, desc in subcategories_meta:
            parent_cat = category_objs[cat_key]
            subcat, created = SubCategory.objects.get_or_create(
                category=parent_cat,
                slug=sub_slug,
                defaults={'name': sub_name, 'description': desc}
            )
            subcat_objs[f"{cat_key}:{sub_slug}"] = subcat
            status = "Created" if created else "Retained"
            self.stdout.write(self.style.SUCCESS(f"  ✓ SubCategory [{cat_key} > {sub_slug}] {status}: {subcat.name}"))

        self.stdout.write("\n" + self.style.MIGRATE_LABEL("Seeding 60 curated items with 100% unique studio photography..."))

        # ----------------------------------------------------------------------
        # 3. EXACT 60-ITEM BALANCED DATASET
        # ----------------------------------------------------------------------
        catalog_items = [
            # ==================================================================
            # MEN > SHOES (EXACTLY 16 UNIQUE SNEAKERS) - 4 full desktop rows
            # ==================================================================
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Nike Air Jordan 1 High Retro Chicago',
                'brand': 'Nike / Jordan', 'price': 13999, 'original_price': 16999,
                'color': 'Varsity Red / White / Black', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Iconic Drop', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 342,
                'description': 'The definitive court classic in premium leather upper with signature Air-Sole heel unit and high-traction rubber pivot cupsole.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Nike Air Max Red Sprint 90',
                'brand': 'Nike', 'price': 8999, 'original_price': 10999,
                'color': 'Gym Red / White', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Bestseller', 'badge_style': 'trending', 'rating': 4.8, 'reviews_count': 215,
                'description': 'Visible Max Air cushioning and durable stitched overlays deliver unmatched athletic heritage and street dominance.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Converse Chuck 70 Vintage High',
                'brand': 'Converse', 'price': 5499, 'original_price': 6499,
                'color': 'Egret White / Black', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Classic', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 180,
                'description': 'Crafted in 12oz organic canvas with enhanced archival winged tongue stitching and OrthoLite insole comfort.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Nike Dunk Low Retro Panda Edition',
                'brand': 'Nike', 'price': 9999, 'original_price': 11999,
                'color': 'Black / White', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Hot Drop', 'badge_style': 'sale', 'rating': 4.9, 'reviews_count': 410,
                'description': 'Crisp leather color blocking with padded low-cut collar for slick modern versatility across day-to-night styling.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Adidas Forum Low Cloud White',
                'brand': 'Adidas', 'price': 7499, 'original_price': 8999,
                'color': 'Cloud White / Core Royal', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Heritage', 'badge_style': 'new', 'rating': 4.6, 'reviews_count': 124,
                'description': '80s hardwood legacy reinvented with hook-and-loop ankle cross strap and premium coated leather construction.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Yeezy Boost 350 V2 Core Onyx',
                'brand': 'Adidas / Yeezy', 'price': 18499, 'original_price': 21999,
                'color': 'Core Black / Charcoal', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Grail Piece', 'badge_style': 'limited', 'rating': 5.0, 'reviews_count': 520,
                'description': 'Re-engineered Primeknit upper fitted onto full-length responsive Boost midsole encased within semi-translucent TPU ribbing.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'New Balance 550 White Sea Salt',
                'brand': 'New Balance', 'price': 8499, 'original_price': 9999,
                'color': 'Sea Salt / Neutral Grey', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Trending', 'badge_style': 'trending', 'rating': 4.8, 'reviews_count': 195,
                'description': 'Tribute to 1989 basketball icons featuring streamlined leather silhouette and clean non-marking rubber outsole.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Puma Suede Classic XXI Streetwear',
                'brand': 'Puma', 'price': 4999, 'original_price': 6299,
                'color': 'Forest Green / Pristine', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Essential', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 89,
                'description': 'Velvety full-suede upper, comfortable synthetic lining, and textured rubber sole that shaped breakdance culture.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Vans Old Skool Pro Skate Black',
                'brand': 'Vans', 'price': 4499, 'original_price': 5299,
                'color': 'Black / White Sidestripe', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Core Skate', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 310,
                'description': 'DURACAP reinforced underlays, PopCush energy return footbeds, and original waffle compound outsoles for board feel.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Asics Gel-Kayano 14 Metallic Silver',
                'brand': 'Asics', 'price': 11999, 'original_price': 13999,
                'color': 'Pure Silver / French Blue', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1579338559194-a162d19bf842?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Y2K Runner', 'badge_style': 'trending', 'rating': 4.9, 'reviews_count': 167,
                'description': '2000s technical running aesthetics infused with original GEL technology cushioning and supportive TRUSSTIC system.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Reebok Club C 85 Vintage Chalk',
                'brand': 'Reebok', 'price': 5999, 'original_price': 7299,
                'color': 'Chalk / Glen Green', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Court Icon', 'badge_style': 'new', 'rating': 4.6, 'reviews_count': 142,
                'description': 'Soft garment leather upper with terrycloth collar lining for vintage tennis aesthetic and lightweight die-cut EVA midsole.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': "Nike Air Force 1 '07 Triple White",
                'brand': 'Nike', 'price': 8195, 'original_price': 9995,
                'color': 'Triple White', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1605348532760-6753d2c43329?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Must Have', 'badge_style': 'trending', 'rating': 4.9, 'reviews_count': 640,
                'description': 'The legend lives on with smooth leather overlays, crisp edges, and encapsulated Nike Air cushioning.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Air Jordan 4 Retro Bred Reimagined',
                'brand': 'Nike / Jordan', 'price': 17999, 'original_price': 20999,
                'color': 'Black / Fire Red / Cement Grey', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1512374382149-233c42b661ac?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Grail Drop', 'badge_style': 'limited', 'rating': 5.0, 'reviews_count': 480,
                'description': 'Supple full-grain leather replacement with authentic molded quarter mesh panels and sculpted Air unit heel wedge.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Adidas Samba OG Cloud White Core Black',
                'brand': 'Adidas', 'price': 7999, 'original_price': 9499,
                'color': 'Cloud White / Core Black / Gum', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Viral Street', 'badge_style': 'trending', 'rating': 4.8, 'reviews_count': 390,
                'description': 'Low-profile indoor soccer icon sporting distinctive T-toe suede overlay and gum rubber traction cupsole.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'New Balance 990v5 Heritage Grey',
                'brand': 'New Balance', 'price': 16499, 'original_price': 18999,
                'color': 'Castlerock Grey / White', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1514989940723-e8e51635b782?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Made In USA', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 220,
                'description': 'ENCAP midsole technology pairs durable polyurethane rim with lightweight EVA core for all-day arch stability.'
            },
            {
                'category': 'men', 'subcat': 'shoes', 'gender': 'men',
                'title': 'Nike ZoomX Vaporfly Next% Racing',
                'brand': 'Nike', 'price': 19999, 'original_price': 23999,
                'color': 'Electric Volt / Mint', 'tag': 'shoes',
                'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Marathon Elite', 'badge_style': 'new', 'rating': 4.9, 'reviews_count': 175,
                'description': 'Full-length carbon fiber propulsion plate suspended inside responsive ZoomX foam for competitive speed records.'
            },

            # ==================================================================
            # MEN > APPAREL (EXACTLY 8 UNIQUE ITEMS) - 2 full desktop rows
            # ==================================================================
            {
                'category': 'men', 'subcat': 'apparel', 'gender': 'men',
                'title': 'Heavyweight Streetwear Boxy Hoodie',
                'brand': 'Squad Kicks Studio', 'price': 3499, 'original_price': 4499,
                'color': 'Charcoal Slate', 'tag': 'apparel',
                'image_url': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'New Drop', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 92,
                'description': '450 GSM ultra-heavy combed cotton fleece with drop shoulders, double-layered hood, and hidden kangaroo pocket.'
            },
            {
                'category': 'men', 'subcat': 'apparel', 'gender': 'men',
                'title': 'Vintage Washed Oversized Boxy Tee',
                'brand': 'Squad Kicks Studio', 'price': 1499, 'original_price': 1999,
                'color': 'Washed Acid Black', 'tag': 'apparel',
                'image_url': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Bestseller', 'badge_style': 'trending', 'rating': 4.7, 'reviews_count': 158,
                'description': '240 GSM single jersey cotton finished with vintage enzyme wash, thick ribbed collar, and relaxed skater fit.'
            },
            {
                'category': 'men', 'subcat': 'apparel', 'gender': 'men',
                'title': 'Tactical Ripstop Utility Cargo Pants',
                'brand': 'TechDivision', 'price': 3999, 'original_price': 4999,
                'color': 'Combat Olive Drab', 'tag': 'apparel',
                'image_url': 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Techwear', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 84,
                'description': 'DWR water-repellent ripstop weave equipped with 8 modular bellows pockets, articulated knees, and toggle ankle cuffs.'
            },
            {
                'category': 'men', 'subcat': 'apparel', 'gender': 'men',
                'title': 'Relaxed French Terry Street Joggers',
                'brand': 'Squad Kicks Studio', 'price': 2799, 'original_price': 3499,
                'color': 'Heather Grey', 'tag': 'apparel',
                'image_url': 'https://images.unsplash.com/photo-1552902865-b72c031ac5ea?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Core Comfort', 'badge_style': 'new', 'rating': 4.6, 'reviews_count': 64,
                'description': '380 GSM loopback cotton terry featuring concealed metal zipper pockets, elasticized waistband, and clean tapered cuff.'
            },
            {
                'category': 'men', 'subcat': 'apparel', 'gender': 'men',
                'title': 'Sherpa Lined Vintage Denim Trucker Jacket',
                'brand': 'Heritage Denim', 'price': 4999, 'original_price': 6499,
                'color': 'Washed Indigo Blue', 'tag': 'apparel',
                'image_url': 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Winter Drop', 'badge_style': 'sale', 'rating': 4.9, 'reviews_count': 110,
                'description': '14oz non-stretch ring-spun denim lined with warm faux shearling, dual button flap chest pockets, and waist adjusters.'
            },
            {
                'category': 'men', 'subcat': 'apparel', 'gender': 'men',
                'title': 'Athletic Graphic Fleece Crewneck Sweatshirt',
                'brand': 'Sneaker Squad Lab', 'price': 2499, 'original_price': 3199,
                'color': 'Oatmeal Melange', 'tag': 'apparel',
                'image_url': 'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Retro Graphic', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 78,
                'description': 'Vintage collegiate screen-printed chest emblem with reinforced V-insert triangle ribbing and brushed fleece interior.'
            },
            {
                'category': 'men', 'subcat': 'apparel', 'gender': 'men',
                'title': 'Modern Flight Satin MA-1 Bomber Jacket',
                'brand': 'AeroStyle', 'price': 5499, 'original_price': 6999,
                'color': 'Midnight Navy Black', 'tag': 'apparel',
                'image_url': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Premium', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 135,
                'description': 'High-density water-resistant nylon shell with emergency orange satin lining, antique brass hardware, and sleeve utility tag.'
            },
            {
                'category': 'men', 'subcat': 'apparel', 'gender': 'men',
                'title': 'Breathable Performance Mesh Training Shorts',
                'brand': 'Squad Athletics', 'price': 1299, 'original_price': 1799,
                'color': 'Core Black / Reflective', 'tag': 'apparel',
                'image_url': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Quick Dry', 'badge_style': 'new', 'rating': 4.6, 'reviews_count': 56,
                'description': 'Double-layer open-hole sports mesh with sweat-wicking poly liner, 7-inch inseam, and reflective side split hems.'
            },

            # ==================================================================
            # WOMEN > SNEAKERS (EXACTLY 12 UNIQUE ITEMS) - 3 full desktop rows
            # ==================================================================
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Nike Air Max 270 Blush Peach Edition',
                'brand': 'Nike', 'price': 10999, 'original_price': 12999,
                'color': 'Pastel Peach / White', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1588117260148-b47818741c74?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Bestseller', 'badge_style': 'trending', 'rating': 4.9, 'reviews_count': 230,
                'description': 'Signature 270-degree Max Air heel unit with breathable stretch knit mesh bootie sleeve for a snug cloud-like stride.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Adidas Gazelle Pastel Lavender Suede',
                'brand': 'Adidas', 'price': 6999, 'original_price': 8499,
                'color': 'Lilac / Cloud White / Gum', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Pastel Drop', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 165,
                'description': 'Soft pigskin suede upper accented with synthetic leather 3-Stripes and retro low-profile rubber cupsole.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'New Balance 327 Sea Salt White',
                'brand': 'New Balance', 'price': 7999, 'original_price': 9499,
                'color': 'Sea Salt / Turtledove', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Chunky Retro', 'badge_style': 'trending', 'rating': 4.8, 'reviews_count': 190,
                'description': 'Asymmetric flared EVA wedge midsole combined with wraparound trail-inspired lugged rubber outsole.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Veja Campo Peach White Leather',
                'brand': 'Veja', 'price': 11499, 'original_price': 13499,
                'color': 'Extra White / Peach V-Logo', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1575537302964-96cd47c06b1b?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Eco Luxury', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 140,
                'description': 'ChromeFree leather construction with Amazonian wild rubber sole and organic cotton mesh lining.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Nike Dunk Low Rose Whisper Pastel',
                'brand': 'Nike', 'price': 9499, 'original_price': 11499,
                'color': 'Rose Whisper / White', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1595341888016-a392ef81b7de?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Viral Drop', 'badge_style': 'sale', 'rating': 5.0, 'reviews_count': 380,
                'description': 'Subtle muted blush two-tone panels crafted on supple leather frame with perforated toe box and cushioned heel.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Puma Cali Dream Pastel Mint Edition',
                'brand': 'Puma', 'price': 5499, 'original_price': 6999,
                'color': 'Pristine / Soft Mint', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Platform Dream', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 112,
                'description': 'West Coast court attitude featuring elevated chunky platform midsole with sleek TPU insert accents.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Converse Run Star Hike High Platform',
                'brand': 'Converse', 'price': 6499, 'original_price': 7999,
                'color': 'White Canvas / Gum Lug', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1529810313688-44ea1c2d81d3?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Statement Kick', 'badge_style': 'trending', 'rating': 4.9, 'reviews_count': 275,
                'description': 'Classic canvas Chuck silhouette perched upon dramatic two-tone jagged sawtooth rubber platform outsole.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'On Cloudtilt Pearl Cream Runner',
                'brand': 'On Running', 'price': 13999, 'original_price': 15999,
                'color': 'Pearl / Sand', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1518002171953-a080ee817e1f?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'CloudTec', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 160,
                'description': 'Computer-generated CloudTec Phase cushioning delivers seamless sequential weight transfer and ultra-soft landings.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Asics Gel-NYC Cream Blush Pink',
                'brand': 'Asics', 'price': 10499, 'original_price': 12499,
                'color': 'Cream / Oyster Grey / Blush', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1597045566677-8cf032ed6634?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Street Tech', 'badge_style': 'trending', 'rating': 4.8, 'reviews_count': 130,
                'description': 'Gel-Cumulus 16 tooling merges with archival GEL-NIMBUS 3 upper panels for maximum shock dampening.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Adidas Samba Classic Blush Pink Leather',
                'brand': 'Adidas', 'price': 8499, 'original_price': 9999,
                'color': 'Wonder Clay Pink / Off White', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1579298245158-3382b0f9f882?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Trending', 'badge_style': 'trending', 'rating': 4.9, 'reviews_count': 320,
                'description': 'Beloved retro trainer upgraded in soft powdery pink leather with tonal 3-stripes and natural gum outsole.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Nike Air Force 1 Shadow Pastel Mix',
                'brand': 'Nike', 'price': 9299, 'original_price': 10999,
                'color': 'Sail / Glacier Blue / Sunset Pulse', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Double Vision', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 245,
                'description': 'Playful layered perspective boasting 2 eyestays, 2 mudguards, 2 back tabs, and 2 Swoosh design overlays.'
            },
            {
                'category': 'women', 'subcat': 'sneakers', 'gender': 'women',
                'title': 'Hoka Clifton 9 Whisper Lilac Runner',
                'brand': 'Hoka', 'price': 12499, 'original_price': 14499,
                'color': 'Whisper Lilac / Pearl', 'tag': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Ultra Cushion', 'badge_style': 'new', 'rating': 4.9, 'reviews_count': 185,
                'description': 'Lighter and more cushioned with responsive compression-molded EVA foam and early-stage Meta-Rocker geometry.'
            },

            # ==================================================================
            # WOMEN > HEELS & FLATS (EXACTLY 8 UNIQUE ITEMS) - 2 full desktop rows
            # ==================================================================
            {
                'category': 'women', 'subcat': 'heels', 'gender': 'women',
                'title': 'Classic Pointed Toe Noir Stiletto Pump',
                'brand': 'Atelier Elegance', 'price': 4499, 'original_price': 5999,
                'color': 'Glossy Noir Black', 'tag': 'heels',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Evening Classic', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 140,
                'description': 'Sharp sculpted silhouette with balanced 85mm slim heel, cushioned memory foam insole, and leather outsole.'
            },
            {
                'category': 'women', 'subcat': 'heels', 'gender': 'women',
                'title': 'Minimalist Strappy Nude Block Heel Sandal',
                'brand': 'Atelier Elegance', 'price': 3799, 'original_price': 4799,
                'color': 'Warm Sand Nude', 'tag': 'heels',
                'image_url': 'https://images.unsplash.com/photo-1534653299134-96a171b61581?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Bestseller', 'badge_style': 'trending', 'rating': 4.7, 'reviews_count': 95,
                'description': 'Barely-there tubular straps with comfortable 60mm architectural cylindrical block heel and adjustable ankle clasp.'
            },
            {
                'category': 'women', 'subcat': 'heels', 'gender': 'women',
                'title': 'Chunky Platform Mary Jane Suede Loafers',
                'brand': 'Atelier Elegance', 'price': 3999, 'original_price': 4999,
                'color': 'Burgundy Wine / Polished Black', 'tag': 'heels',
                'image_url': 'https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Runway Drop', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 82,
                'description': 'Polished calfskin upper adorned with silver horsebit buckle and chunky grooved platform lug sole.'
            },
            {
                'category': 'women', 'subcat': 'heels', 'gender': 'women',
                'title': 'Suede Slingback Low Kitten Heel',
                'brand': 'Atelier Elegance', 'price': 3499, 'original_price': 4299,
                'color': 'Dusty Rose Pink', 'tag': 'heels',
                'image_url': 'https://images.unsplash.com/photo-1596704017254-9b121068fb31?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Chic Comfort', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 74,
                'description': 'Buttery velvet suede pointed toe with delicate 45mm curved kitten heel and flexible elastic slingback loop.'
            },
            {
                'category': 'women', 'subcat': 'heels', 'gender': 'women',
                'title': 'Square Toe Woven Leather Slip-On Mule',
                'brand': 'Atelier Elegance', 'price': 2999, 'original_price': 3799,
                'color': 'Ivory Cream Woven', 'tag': 'heels',
                'image_url': 'https://images.unsplash.com/photo-1562273138-f46be4ebdf33?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Resort Edition', 'badge_style': 'new', 'rating': 4.6, 'reviews_count': 60,
                'description': 'Intricately hand-woven nappa leather band on low stacked wooden heel for easy warm-weather elegance.'
            },
            {
                'category': 'women', 'subcat': 'heels', 'gender': 'women',
                'title': 'Classic Leather Penny Loafer Flat',
                'brand': 'Heritage Studio', 'price': 4299, 'original_price': 5499,
                'color': 'Cognac Tan Leather', 'tag': 'heels',
                'image_url': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Preppy Icon', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 115,
                'description': 'Traditional moc-stitched toe box with authentic slotted leather penny saddle and durable Goodyear-welted rubber heel.'
            },
            {
                'category': 'women', 'subcat': 'heels', 'gender': 'women',
                'title': "Elegant D'Orsay Ankle Strap Velvet Pump",
                'brand': 'Atelier Elegance', 'price': 3899, 'original_price': 4899,
                'color': 'Emerald Velvet Green', 'tag': 'heels',
                'image_url': 'https://images.unsplash.com/photo-1581044777550-4cfa60707c03?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Cocktail Edit', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 88,
                'description': 'Side cutaway D\'Orsay silhouette finished with slender ankle strap and padded satin sockliner.'
            },
            {
                'category': 'women', 'subcat': 'heels', 'gender': 'women',
                'title': 'Pointed Toe Muted Ballerina Ballet Flat',
                'brand': 'Atelier Elegance', 'price': 2499, 'original_price': 3299,
                'color': 'Matte Dove Grey', 'tag': 'heels',
                'image_url': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Everyday Staple', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 102,
                'description': 'Featherweight slip-on flat with cushioned latex arch support and flexible anti-skid rubber sole.'
            },

            # ==================================================================
            # ACCESSORIES > WATCHES (EXACTLY 8 UNIQUE TIMEPIECES)
            # ==================================================================
            {
                'category': 'accessories', 'subcat': 'watches', 'gender': 'unisex',
                'title': 'Matte Black Stealth Chronograph Timepiece',
                'brand': 'Chronos Precision', 'price': 7999, 'original_price': 9999,
                'color': 'Matte PVD Black', 'tag': 'watches',
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Stealth Edit', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 180,
                'description': '42mm 316L surgical stainless steel case with scratch-resistant sapphire crystal and Japanese quartz triple subdial movement.'
            },
            {
                'category': 'accessories', 'subcat': 'watches', 'gender': 'unisex',
                'title': 'Minimalist Brushed Silver Steel Watch',
                'brand': 'Nordic Minimal', 'price': 5499, 'original_price': 6999,
                'color': 'Brushed Silver / Sunray White', 'tag': 'watches',
                'image_url': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Scandinavian', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 125,
                'description': 'Ultra-slim 7mm profile watch featuring clean index markers, quick-release link bracelet, and 50M water resistance.'
            },
            {
                'category': 'accessories', 'subcat': 'watches', 'gender': 'unisex',
                'title': 'Rose Gold Milanese Mesh Minimalist Watch',
                'brand': 'Nordic Minimal', 'price': 6299, 'original_price': 7999,
                'color': 'Rose Gold / Eggshell White', 'tag': 'watches',
                'image_url': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Bestseller', 'badge_style': 'trending', 'rating': 4.9, 'reviews_count': 160,
                'description': 'Jewelry-grade ion-plated rose gold finish with magnetic adjustable woven Milanese stainless steel loop strap.'
            },
            {
                'category': 'accessories', 'subcat': 'watches', 'gender': 'unisex',
                'title': 'Tactical Diver Stainless Steel 200M Watch',
                'brand': 'Nautilus Tech', 'price': 11499, 'original_price': 13999,
                'color': 'Deep Ocean Blue / Steel', 'tag': 'watches',
                'image_url': 'https://images.unsplash.com/photo-1533139502658-0198f920d8e8?auto=format&fit=crop&w=800&q=80',
                'badge_text': '200M Diver', 'badge_style': 'limited', 'rating': 5.0, 'reviews_count': 210,
                'description': 'Unidirectional 120-click ceramic dive bezel, Swiss Super-LumiNova hour hands, and screw-down crown.'
            },
            {
                'category': 'accessories', 'subcat': 'watches', 'gender': 'unisex',
                'title': 'Heritage Brown Saddle Leather Dress Watch',
                'brand': 'Chronos Precision', 'price': 4999, 'original_price': 6499,
                'color': 'Antique Gold / Tan Leather', 'tag': 'watches',
                'image_url': 'https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Heritage', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 94,
                'description': 'Hand-stitched Tuscan vegetable-tanned leather strap with champagne sunburst dial and date magnification cyclops window.'
            },
            {
                'category': 'accessories', 'subcat': 'watches', 'gender': 'unisex',
                'title': 'Digital Retro Gold Stainless Steel Watch',
                'brand': 'Tokyo Cyber', 'price': 3999, 'original_price': 4999,
                'color': 'Vintage Gold Plated', 'tag': 'watches',
                'image_url': 'https://images.unsplash.com/photo-1508615039623-a25605d2b022?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Y2K Retro', 'badge_style': 'trending', 'rating': 4.8, 'reviews_count': 178,
                'description': '1980s digital chronograph retro revival with amber electroluminescent backlight, daily alarm, and countdown timer.'
            },
            {
                'category': 'accessories', 'subcat': 'watches', 'gender': 'unisex',
                'title': 'Pilot Aviator Automatic Exhibition Watch',
                'brand': 'Chronos Precision', 'price': 14999, 'original_price': 17999,
                'color': 'Satin Titanium Grey', 'tag': 'watches',
                'image_url': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Automatic', 'badge_style': 'limited', 'rating': 5.0, 'reviews_count': 145,
                'description': 'Self-winding mechanical automatic caliber movement with 42-hour power reserve and transparent sapphire exhibition caseback.'
            },
            {
                'category': 'accessories', 'subcat': 'watches', 'gender': 'unisex',
                'title': 'Ceramic Midnight Stealth Edition Watch',
                'brand': 'AeroStyle', 'price': 9999, 'original_price': 12499,
                'color': 'Gloss Ceramic Noir', 'tag': 'watches',
                'image_url': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'High-Tech Ceramic', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 118,
                'description': 'Virtually unscratchable high-tech sintered zirconium oxide ceramic case and bracelet with hidden butterfly deployant clasp.'
            },

            # ==================================================================
            # ACCESSORIES > BAGS & BACKPACKS (EXACTLY 8 UNIQUE ITEMS)
            # ==================================================================
            {
                'category': 'accessories', 'subcat': 'bags', 'gender': 'unisex',
                'title': 'Waterproof Sneaker Commuter Backpack 30L',
                'brand': 'Squad Carry Lab', 'price': 4499, 'original_price': 5999,
                'color': 'Matte Armor Black', 'tag': 'bags',
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Sneakerhead Pick', 'badge_style': 'trending', 'rating': 4.9, 'reviews_count': 260,
                'description': 'Dedicated ventilated bottom compartment engineered specifically to carry 2 pairs of high-top sneakers plus 16-inch laptop.'
            },
            {
                'category': 'accessories', 'subcat': 'bags', 'gender': 'unisex',
                'title': 'Tactical Cordura Crossbody Utility Sling',
                'brand': 'TechDivision', 'price': 2199, 'original_price': 2999,
                'color': 'Stealth Black / Neon Accent', 'tag': 'bags',
                'image_url': 'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Bestseller', 'badge_style': 'trending', 'rating': 4.8, 'reviews_count': 195,
                'description': '1000D ballistic Cordura fabric with magnetic Fidlock quick-release buckle, waterproof YKK zippers, and MOLLE webbing.'
            },
            {
                'category': 'accessories', 'subcat': 'bags', 'gender': 'unisex',
                'title': 'Premium Full-Grain Leather Duffel Weekend Bag',
                'brand': 'Heritage Carry', 'price': 6999, 'original_price': 8999,
                'color': 'Espresso Rich Brown', 'tag': 'bags',
                'image_url': 'https://images.unsplash.com/photo-1547949003-9792a18a2601?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Luxury Leather', 'badge_style': 'limited', 'rating': 5.0, 'reviews_count': 130,
                'description': 'Full-grain vegetable-tanned bovine leather with brass rivets, reinforced carry handles, and water-resistant nylon lining.'
            },
            {
                'category': 'accessories', 'subcat': 'bags', 'gender': 'unisex',
                'title': 'Ripstop Roll-Top Urban Waterproof Pack 25L',
                'brand': 'Squad Carry Lab', 'price': 3799, 'original_price': 4699,
                'color': 'Storm Grey / Cyan', 'tag': 'bags',
                'image_url': 'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Weatherproof', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 85,
                'description': 'Seamless TPU welded construction guarantees 100% submersion waterproofing with ergonomic EVA foam back panel.'
            },
            {
                'category': 'accessories', 'subcat': 'bags', 'gender': 'unisex',
                'title': 'Minimalist Heavy Canvas Everyday Tote Shopper',
                'brand': 'Squad Studio', 'price': 1499, 'original_price': 1999,
                'color': 'Natural Ecru Canvas', 'tag': 'bags',
                'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Eco Friendly', 'badge_style': 'new', 'rating': 4.6, 'reviews_count': 72,
                'description': '16oz heavy organic unbleached cotton duck canvas featuring reinforced box-X stitched webbing handles and internal key clasp.'
            },
            {
                'category': 'accessories', 'subcat': 'bags', 'gender': 'unisex',
                'title': 'Dedicated Sneaker Travel Organizer Case',
                'brand': 'Squad Carry Lab', 'price': 3299, 'original_price': 4299,
                'color': 'Carbon Fiber Weave', 'tag': 'bags',
                'image_url': 'https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Sneaker Vault', 'badge_style': 'limited', 'rating': 4.9, 'reviews_count': 165,
                'description': 'Shock-absorbing EVA hard-shell briefcase holds 4 pairs of full-size sneakers with adjustable padded protective dividers.'
            },
            {
                'category': 'accessories', 'subcat': 'bags', 'gender': 'unisex',
                'title': 'Compact Streetwear Everyday Waist Pack',
                'brand': 'TechDivision', 'price': 1699, 'original_price': 2299,
                'color': 'Ultra Matte Black', 'tag': 'bags',
                'image_url': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Street Staple', 'badge_style': 'new', 'rating': 4.7, 'reviews_count': 140,
                'description': 'Water-resistant ripstop nylon with padded breathable airmesh back, headphone cord port, and secure rear passport pocket.'
            },
            {
                'category': 'accessories', 'subcat': 'bags', 'gender': 'unisex',
                'title': 'Heritage Waxed Canvas Daypack 20L',
                'brand': 'Heritage Carry', 'price': 4299, 'original_price': 5499,
                'color': 'Field Tan Khaki / Leather', 'tag': 'bags',
                'image_url': 'https://images.unsplash.com/photo-1605733513597-a8f8341084e6?auto=format&fit=crop&w=800&q=80',
                'badge_text': 'Waxed Canvas', 'badge_style': 'new', 'rating': 4.8, 'reviews_count': 98,
                'description': 'Traditional paraffin-wax treated water-shedding canvas combined with bridle leather straps and brass roller buckles.'
            },
        ]

        # ----------------------------------------------------------------------
        # 4. VALIDATE IMAGE UNIQUENESS & DENSITY CONSTRAINTS BEFORE PERSISTING
        # ----------------------------------------------------------------------
        urls_set = set()
        for idx, item in enumerate(catalog_items, 1):
            url = item['image_url']
            if url in urls_set:
                raise ValueError(f"CRITICAL ERROR: Duplicate image URL detected at item #{idx}: {url}")
            urls_set.add(url)

        self.stdout.write(self.style.SUCCESS(f"  ✓ Pre-validation PASSED: 60/60 image URLs strictly unique!"))

        # ----------------------------------------------------------------------
        # 5. PERSIST PRODUCTS
        # ----------------------------------------------------------------------
        created_count = 0
        updated_count = 0

        for idx, data in enumerate(catalog_items, 1):
            cat_obj = category_objs[data['category']]
            subcat_obj = subcat_objs.get(f"{data['category']}:{data['subcat']}")

            # Generate stable unique code
            slug_seed = slugify(data['title'])[:40]
            code = f"{data['category'][:1]}-{data['subcat'][:2]}-{idx:02d}-{slug_seed}"

            # Check if product with this image_url exists
            product, created = Product.objects.update_or_create(
                image_url=data['image_url'],
                defaults={
                    'code': code,
                    'title': data['title'],
                    'name': data['title'],
                    'brand': data['brand'],
                    'category': cat_obj,
                    'subcategory': subcat_obj,
                    'gender': data['gender'],
                    'price': data['price'],
                    'original_price': data['original_price'],
                    'color': data['color'],
                    'tag': data['tag'],
                    'image': data['image_url'],
                    'main_image': data['image_url'],
                    'badge_text': data['badge_text'],
                    'badge_style': data['badge_style'],
                    'rating': data['rating'],
                    'reviews_count': data['reviews_count'],
                    'description': data['description'],
                    'stock_quantity': 25,
                    'is_in_stock': True,
                    'is_active': True,
                    'is_featured': (idx % 6 == 0),
                    'is_trending': (idx % 4 == 0),
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        # ----------------------------------------------------------------------
        # 6. PRINT AUDIT REPORT
        # ----------------------------------------------------------------------
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("=" * 75))
        self.stdout.write(self.style.SUCCESS("  CATALOG SEEDING SUCCESSFUL! DENSITY & UNIQUENESS AUDIT:"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 75))
        
        men_shoes_count = Product.objects.filter(category=category_objs['men'], subcategory=subcat_objs['men:shoes']).count()
        men_apparel_count = Product.objects.filter(category=category_objs['men'], subcategory=subcat_objs['men:apparel']).count()
        women_sneakers_count = Product.objects.filter(category=category_objs['women'], subcategory=subcat_objs['women:sneakers']).count()
        women_heels_count = Product.objects.filter(category=category_objs['women'], subcategory=subcat_objs['women:heels']).count()
        acc_watches_count = Product.objects.filter(category=category_objs['accessories'], subcategory=subcat_objs['accessories:watches']).count()
        acc_bags_count = Product.objects.filter(category=category_objs['accessories'], subcategory=subcat_objs['accessories:bags']).count()

        total_catalog = Product.objects.count()
        unique_images_db = Product.objects.values('image_url').distinct().count()

        self.stdout.write(f"  • Men > Shoes/Sneakers:    {men_shoes_count:2d} items (Target: 16 | 4 full rows) -> {'✅ PASS' if men_shoes_count == 16 else '❌ FAIL'}")
        self.stdout.write(f"  • Men > Apparel/Casuals:   {men_apparel_count:2d} items (Target:  8 | 2 full rows) -> {'✅ PASS' if men_apparel_count == 8 else '❌ FAIL'}")
        self.stdout.write(f"  • Women > Sneakers:        {women_sneakers_count:2d} items (Target: 12 | 3 full rows) -> {'✅ PASS' if women_sneakers_count == 12 else '❌ FAIL'}")
        self.stdout.write(f"  • Women > Heels & Flats:   {women_heels_count:2d} items (Target:  8 | 2 full rows) -> {'✅ PASS' if women_heels_count == 8 else '❌ FAIL'}")
        self.stdout.write(f"  • Accessories > Watches:   {acc_watches_count:2d} items (Target:  8 | 2 full rows) -> {'✅ PASS' if acc_watches_count == 8 else '❌ FAIL'}")
        self.stdout.write(f"  • Accessories > Bags:      {acc_bags_count:2d} items (Target:  8 | 2 full rows) -> {'✅ PASS' if acc_bags_count == 8 else '❌ FAIL'}")
        self.stdout.write("  " + "-" * 71)
        self.stdout.write(f"  • Total Catalog Volume:    {total_catalog:2d} items (Total Target: 60) -> {'✅ PASS' if total_catalog == 60 else '⚠️ NOTICE'}")
        self.stdout.write(f"  • Zero Duplicate Policy:   {unique_images_db:2d} Unique Image URLs in DB -> {'✅ 100% UNIQUE' if unique_images_db == total_catalog else '❌ DUPLICATES'}")
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 75 + "\n"))
