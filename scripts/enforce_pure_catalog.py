import os
import sys
import django

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneakerweb.settings')
django.setup()

from accounts.models import Category, SubCategory, Product, ProductImage

# 1. Update m-ht-04 to ensure it uses the real sneaker studio image
offwhite = Product.objects.filter(code='m-ht-04-off-white-air-jordan-1-high').first()
if offwhite:
    img_path = '/media/sneakers/m-ht-04-off-white-air-jordan-1-high_yCap7lh.jpg'
    offwhite.image_url = img_path
    offwhite.main_image = img_path
    offwhite.image = img_path
    offwhite.save()
    ProductImage.objects.filter(product=offwhite).update(image_url=img_path)
    print("Updated m-ht-04 image to authentic sneaker asset.")

# 2. Define the exact 16 pure items for each category
MEN_16 = [
    'm-ht-01-air-jordan-1-retro-chicago',
    'm-ht-02-air-jordan-1-royal-blue',
    'm-ht-03-nike-blazer-mid-77-vintage',
    'm-ht-04-off-white-air-jordan-1-high',
    'm-lt-05-nike-dunk-low-retro-panda',
    'm-lt-06-adidas-samba-og-cloud-white',
    'm-lt-07-new-balance-550-white-green',
    'm-lt-08-puma-suede-classic-xxi-black',
    'm-rp-09-nike-air-zoom-pegasus-40',
    'm-rp-10-adidas-ultraboost-light-carbon',
    'm-rp-11-nike-vaporfly-3-electric-mint',
    'm-rp-12-nike-tempo-next-flyknit',
    'm-rc-13-air-jordan-4-retro-bred',
    'm-rc-14-travis-scott-jordan-1-reverse-mocha',
    'm-rc-15-nike-air-max-90-infrared-vintage',
    'm-rc-16-new-balance-990v6-castlerock'
]

WOMEN_16 = [
    'w-ps-21-puma-mayze-stack-platform-white',
    'w-ps-22-nike-m2k-tekno-phantom-summit',
    'w-ps-23-salomon-xt6-mindful-trail',
    'w-ps-24-converse-run-star-motion-platform',
    'w-rt-25-asics-gel-nimbus-25-sunrise',
    'w-rt-26-new-balance-fresh-foam-1080v13',
    'w-rt-27-hoka-clifton-9-rose-mist',
    'w-rt-28-nike-air-max-270-coral-white',
    'w-so-29-vans-classic-slip-on-checkerboard',
    'w-so-30-balenciaga-speed-2-knit-slip-on',
    'w-so-31-puma-adelina-comfort-slipon',
    'w-so-32-adidas-puremotion-adapt-white',
    'w-mw-33-nike-air-force-1-triple-white',
    'w-mw-34-vans-old-skool-true-white',
    'w-mw-35-nike-dunk-low-barely-green',
    'w-mw-36-veja-campo-extra-white-natural'
]

ACC_16 = [
    'acc-ck-41-premium-deep-cleaning-kit-solution',
    'acc-ck-42-quick-wipes-dual-textured-30pk',
    'acc-ck-43-hydro-shield-water-stain-repellent',
    'acc-ck-44-suede-nubuck-renewal-eraser-block',
    'acc-ps-45-heavyweight-cotton-flat-laces-sail',
    'acc-ps-46-reflective-3m-rope-laces-black-silver',
    'acc-ps-47-waxed-cotton-dunk-laces-white',
    'acc-ps-48-oval-sb-skate-thick-laces-volt',
    'acc-cp-49-ergonomic-breathable-crease-guards',
    'acc-cp-50-soft-foam-shock-absorbing-toe-fillers',
    'acc-cp-51-universal-anti-crease-shield-v2-black',
    'acc-cp-52-ventilated-clear-gel-toe-guards',
    'acc-dc-53-magnetic-drop-front-sneaker-case',
    'acc-dc-54-led-sound-activated-stackable-crate',
    'acc-oe-57-bamboo-charcoal-deodorizer-pouches',
    'acc-as-61-retro-ribbed-crew-socks-3pk-white'
]

KEPT_CODES = set(MEN_16 + WOMEN_16 + ACC_16)

# Delete all products not in this clean 48 set
deleted_count, _ = Product.objects.exclude(code__in=KEPT_CODES).delete()
print(f"Removed {deleted_count} surplus/non-target product records.")

# Verify and lock categories
men_cat = Category.objects.filter(slug='men').first()
women_cat = Category.objects.filter(slug='women').first()
acc_cat = Category.objects.filter(slug='accessories').first()

Product.objects.filter(code__in=MEN_16).update(category=men_cat, gender='men', is_active=True, is_in_stock=True)
Product.objects.filter(code__in=WOMEN_16).update(category=women_cat, gender='women', is_active=True, is_in_stock=True)
Product.objects.filter(code__in=ACC_16).update(category=acc_cat, gender='unisex', is_active=True, is_in_stock=True)

# Final Count Check
men_count = Product.objects.filter(category=men_cat).count()
women_count = Product.objects.filter(category=women_cat).count()
acc_count = Product.objects.filter(category=acc_cat).count()

print(f"Final Database Counts: Men={men_count}, Women={women_count}, Accessories={acc_count} (Total: {Product.objects.count()})")
