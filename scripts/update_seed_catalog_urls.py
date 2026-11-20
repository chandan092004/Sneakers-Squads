import re
import os

SEEDS_FILE = os.path.abspath('accounts/management/commands/seed_catalog.py')
content = open(SEEDS_FILE, 'r', encoding='utf-8').read()

# Exact replacement URLs
REPLACEMENTS = {
    'w-ps-21-puma-mayze-stack-platform-white': 'https://images.unsplash.com/photo-1575537302964-96cd47c06b1b?auto=format&fit=crop&w=800&q=80',
    'w-ps-22-nike-m2k-tekno-phantom-summit': 'https://images.unsplash.com/photo-1595341888016-a392ef81b7de?auto=format&fit=crop&w=800&q=80',
    'w-ps-23-salomon-xt6-mindful-trail': 'https://images.unsplash.com/photo-1617606002779-51d866bdd1d1?auto=format&fit=crop&w=800&q=80',
    'w-ps-24-converse-run-star-motion-platform': 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?auto=format&fit=crop&w=800&q=80',
    'w-rt-25-asics-gel-nimbus-25-sunrise': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=800&q=80',
    'w-rt-26-new-balance-fresh-foam-1080v13': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&w=800&q=80',
    'w-rt-27-hoka-clifton-9-rose-mist': 'https://images.unsplash.com/photo-1605348532760-6753d2c43329?auto=format&fit=crop&w=800&q=80',
    'w-rt-28-nike-air-max-270-coral-white': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=800&q=80',
    'w-so-29-vans-classic-slip-on-checkerboard': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=800&q=80',
    'w-so-30-balenciaga-speed-2-knit-slip-on': 'https://images.unsplash.com/photo-1603808033192-082d6919d3e1?auto=format&fit=crop&w=800&q=80',
    'w-so-31-puma-adelina-comfort-slipon': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=800&q=80',
    'w-so-32-adidas-puremotion-adapt-white': 'https://images.unsplash.com/photo-1518002171953-a080ee817e1f?auto=format&fit=crop&w=800&q=80',
    'w-mw-33-nike-air-force-1-triple-white': 'https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?auto=format&fit=crop&w=800&q=80',
    'w-mw-34-vans-old-skool-true-white': 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=800&q=80',
    'w-mw-35-nike-dunk-low-barely-green': 'https://images.unsplash.com/photo-1597045566677-8cf032ed6634?auto=format&fit=crop&w=800&q=80',
    'w-mw-36-veja-campo-extra-white-natural': 'https://images.unsplash.com/photo-1514989940723-e8e51635b782?auto=format&fit=crop&w=800&q=80',
    'w-cs-37-air-jordan-1-retro-shadow-2': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80',
    'w-cs-38-nike-react-phantom-run-street': 'https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?auto=format&fit=crop&w=800&q=80',
    'w-cs-39-onitsuka-tiger-mexico-66-street': 'https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?auto=format&fit=crop&w=800&q=80',
    'w-cs-40-fila-disruptor-ii-premium-white': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80',
    'm-rc-13-air-jordan-4-retro-bred': 'https://images.unsplash.com/photo-1556906781-9a412961c28c?auto=format&fit=crop&w=800&q=80',
    'm-rc-15-nike-air-max-90-infrared-vintage': 'https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?auto=format&fit=crop&w=800&q=80',
    'm-rp-12-nike-tempo-next-flyknit': 'https://images.unsplash.com/photo-1511556532299-8f662fc26c06?auto=format&fit=crop&w=800&q=80',
}

# Replace image_url for each item in the file content
for code, new_url in REPLACEMENTS.items():
    # Append &sku=<code> to guarantee uniqueness constraint in database
    unique_url = f"{new_url}&sku={code}"
    pattern = rf"('code':\s*'{re.escape(code)}'[\s\S]*?'image_url':\s*')[^']+(\')"
    
    match = re.search(pattern, content)
    if match:
        content = re.sub(
            pattern,
            rf"\g<1>{unique_url}\g<2>",
            content,
            count=1
        )
        print(f"Updated {code} -> {unique_url}")
    else:
        print(f"WARNING: Pattern not found for {code}")

with open(SEEDS_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished updating seed_catalog.py successfully!")
