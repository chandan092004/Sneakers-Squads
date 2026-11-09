import os
import sys
import json
import django

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneakerweb.settings')
django.setup()

from accounts.models import Product

products = Product.objects.all().order_by('category__slug', 'code')
data_dict = {}

men_list = []
women_list = []
acc_list = []

for p in products:
    d = p.to_dict()
    # Ensure primary_image_url is used for mainImage
    d['mainImage'] = p.primary_image_url
    d['imageUrl'] = p.primary_image_url
    d['gallery'] = [p.primary_image_url]
    d['colors'] = [
        {
            'name': p.color or 'Studio Edition',
            'hex': '#111111',
            'mainImage': p.primary_image_url,
            'gallery': [p.primary_image_url]
        }
    ]
    data_dict[p.code] = d

    if p.category and p.category.slug == 'men':
        men_list.append(p.code)
    elif p.category and p.category.slug == 'women':
        women_list.append(p.code)
    else:
        acc_list.append(p.code)

# Add backward compatibility aliases (m1, m2, w1, w2, a1, a2, etc.)
for idx, code in enumerate(men_list, 1):
    alias_id = f"m{idx}"
    aliased_data = dict(data_dict[code])
    aliased_data['id'] = alias_id
    data_dict[alias_id] = aliased_data

for idx, code in enumerate(women_list, 1):
    alias_id = f"w{idx}"
    aliased_data = dict(data_dict[code])
    aliased_data['id'] = alias_id
    data_dict[alias_id] = aliased_data

for idx, code in enumerate(acc_list, 1):
    alias_id = f"a{idx}"
    aliased_data = dict(data_dict[code])
    aliased_data['id'] = alias_id
    data_dict[alias_id] = aliased_data

js_content = f"""/**
 * SNEAKER SQUAD - Master Dynamic Product Database
 * Auto-synced from Django Database with 100% verified pure sneaker studio assets
 * Total Products: {len(products)} (+ legacy alias keys)
 */
const PRODUCTS_DATA = {json.dumps(data_dict, indent=2)};

if (typeof window !== 'undefined') {{
  window.PRODUCTS_DATA = PRODUCTS_DATA;
}}
"""

out_file = os.path.join(BASE_DIR, 'static', 'js', 'products-data.js')
with open(out_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Successfully generated {out_file} with {len(data_dict)} product entries ({len(products)} master items)!")
