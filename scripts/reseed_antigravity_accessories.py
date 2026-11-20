"""
ANTI-GRAVITY SNEAKER ACCESSORIES SEEDER & IMAGE ASSET BUILDER
Strictly replaces low-quality / irrelevant items (socks, generic storage bins)
with 24 authentic, high-end sneaker accessories:
1. Magnetic Levitating Displays (4 items)
2. Crease Protectors (4 items)
3. Premium Sneaker Cleaning Kits (4 items)
4. Hydrophobic Waterproof Sprays (4 items)
5. Reflective & Custom Shoelaces (4 items)
6. Sneaker Deodorizer Balls (4 items)
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneakerweb.settings')
django.setup()

from django.core.files.base import ContentFile
from accounts.models import Category, SubCategory, Product, ProductImage

MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'sneakers')
STATIC_ACC_DIR = os.path.join(BASE_DIR, 'static', 'img', 'accessories')
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(STATIC_ACC_DIR, exist_ok=True)

ACCESSORIES_DATA = [
    # -------------------------------------------------------------------------
    # 1. Magnetic Levitating Displays (levitating-displays)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'levitating-displays',
        'subcat_name': 'Magnetic Levitating Displays',
        'code': 'acc-ml-01-anti-gravity-floating-sneaker-display',
        'title': 'Anti-Gravity Magnetic Levitating Sneaker Display Stand',
        'brand': 'Gravity Kicks',
        'price': 4499.00,
        'original_price': 6999.00,
        'gender': 'unisex',
        'color': 'Matte Black / Cyber Glow',
        'badge_text': 'HOT DROP',
        'badge_style': 'hot',
        'rating': 4.9,
        'reviews_count': 342,
        'stock': 40,
        'tag': 'levitating-displays magnetic levitating floating display sneaker stand 360 rotation',
        'description': 'Futuristic electromagnetic suspension dock with 360-degree continuous silent rotation and white LED halo illumination. Effortlessly suspends kicks up to 550g in mid-air.',
        'image_url': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#ff5a1f',
        'category_tag': 'LEVITATING DISPLAY'
    },
    {
        'subcat_slug': 'levitating-displays',
        'subcat_name': 'Magnetic Levitating Displays',
        'code': 'acc-ml-02-aura-rgb-levitating-platform',
        'title': 'Aura RGB 360° Rotating Floating Sneaker Platform',
        'brand': 'Gravity Kicks',
        'price': 4999.00,
        'original_price': 7499.00,
        'gender': 'unisex',
        'color': 'Obsidian Black / Chroma RGB',
        'badge_text': 'PREMIUM',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 285,
        'stock': 35,
        'tag': 'levitating-displays aura rgb floating sneaker platform 360 ambient led magnetic dock',
        'description': 'Dynamic 16-color ambient RGB LED system with touch-sensitive mode toggle, auto-stabilizing dual magnet core, and ultra-quiet motor for showcasegrails.',
        'image_url': 'https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#ec4899',
        'category_tag': 'LEVITATING DISPLAY'
    },
    {
        'subcat_slug': 'levitating-displays',
        'subcat_name': 'Magnetic Levitating Displays',
        'code': 'acc-ml-03-starlight-magnetic-levitation-showcase',
        'title': 'Starlight Pro Levitating Sneaker Showcase Dock',
        'brand': 'Gravity Kicks',
        'price': 5499.00,
        'original_price': 7999.00,
        'gender': 'unisex',
        'color': 'Space Grey / Pure White',
        'badge_text': 'GRAIL',
        'badge_style': 'hot',
        'rating': 5.0,
        'reviews_count': 198,
        'stock': 25,
        'tag': 'levitating-displays starlight pro magnetic levitation dock aluminum spotlight showcase',
        'description': 'Anodized aerospace aluminum finish with intelligent auto-pickup power memory, micro-weight balance calibration, and an integrated exhibition-grade downward spotlight.',
        'image_url': 'https://images.unsplash.com/photo-1597045566677-8cf032ed6634?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#3b82f6',
        'category_tag': 'LEVITATING DISPLAY'
    },
    {
        'subcat_slug': 'levitating-displays',
        'subcat_name': 'Magnetic Levitating Displays',
        'code': 'acc-ml-04-minimalist-float-pedestal-white',
        'title': 'Minimalist Apex Magnetic Floating Sneaker Pedestal',
        'brand': 'Gravity Kicks',
        'price': 3999.00,
        'original_price': 5999.00,
        'gender': 'unisex',
        'color': 'Triple White',
        'badge_text': 'BEST VALUE',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 175,
        'stock': 45,
        'tag': 'levitating-displays minimalist apex floating pedestal white magnetic underglow dock',
        'description': 'Ultra-clean matte white architectural floating dock with soft ambient underglow, silent neodymium levitation ring, and instant power-loss anti-drop protection.',
        'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#10b981',
        'category_tag': 'LEVITATING DISPLAY'
    },

    # -------------------------------------------------------------------------
    # 2. Crease Protectors (crease-protectors)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'crease-protectors',
        'subcat_name': 'Crease Protectors',
        'code': 'acc-cp-05-ergonomic-breathable-crease-guards',
        'title': 'Ergonomic Breathable Sneaker Crease Protectors (2-Pairs)',
        'brand': 'Shield Squad',
        'price': 499.00,
        'original_price': 899.00,
        'gender': 'unisex',
        'color': 'Carbon Black / Clear',
        'badge_text': 'BESTSELLER',
        'badge_style': 'hot',
        'rating': 4.9,
        'reviews_count': 560,
        'stock': 120,
        'tag': 'crease-protectors ergonomic breathable crease guards toe box wrinkle shield',
        'description': 'Ultra-thin pre-curved TPR polymer shields with 24 ventilation holes to keep your Jordan 1 & Air Force 1 toe boxes 100% wrinkle-free without pinching toes.',
        'image_url': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#ff5a1f',
        'category_tag': 'CREASE PROTECTOR'
    },
    {
        'subcat_slug': 'crease-protectors',
        'subcat_name': 'Crease Protectors',
        'code': 'acc-cp-06-ultra-flex-memory-foam-crease-armor',
        'title': 'Ultra-Flex Memory Foam Sneaker Toe Armor (2-Pairs)',
        'brand': 'Shield Squad',
        'price': 599.00,
        'original_price': 999.00,
        'gender': 'unisex',
        'color': 'Stealth Grey',
        'badge_text': 'MAX COMFORT',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 310,
        'stock': 90,
        'tag': 'crease-protectors ultra-flex memory foam toe armor cushion crease shield',
        'description': 'Dual-layer shock-absorbing memory foam and high-resilience polymer composite for all-day comfort while walking, running, or standing at sneaker conventions.',
        'image_url': 'https://images.unsplash.com/photo-1512374382149-233c42b6a83b?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#6366f1',
        'category_tag': 'CREASE PROTECTOR'
    },
    {
        'subcat_slug': 'crease-protectors',
        'subcat_name': 'Crease Protectors',
        'code': 'acc-cp-07-carbon-fiber-reinforced-shields',
        'title': 'Carbon Shield V2 Rigid Toe Box Deflectors',
        'brand': 'Shield Squad',
        'price': 699.00,
        'original_price': 1199.00,
        'gender': 'unisex',
        'color': 'Matte Carbon',
        'badge_text': 'HEAVY DUTY',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 240,
        'stock': 75,
        'tag': 'crease-protectors carbon shield v2 rigid toe box deflector high top crease guard',
        'description': 'Engineered carbon-reinforced toe structure designed specifically for premium high-top leather sneakers. Guided cut lines for custom edge-to-edge trimming.',
        'image_url': 'https://images.unsplash.com/photo-1514989940723-e8e51635b782?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#f59e0b',
        'category_tag': 'CREASE PROTECTOR'
    },
    {
        'subcat_slug': 'crease-protectors',
        'subcat_name': 'Crease Protectors',
        'code': 'acc-cp-08-invisible-gel-cushioned-toe-guards',
        'title': 'Invisible Clear Gel Crease Protectors (3-Pairs Combo)',
        'brand': 'Shield Squad',
        'price': 799.00,
        'original_price': 1499.00,
        'gender': 'unisex',
        'color': 'Crystal Clear',
        'badge_text': 'COMBO PACK',
        'badge_style': 'hot',
        'rating': 4.8,
        'reviews_count': 415,
        'stock': 110,
        'tag': 'crease-protectors invisible clear gel crease protectors toe guards multi pack',
        'description': 'Medical-grade hypoallergenic transparent silicone gel toe inserts. Zero visual imprint, anti-slip internal ribbing, and fully washable for endless reusability.',
        'image_url': 'https://images.unsplash.com/photo-1595341888016-a392ef81b7de?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#06b6d4',
        'category_tag': 'CREASE PROTECTOR'
    },

    # -------------------------------------------------------------------------
    # 3. Premium Sneaker Cleaning Kits (cleaning-kits)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'cleaning-kits',
        'subcat_name': 'Premium Sneaker Cleaning Kits',
        'code': 'acc-ck-09-pro-clean-ultimate-sneaker-kit',
        'title': 'Pro Clean Ultimate Sneaker Care Box Kit',
        'brand': 'Squad Care',
        'price': 1299.00,
        'original_price': 1999.00,
        'gender': 'unisex',
        'color': 'Squad Signature Orange/Black',
        'badge_text': 'ESSENTIAL',
        'badge_style': 'hot',
        'rating': 5.0,
        'reviews_count': 680,
        'stock': 85,
        'tag': 'cleaning-kits pro clean ultimate care kit solution hog bristle brush microfiber',
        'description': 'Comprehensive sneaker care setup: 200ml eco-friendly natural foaming solution, natural hog-bristle medium brush, brass sole brush, and ultra-plush microfiber cloth.',
        'image_url': 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#ff5a1f',
        'category_tag': 'CLEANING KIT'
    },
    {
        'subcat_slug': 'cleaning-kits',
        'subcat_name': 'Premium Sneaker Cleaning Kits',
        'code': 'acc-ck-10-quick-cleansing-foam-ready-pump',
        'title': 'Ready-Foam Instant Sneaker Cleanser 250ml Pump',
        'brand': 'Squad Care',
        'price': 649.00,
        'original_price': 999.00,
        'gender': 'unisex',
        'color': 'Clean White',
        'badge_text': 'NO WATER NEEDED',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 320,
        'stock': 95,
        'tag': 'cleaning-kits ready foam instant sneaker cleanser waterless pump cleaner',
        'description': 'Direct pump-to-shoe foaming cleanser that lifts stubborn road grime, dirt, and scuffs on contact without requiring water. Completely safe on knit, canvas, mesh, and leather.',
        'image_url': 'https://images.unsplash.com/photo-1585652615205-3aba30c23223?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#3b82f6',
        'category_tag': 'CLEANING KIT'
    },
    {
        'subcat_slug': 'cleaning-kits',
        'subcat_name': 'Premium Sneaker Cleaning Kits',
        'code': 'acc-ck-11-suede-nubuck-renewal-eraser-kit',
        'title': 'Suede & Nubuck Gentle Eraser & Crepe Brush Set',
        'brand': 'Squad Care',
        'price': 599.00,
        'original_price': 899.00,
        'gender': 'unisex',
        'color': 'Raw Wood / Sand Rubber',
        'badge_text': 'SPECIALTY',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 230,
        'stock': 70,
        'tag': 'cleaning-kits suede nubuck eraser crepe brush dry cleaner nap restorer',
        'description': 'Dry-cleaning crumb rubber eraser block and natural crepe brass wire brush to revive delicate suede nap and lift scuffs from Travis Scott Jordans & Dunks.',
        'image_url': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#d97706',
        'category_tag': 'CLEANING KIT'
    },
    {
        'subcat_slug': 'cleaning-kits',
        'subcat_name': 'Premium Sneaker Cleaning Kits',
        'code': 'acc-ck-12-dual-sided-textured-sneaker-wipes-40pk',
        'title': 'Dual-Textured Quick Sneaker Cleaning Wipes (40-Pack)',
        'brand': 'Squad Care',
        'price': 499.00,
        'original_price': 799.00,
        'gender': 'unisex',
        'color': 'Foil Wrapped White',
        'badge_text': 'TRAVEL READY',
        'badge_style': 'hot',
        'rating': 4.8,
        'reviews_count': 510,
        'stock': 130,
        'tag': 'cleaning-kits dual textured quick sneaker wipes portable wipes 40 pack',
        'description': 'Individually foil-wrapped wipes. Raised textured rubber dots on one side for midsole scrubbing and smooth soft weave on the other for delicate leather uppers.',
        'image_url': 'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#10b981',
        'category_tag': 'CLEANING KIT'
    },

    # -------------------------------------------------------------------------
    # 4. Hydrophobic Waterproof Sprays (hydrophobic-sprays)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'hydrophobic-sprays',
        'subcat_name': 'Hydrophobic Waterproof Sprays',
        'code': 'acc-hs-13-hydro-shield-nano-waterproof-spray',
        'title': 'Hydro-Shield Ultra Nano Waterproof & Stain Repellent 250ml',
        'brand': 'Hydro Guard',
        'price': 899.00,
        'original_price': 1399.00,
        'gender': 'unisex',
        'color': 'Matte Black Canister',
        'badge_text': 'TOP RATED',
        'badge_style': 'hot',
        'rating': 5.0,
        'reviews_count': 490,
        'stock': 90,
        'tag': 'hydrophobic-sprays hydro shield nano waterproof stain repellent aerosol spray',
        'description': 'Revolutionary nanotechnology aerosol barrier creates an invisible lotus-leaf hydrophobic seal. Repels water, mud, coffee, and sauce for up to 6 months per coat.',
        'image_url': 'https://images.unsplash.com/photo-1563178406-4cdc2923acbc?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#06b6d4',
        'category_tag': 'HYDROPHOBIC SPRAY'
    },
    {
        'subcat_slug': 'hydrophobic-sprays',
        'subcat_name': 'Hydrophobic Waterproof Sprays',
        'code': 'acc-hs-14-invisible-armor-heavy-rain-barrier',
        'title': 'Invisible Armor Extreme Weather Proofing Spray 300ml',
        'brand': 'Hydro Guard',
        'price': 1099.00,
        'original_price': 1699.00,
        'gender': 'unisex',
        'color': 'Gunmetal Steel',
        'badge_text': 'MAX DEFENSE',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 260,
        'stock': 60,
        'tag': 'hydrophobic-sprays invisible armor extreme weather proofing heavy rain barrier spray',
        'description': 'Industrial-grade UV and water protective coating tailored for primeknit and mesh uppers. 100% breathable with zero discoloration or shoe stiffening.',
        'image_url': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#8b5cf6',
        'category_tag': 'HYDROPHOBIC SPRAY'
    },
    {
        'subcat_slug': 'hydrophobic-sprays',
        'subcat_name': 'Hydrophobic Waterproof Sprays',
        'code': 'acc-hs-15-eco-pump-non-aerosol-water-repellent',
        'title': 'Eco-Shield Odorless Non-Aerosol Repellent 200ml',
        'brand': 'Hydro Guard',
        'price': 749.00,
        'original_price': 1149.00,
        'gender': 'unisex',
        'color': 'Forest Green / Clear',
        'badge_text': 'ECO FRIENDLY',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 185,
        'stock': 80,
        'tag': 'hydrophobic-sprays eco shield odorless non aerosol pump spray water repellent',
        'description': 'Water-based, non-flammable pump spray formula safe for indoor home application. Exceptional stain barrier on nubuck, canvas, and vintage Jordan leather.',
        'image_url': 'https://images.unsplash.com/photo-1608248597359-20f5080c950a?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#10b981',
        'category_tag': 'HYDROPHOBIC SPRAY'
    },
    {
        'subcat_slug': 'hydrophobic-sprays',
        'subcat_name': 'Hydrophobic Waterproof Sprays',
        'code': 'acc-hs-16-rapid-cure-quick-dry-repel-mist',
        'title': 'Rapid-Cure 15-Minute Quick-Dry Hydrophobic Mist 250ml',
        'brand': 'Hydro Guard',
        'price': 949.00,
        'original_price': 1499.00,
        'gender': 'unisex',
        'color': 'Electric Blue Can',
        'badge_text': 'RAPID DRY',
        'badge_style': 'hot',
        'rating': 4.9,
        'reviews_count': 310,
        'stock': 75,
        'tag': 'hydrophobic-sprays rapid cure quick dry hydrophobic mist fast acting repellent',
        'description': 'Flash-drying nano-polymer dries fully in just 15 minutes. Instant weatherproofing protection when stepping out during sudden monsoon showers.',
        'image_url': 'https://images.unsplash.com/photo-1526947425960-945c6e72858f?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#3b82f6',
        'category_tag': 'HYDROPHOBIC SPRAY'
    },

    # -------------------------------------------------------------------------
    # 5. Reflective & Custom Shoelaces (custom-shoelaces)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'custom-shoelaces',
        'subcat_name': 'Reflective & Custom Shoelaces',
        'code': 'acc-sl-17-3m-high-vis-reflective-rope-laces-silver',
        'title': '3M High-Vis Reflective Rope Laces - Silver / Black (130cm)',
        'brand': 'Lace Squad',
        'price': 449.00,
        'original_price': 699.00,
        'gender': 'unisex',
        'color': 'Silver / Black 3M',
        'badge_text': '3M REFLECTIVE',
        'badge_style': 'hot',
        'rating': 5.0,
        'reviews_count': 420,
        'stock': 150,
        'tag': 'custom-shoelaces 3m high vis reflective rope laces silver black sneaker laces',
        'description': 'Premium braided tubular polyester woven with authentic 3M scotchlite reflective thread. Blazes brilliantly under flash and headlights with gunmetal metal aglets.',
        'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#e2e8f0',
        'category_tag': 'CUSTOM LACES'
    },
    {
        'subcat_slug': 'custom-shoelaces',
        'subcat_name': 'Reflective & Custom Shoelaces',
        'code': 'acc-sl-18-heavyweight-waxed-cotton-dunk-laces-sail',
        'title': 'Heavyweight Waxed Cotton Flat Laces - Vintage Sail (140cm)',
        'brand': 'Lace Squad',
        'price': 399.00,
        'original_price': 649.00,
        'gender': 'unisex',
        'color': 'Vintage Sail Cream',
        'badge_text': 'VINTAGE VIBE',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 380,
        'stock': 140,
        'tag': 'custom-shoelaces heavyweight waxed cotton flat laces vintage sail cream dunk laces',
        'description': 'Subtly waxed double-weave Japanese cotton with water resistance and stay-tied grip. The definitive custom lace swap for retro Jordan 1s and Nike SB Dunks.',
        'image_url': 'https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#fef3c7',
        'category_tag': 'CUSTOM LACES'
    },
    {
        'subcat_slug': 'custom-shoelaces',
        'subcat_name': 'Reflective & Custom Shoelaces',
        'code': 'acc-sl-19-neon-volt-oval-sb-skate-laces',
        'title': 'Chunky Oval SB Skate Laces - Cyber Neon Volt (140cm)',
        'brand': 'Lace Squad',
        'price': 399.00,
        'original_price': 599.00,
        'gender': 'unisex',
        'color': 'Neon Volt Yellow',
        'badge_text': 'STREETWEAR',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 210,
        'stock': 110,
        'tag': 'custom-shoelaces chunky oval sb skate laces neon volt yellow puffy tongue',
        'description': '9mm thick padded chunky oval skate laces engineered with dense core stuffing to deliver the iconic puffy tongue aesthetic for Nike SB Dunks and skate kicks.',
        'image_url': 'https://images.unsplash.com/photo-1511556532299-8f662fc26c06?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#84cc16',
        'category_tag': 'CUSTOM LACES'
    },
    {
        'subcat_slug': 'custom-shoelaces',
        'subcat_name': 'Reflective & Custom Shoelaces',
        'code': 'acc-sl-20-glow-in-the-dark-tubular-laces-cyber',
        'title': 'Glow-in-the-Dark Phosphor Laces - Aurora Green (125cm)',
        'brand': 'Lace Squad',
        'price': 499.00,
        'original_price': 799.00,
        'gender': 'unisex',
        'color': 'Aurora Green Glow',
        'badge_text': 'GLOW EFFECT',
        'badge_style': 'hot',
        'rating': 4.9,
        'reviews_count': 340,
        'stock': 95,
        'tag': 'custom-shoelaces glow in the dark phosphor laces aurora green night kicks',
        'description': 'Sunlight and UV-reactive phosphor yarn charges in 10 minutes and glows a vibrant electric emerald green in dark rooms, clubs, and night city streets.',
        'image_url': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#10b981',
        'category_tag': 'CUSTOM LACES'
    },

    # -------------------------------------------------------------------------
    # 6. Sneaker Deodorizer Balls (deodorizer-balls)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'deodorizer-balls',
        'subcat_name': 'Sneaker Deodorizer Balls',
        'code': 'acc-db-21-activated-carbon-kinetic-deodorizer-balls-6pk',
        'title': 'Activated Carbon Kinetic Sneaker Deodorizer Balls (6-Pack)',
        'brand': 'Fresh Squad',
        'price': 599.00,
        'original_price': 999.00,
        'gender': 'unisex',
        'color': 'Matte Black / Orange Vents',
        'badge_text': 'BESTSELLER',
        'badge_style': 'hot',
        'rating': 5.0,
        'reviews_count': 640,
        'stock': 130,
        'tag': 'deodorizer-balls activated carbon kinetic sneaker deodorizer balls shoe freshener',
        'description': 'Twist-to-activate spherical air fresheners packed with natural microporous activated carbon and tea tree extract to neutralize sneaker odor at the bacterial source.',
        'image_url': 'https://images.unsplash.com/photo-1602928321679-560bb453f190?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#ff5a1f',
        'category_tag': 'DEODORIZER BALLS'
    },
    {
        'subcat_slug': 'deodorizer-balls',
        'subcat_name': 'Sneaker Deodorizer Balls',
        'code': 'acc-db-22-aroma-lock-capsule-freshener-pills-4pk',
        'title': 'Aroma-Lock Zeolite Capsule Deodorizer Pills (4-Pack)',
        'brand': 'Fresh Squad',
        'price': 649.00,
        'original_price': 1099.00,
        'gender': 'unisex',
        'color': 'Cool Mint / Ice Blue',
        'badge_text': 'ZEOLITE TECH',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 275,
        'stock': 85,
        'tag': 'deodorizer-balls aroma lock zeolite capsule deodorizer pills moisture absorber',
        'description': 'Medical pill design featuring natural volcanic zeolite minerals and moisture-absorbing silica beads that keep shoe insoles dry, fresh, and bacteria-free.',
        'image_url': 'https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#06b6d4',
        'category_tag': 'DEODORIZER PILLS'
    },
    {
        'subcat_slug': 'deodorizer-balls',
        'subcat_name': 'Sneaker Deodorizer Balls',
        'code': 'acc-db-23-citrus-burst-antibacterial-freshener-spheres',
        'title': 'Citrus Burst Antibacterial Sneaker Spheres (6-Pack)',
        'brand': 'Fresh Squad',
        'price': 549.00,
        'original_price': 899.00,
        'gender': 'unisex',
        'color': 'Vibrant Orange',
        'badge_text': 'CITRUS FRESH',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 310,
        'stock': 100,
        'tag': 'deodorizer-balls citrus burst antibacterial sneaker spheres shoe freshener balls',
        'description': 'Quick-twist lock mechanism releases a fresh natural bergamot and cedarwood aroma. Perfect for post-gym runners, high-top kicks, and closet storage boxes.',
        'image_url': 'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#f97316',
        'category_tag': 'DEODORIZER BALLS'
    },
    {
        'subcat_slug': 'deodorizer-balls',
        'subcat_name': 'Sneaker Deodorizer Balls',
        'code': 'acc-db-24-bamboo-charcoal-deodorizing-sachets-4pk',
        'title': 'Moso Bamboo Charcoal Sneaker Deodorizing Pods (4-Pack)',
        'brand': 'Fresh Squad',
        'price': 699.00,
        'original_price': 1199.00,
        'gender': 'unisex',
        'color': 'Natural Heather Charcoal',
        'badge_text': 'NATURAL 100%',
        'badge_style': 'hot',
        'rating': 4.9,
        'reviews_count': 410,
        'stock': 95,
        'tag': 'deodorizer-balls moso bamboo charcoal deodorizing pods reusable odor absorber',
        'description': '100% organic activated Moso bamboo charcoal in breathable linen pouches. Reusable for up to 2 years by simply recharging under direct sunlight once a month.',
        'image_url': 'https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80',
        'accent_color': '#10b981',
        'category_tag': 'DEODORIZER PODS'
    }
]


def generate_modern_placeholder_image(item):
    """
    Creates an ultra-modern 800x800 dark-aesthetic product card visual.
    Matches the sleek Sneaker Squad cyberpunk / street aesthetic.
    """
    width, height = 800, 800
    img = Image.new('RGB', (width, height), color='#0d1017')
    draw = ImageDraw.Draw(img)

    accent = item.get('accent_color', '#ff5a1f')

    # 1. Subtle Outer Border & Inner Glow Container
    draw.rectangle([(24, 24), (776, 776)], outline='#1e2433', width=2)
    draw.rectangle([(32, 32), (768, 768)], fill='#141824')

    # 2. Glowing Category Badge Header
    cat_text = item.get('category_tag', 'SNEAKER ACCESSORY')
    draw.rectangle([(48, 48), (320, 84)], fill='#1e2433', outline=accent, width=1)
    draw.text((64, 58), cat_text, fill=accent)

    # 3. Top-Right Brand Badge
    brand = item['brand'].upper()
    draw.text((600, 58), brand, fill='#94a3b8')

    # 4. Center Futuristic Geometric Icon & Product Silhouette
    cx, cy = 400, 360
    # Outer ring
    draw.ellipse([(cx - 160, cy - 160), (cx + 160, cy + 160)], outline='#242c3d', width=3)
    draw.ellipse([(cx - 120, cy - 120), (cx + 120, cy + 120)], outline=accent, width=2)
    # Floating diamond / centerpiece
    draw.polygon([(cx, cy - 80), (cx + 80, cy), (cx, cy + 80), (cx - 80, cy)], outline='#ffffff', fill='#1b2030', width=2)
    # Inner energy core
    draw.ellipse([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill=accent)

    # 5. Product Title Block
    title = item['title']
    words = title.split()
    line1 = " ".join(words[:4])
    line2 = " ".join(words[4:9])
    line3 = " ".join(words[9:])

    draw.text((48, 560), line1, fill='#ffffff')
    if line2:
        draw.text((48, 595), line2, fill='#ffffff')
    if line3:
        draw.text((48, 630), line3, fill='#94a3b8')

    # 6. Bottom Price & Authentic Badge Bar
    draw.line([(48, 680), (752, 680)], fill='#242c3d', width=1)
    price_str = f"INR {int(item['price']):,}"
    draw.text((48, 710), price_str, fill=accent)

    badge_str = f"[{item['badge_text']}] - 100% AUTHENTIC"
    draw.text((480, 715), badge_str, fill='#10b981')

    # Save to buffer
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=95)
    return buf.getvalue()


def run():
    print("=" * 70)
    print("  👟 SEEDING AUTHENTIC ANTI-GRAVITY ACCESSORIES CATALOG")
    print("=" * 70)

    # 1. Ensure Parent Category 'accessories'
    cat_acc, _ = Category.objects.get_or_create(
        slug='accessories',
        defaults={'name': 'accessories', 'is_active': True}
    )

    # 2. Register 6 Clean Subcategories
    subcat_map = {}
    for item in ACCESSORIES_DATA:
        s_slug = item['subcat_slug']
        s_name = item['subcat_name']
        if s_slug not in subcat_map:
            sub_obj, _ = SubCategory.objects.get_or_create(
                slug=s_slug,
                category=cat_acc,
                defaults={'name': s_name, 'description': s_name}
            )
            subcat_map[s_slug] = sub_obj

    print(f"✅ Registered {len(subcat_map)} subcategories under Anti-Gravity Accessories.")

    # 3. Purge old irrelevant accessories (socks, crates, generic items)
    old_accs = Product.objects.filter(category=cat_acc)
    print(f"Purging {old_accs.count()} old accessory products...")
    ProductImage.objects.filter(product__in=old_accs).delete()
    old_accs.delete()
    print("✓ Old accessories purged cleanly.")

    # 4. Create all 24 authentic items
    print(f"\nPopulating {len(ACCESSORIES_DATA)} authentic Anti-Gravity accessories...")
    for idx, item in enumerate(ACCESSORIES_DATA, 1):
        code = item['code']
        subcat = subcat_map[item['subcat_slug']]

        # Save binary image asset locally
        image_bytes = generate_modern_placeholder_image(item)
        filename = f"{code}.jpg"
        local_path = os.path.join(MEDIA_DIR, filename)
        with open(local_path, 'wb') as f:
            f.write(image_bytes)

        # Also copy to static accessories folder
        static_path = os.path.join(STATIC_ACC_DIR, filename)
        with open(static_path, 'wb') as f:
            f.write(image_bytes)

        img_asset_url = f"/static/img/accessories/{filename}"

        # Create Product with guaranteed strictly unique asset URL
        product = Product.objects.create(
            code=code,
            title=item['title'],
            name=item['title'],
            brand=item['brand'],
            category=cat_acc,
            subcategory=subcat,
            gender=item['gender'],
            price=item['price'],
            original_price=item['original_price'],
            color=item['color'],
            badge_text=item['badge_text'],
            badge_style=item['badge_style'],
            rating=item['rating'],
            reviews_count=item['reviews_count'],
            stock_quantity=item['stock'],
            tag=f"accessories {item['subcat_slug']} {item['tag']}",
            description=item['description'],
            image_url=img_asset_url,
            main_image=img_asset_url,
            image=img_asset_url,
            is_in_stock=True,
            is_featured=(idx % 3 == 0),
            is_trending=('HOT' in item['badge_text'] or 'BESTSELLER' in item['badge_text']),
            is_active=True,
        )

        # Attach local image file
        product.image_file.save(filename, ContentFile(image_bytes), save=True)

        # Create primary ProductImage
        ProductImage.objects.create(
            product=product,
            image=product.image_file,
            image_url=img_asset_url,
            alt_text=item['title'],
            is_primary=True
        )

        print(f"  [{idx:02d}/24] ✅ Created: {item['title'][:40]} | ₹{item['price']:,.0f} ({item['subcat_slug']})")

    total_acc = Product.objects.filter(category=cat_acc).count()
    print("\n" + "=" * 70)
    print(f"  🎉 SUCCESS: {total_acc} authentic Anti-Gravity Accessories live in database!")
    print("=" * 70)


if __name__ == '__main__':
    run()
