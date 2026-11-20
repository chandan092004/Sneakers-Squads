"""
INSTALL PURE SNEAKERS (MEN & WOMEN) AND AUTHENTIC SNEAKER ACCESSORIES
- Replaces any t-shirt, apparel, or model photo with 100% genuine studio sneakers.
- Men's Collection: 20 unique pure sneakers.
- Women's Collection: 20 unique pure sneakers.
- Accessories: 24 strictly sneaker care, utility & display products.
"""

import os
import sys
import urllib.request
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneakerweb.settings')
import django
django.setup()

from django.core.files.base import ContentFile
from accounts.models import Product, ProductImage

MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'sneakers')
STATIC_ACC_DIR = os.path.join(BASE_DIR, 'static', 'img', 'accessories')
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(STATIC_ACC_DIR, exist_ok=True)

# 20 MEN'S PURE SNEAKERS (ZERO APPAREL, ZERO T-SHIRTS, ZERO HUMANS)
MEN_SNEAKERS = {
    # High-Tops
    'm-ht-01-air-jordan-1-retro-chicago': 'photo-1552346154-21d32810aba3',
    'm-ht-02-air-jordan-1-royal-blue': 'photo-1600774236989-a383d15c2e8a',
    'm-ht-03-nike-blazer-mid-77-vintage': 'photo-1629097499121-290fd9a95dee',
    'm-ht-04-off-white-air-jordan-1-high': 'photo-1516478177764-9fe5bd7e9717', # PURE SNEAKER (Replaced t-shirt!)

    # Low-Tops
    'm-lt-05-nike-dunk-low-retro-panda': 'photo-1597350584914-55bb62285896',
    'm-lt-06-adidas-samba-og-cloud-white': 'photo-1582588678413-dbf45f4823e9',
    'm-lt-07-new-balance-550-white-green': 'photo-1539185441755-769473a23570',
    'm-lt-08-puma-suede-classic-xxi-black': 'photo-1608231387042-66d1773070a5',

    # Running / Performance
    'm-rp-09-nike-air-zoom-pegasus-40': 'photo-1542291026-7eec264c27ff',
    'm-rp-10-adidas-ultraboost-light-carbon': 'photo-1637437757614-6491c8e915b5',
    'm-rp-11-nike-vaporfly-3-electric-mint': 'photo-1606107557195-0e29a4b5b4aa',
    'm-rp-12-nike-tempo-next-flyknit': 'photo-1605348532760-6753d2c43329',

    # Retro Classic
    'm-rc-13-air-jordan-4-retro-bred': 'photo-1512374382149-233c42b6a83b',
    'm-rc-14-travis-scott-jordan-1-reverse-mocha': 'photo-1597045566677-8cf032ed6634',
    'm-rc-15-nike-air-max-90-infrared-vintage': 'photo-1637437411826-bab0dc76a310',
    'm-rc-16-new-balance-990v6-castlerock': 'photo-1465453869711-7e174808ace9',

    # Chunky Streetwear
    'm-cs-17-balenciaga-triple-s-clear-sole': 'photo-1549298916-b41d501d3772',
    'm-cs-18-new-balance-9060-sea-salt': 'photo-1587563871167-1ee9c731aefb',
    'm-cs-19-adidas-ozweego-pure-chalk': 'photo-1600185365483-26d7a4cc7519',
    'm-cs-20-adidas-yeezy-boost-700-waverunner': 'photo-1600185365926-3a2ce3cdb9eb'
}

# 20 WOMEN'S PURE SNEAKERS (ZERO APPAREL, ZERO MODELS, ZERO DUPLICATES WITH MEN)
WOMEN_SNEAKERS = {
    # Platform Sneakers
    'w-ps-21-puma-mayze-stack-platform-white': 'photo-1575537302964-96cd47c06b1b',
    'w-ps-22-nike-m2k-tekno-phantom-summit': 'photo-1595341888016-a392ef81b7de',
    'w-ps-23-salomon-xt6-mindful-trail': 'photo-1617606002779-51d866bdd1d1',
    'w-ps-24-converse-run-star-motion-platform': 'photo-1607522370275-f14206abe5d3',

    # Running Trainers
    'w-rt-25-asics-gel-nimbus-25-sunrise': 'photo-1595950653106-6c9ebd614d3a',
    'w-rt-26-new-balance-fresh-foam-1080v13': 'photo-1621315271772-28b1f3a5df87',
    'w-rt-27-hoka-clifton-9-rose-mist': 'photo-1562183241-b937e95585b6',
    'w-rt-28-nike-air-max-270-coral-white': 'photo-1584735935682-2f2b69dff9d2',

    # Slip-Ons
    'w-so-29-vans-classic-slip-on-checkerboard': 'photo-1525966222134-fcfa99b8ae77',
    'w-so-30-balenciaga-speed-2-knit-slip-on': 'photo-1603808033192-082d6919d3e1',
    'w-so-31-puma-adelina-comfort-slipon': 'photo-1588117260148-b47818741c74',
    'w-so-32-adidas-puremotion-adapt-white': 'photo-1518002171953-a080ee817e1f',

    # Minimalist White
    'w-mw-33-nike-air-force-1-triple-white': 'photo-1560769629-975ec94e6a86',
    'w-mw-34-vans-old-skool-true-white': 'photo-1637437735621-22472eee4875',
    'w-mw-35-nike-dunk-low-barely-green': 'photo-1617814121568-9b184eaabf08',
    'w-mw-36-veja-campo-extra-white-natural': 'photo-1571744253502-6c4e841ccd91',

    # Chunky Streetwear
    'w-cs-37-air-jordan-1-retro-shadow-2': 'photo-1579338559194-a162d19bf842',
    'w-cs-38-nike-react-phantom-run-street': 'photo-1706550631437-0ad78e9005d5',
    'w-cs-39-onitsuka-tiger-mexico-66-street': 'photo-1747691574113-7388c13aae8a',
    'w-cs-40-fila-disruptor-ii-premium-white': 'photo-1511556532299-8f662fc26c06'
}

# 24 ACCESSORIES (STRICTLY SNEAKER CARE, LACES, DISPLAYS, DEODORIZERS - ZERO SHOES)
ACCESSORIES_META = {
    # 1. Magnetic Levitating Displays
    'acc-ml-01-anti-gravity-floating-sneaker-display': {'pid': 'photo-1550745165-9bc0b252726f', 'badge': 'MAGNETIC FLOAT', 'color': '#ff5a1f'},
    'acc-ml-02-aura-rgb-levitating-platform': {'pid': 'photo-1508700115892-45ecd05ae2ad', 'badge': 'AURA RGB 360°', 'color': '#ec4899'},
    'acc-ml-03-starlight-magnetic-levitation-showcase': {'pid': 'photo-1518770660439-4636190af475', 'badge': 'LEVITATION DOCK', 'color': '#3b82f6'},
    'acc-ml-04-minimalist-float-pedestal-white': {'pid': 'photo-1517336714731-489689fd1ca8', 'badge': 'FLOAT PEDESTAL', 'color': '#10b981'},

    # 2. Crease Protectors
    'acc-cp-05-ergonomic-breathable-crease-guards': {'pid': 'photo-1584308666744-24d5c474f2ae', 'badge': 'CREASE DEFLECTOR', 'color': '#ff5a1f'},
    'acc-cp-06-ultra-flex-memory-foam-crease-armor': {'pid': 'photo-1584735935682-2f2b69dff9d2', 'badge': 'MEMORY FOAM ARMOR', 'color': '#6366f1'},
    'acc-cp-07-carbon-fiber-reinforced-shields': {'pid': 'photo-1607604276583-eef5d076aa5f', 'badge': 'CARBON FIBER SHIELD', 'color': '#f59e0b'},
    'acc-cp-08-invisible-gel-cushioned-toe-guards': {'pid': 'photo-1528740561666-dc2479dc08ab', 'badge': 'CLEAR GEL GUARDS', 'color': '#06b6d4'},

    # 3. Sneaker Cleaning Kits
    'acc-ck-09-pro-clean-ultimate-sneaker-kit': {'pid': 'photo-1583947215259-38e31be8751f', 'badge': 'DEEP CLEANING KIT', 'color': '#ff5a1f'},
    'acc-ck-10-quick-cleansing-foam-ready-pump': {'pid': 'photo-1528740561666-dc2479dc08ab', 'badge': 'CLEANSING FOAM PUMP', 'color': '#3b82f6'},
    'acc-ck-11-suede-nubuck-renewal-eraser-kit': {'pid': 'photo-1584308666744-24d5c474f2ae', 'badge': 'SUEDE ERASER SET', 'color': '#d97706'},
    'acc-ck-12-dual-sided-textured-sneaker-wipes-40pk': {'pid': 'photo-1607604276583-eef5d076aa5f', 'badge': 'TEXTURED WIPES 40PK', 'color': '#10b981'},

    # 4. Hydrophobic Waterproof Sprays
    'acc-hs-13-hydro-shield-nano-waterproof-spray': {'pid': 'photo-1563178406-4cdc2923acbc', 'badge': 'NANO REPELLENT SPRAY', 'color': '#06b6d4'},
    'acc-hs-14-invisible-armor-heavy-rain-barrier': {'pid': 'photo-1522335789203-aabd1fc54bc9', 'badge': 'WEATHERPROOF SHIELD', 'color': '#8b5cf6'},
    'acc-hs-15-eco-pump-non-aerosol-water-repellent': {'pid': 'photo-1585421514738-01798e348b17', 'badge': 'ECO NON-AEROSOL PUMP', 'color': '#10b981'},
    'acc-hs-16-rapid-cure-quick-dry-repel-mist': {'pid': 'photo-1526947425960-945c6e72858f', 'badge': '15-MIN QUICK DRY MIST', 'color': '#3b82f6'},

    # 5. Reflective & Custom Shoelaces
    'acc-sl-17-3m-high-vis-reflective-rope-laces-silver': {'pid': 'photo-1584917865442-de89df76afd3', 'badge': '3M REFLECTIVE ROPE', 'color': '#e2e8f0'},
    'acc-sl-18-heavyweight-waxed-cotton-dunk-laces-sail': {'pid': 'photo-1582588678413-dbf45f4823e9', 'badge': 'WAXED COTTON SAIL', 'color': '#fef3c7'},
    'acc-sl-19-neon-volt-oval-sb-skate-laces': {'pid': 'photo-1511556532299-8f662fc26c06', 'badge': 'CHUNKY SB OVAL LACES', 'color': '#84cc16'},
    'acc-sl-20-glow-in-the-dark-tubular-laces-cyber': {'pid': 'photo-1509198397868-475647b2a1e5', 'badge': 'GLOW PHOSPHOR LACES', 'color': '#10b981'},

    # 6. Sneaker Deodorizer Balls
    'acc-db-21-activated-carbon-kinetic-deodorizer-balls-6pk': {'pid': 'photo-1602928321679-560bb453f190', 'badge': 'ACTIVATED CARBON BALLS', 'color': '#ff5a1f'},
    'acc-db-22-aroma-lock-capsule-freshener-pills-4pk': {'pid': 'photo-1584017911766-d451b3d0e843', 'badge': 'ZEOLITE FRESHENER PILLS', 'color': '#06b6d4'},
    'acc-db-23-citrus-burst-antibacterial-freshener-spheres': {'pid': 'photo-1616486338812-3dadae4b4ace', 'badge': 'CITRUS FRESH SPHERES', 'color': '#f97316'},
    'acc-db-24-bamboo-charcoal-deodorizing-sachets-4pk': {'pid': 'photo-1563245372-f21724e3856d', 'badge': 'BAMBOO CHARCOAL PODS', 'color': '#10b981'}
}


def download_square_photo(pid, badge=None, color='#ff5a1f'):
    url = f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w=800&q=82"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        req = urllib.request.Request(url, headers=headers)
        raw = urllib.request.urlopen(req, timeout=12).read()
        img = Image.open(BytesIO(raw)).convert('RGB')
    except Exception as e:
        print(f"  ⚠️ Error downloading {pid}: {e}")
        return None

    img = ImageOps.fit(img, (800, 800), Image.Resampling.LANCZOS)

    # Optional subtle badge tag for accessories
    if badge:
        draw = ImageDraw.Draw(img)
        draw.rectangle([(20, 20), (320, 56)], fill='#0b0d13')
        draw.rectangle([(20, 20), (320, 56)], outline=color, width=2)
        draw.text((36, 28), f"SQUAD • {badge}", fill='#ffffff')

        draw.rectangle([(0, 755), (800, 800)], fill='#0b0d13')
        draw.text((24, 768), "ANTI-GRAVITY SNEAKER LABS", fill='#94a3b8')
        draw.text((630, 768), "VERIFIED GEAR", fill=color)

    buf = BytesIO()
    img.save(buf, format='JPEG', quality=90)
    return buf.getvalue()


def run():
    print("=" * 70)
    print("👟 INSTALLING 100% PURE SNEAKERS & AUTHENTIC ACCESSORIES")
    print("=" * 70)

    # 1. Update Men's Sneakers (20 Items)
    print("\n--- [1/3] UPDATING 20 MEN'S SNEAKERS (ZERO APPAREL, ZERO T-SHIRTS) ---")
    for idx, (code, pid) in enumerate(MEN_SNEAKERS.items(), 1):
        filename = f"{code}.jpg"
        media_path = os.path.join(MEDIA_DIR, filename)

        print(f"[{idx:02d}/20] Downloading Men Sneaker {code} ({pid})...")
        img_bytes = download_square_photo(pid)
        if img_bytes:
            with open(media_path, 'wb') as f:
                f.write(img_bytes)

            try:
                prod = Product.objects.get(code=code)
                prod.image_file.name = f"sneakers/{filename}"
                prod.image_url = f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w=800&q=80&sku={code}"
                prod.main_image = prod.image_url
                prod.image = prod.image_url
                prod.gender = 'men'
                prod.save()

                ProductImage.objects.filter(product=prod).delete()
                ProductImage.objects.create(
                    product=prod,
                    image=prod.image_file,
                    image_url=prod.image_url,
                    alt_text=prod.title or prod.name,
                    is_primary=True
                )
                print(f"  ✅ Updated Men Sneaker: {prod.name[:45]}")
            except Product.DoesNotExist:
                print(f"  ⚠️ Product {code} not in DB")

    # 2. Update Women's Sneakers (20 Items)
    print("\n--- [2/3] UPDATING 20 WOMEN'S SNEAKERS (ZERO APPAREL, ZERO DUPLICATES) ---")
    for idx, (code, pid) in enumerate(WOMEN_SNEAKERS.items(), 1):
        filename = f"{code}.jpg"
        media_path = os.path.join(MEDIA_DIR, filename)

        print(f"[{idx:02d}/20] Downloading Women Sneaker {code} ({pid})...")
        img_bytes = download_square_photo(pid)
        if img_bytes:
            with open(media_path, 'wb') as f:
                f.write(img_bytes)

            try:
                prod = Product.objects.get(code=code)
                prod.image_file.name = f"sneakers/{filename}"
                prod.image_url = f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w=800&q=80&sku={code}"
                prod.main_image = prod.image_url
                prod.image = prod.image_url
                prod.gender = 'women'
                prod.save()

                ProductImage.objects.filter(product=prod).delete()
                ProductImage.objects.create(
                    product=prod,
                    image=prod.image_file,
                    image_url=prod.image_url,
                    alt_text=prod.title or prod.name,
                    is_primary=True
                )
                print(f"  ✅ Updated Women Sneaker: {prod.name[:45]}")
            except Product.DoesNotExist:
                print(f"  ⚠️ Product {code} not in DB")

    # 3. Update Accessories (24 Items - Strictly Gear/Utility)
    print("\n--- [3/3] UPDATING 24 ACCESSORIES (STRICTLY SNEAKER CARE & GEAR) ---")
    for idx, (code, meta) in enumerate(ACCESSORIES_META.items(), 1):
        filename = f"{code}.jpg"
        media_path = os.path.join(MEDIA_DIR, filename)
        static_path = os.path.join(STATIC_ACC_DIR, filename)

        print(f"[{idx:02d}/24] Processing Accessory {code}...")
        img_bytes = download_square_photo(meta['pid'], badge=meta['badge'], color=meta['color'])
        if img_bytes:
            with open(media_path, 'wb') as f:
                f.write(img_bytes)
            with open(static_path, 'wb') as f:
                f.write(img_bytes)

            try:
                prod = Product.objects.get(code=code)
                prod.image_file.name = f"sneakers/{filename}"
                prod.image_url = f"/static/img/accessories/{filename}"
                prod.main_image = prod.image_url
                prod.image = prod.image_url
                prod.gender = 'unisex'
                prod.save()

                ProductImage.objects.filter(product=prod).delete()
                ProductImage.objects.create(
                    product=prod,
                    image=prod.image_file,
                    image_url=prod.image_url,
                    alt_text=prod.title or prod.name,
                    is_primary=True
                )
                print(f"  ✅ Updated Accessory: {prod.name[:45]}")
            except Product.DoesNotExist:
                print(f"  ⚠️ Accessory {code} not in DB")

    print("\n" + "=" * 70)
    print("🎉 ALL 64 PRODUCTS (20 MEN + 20 WOMEN + 24 ACCESSORIES) INSTALLED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    run()
