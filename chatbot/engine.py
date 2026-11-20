"""
SNEAKER SQUAD - PANDAS RULE-BASED CHATBOT ENGINE (engine.py)
-----------------------------------------------------------
Final-Year CS Project Architecture:
1. get_df(): Loads in-stock products from Django ORM into a pandas DataFrame.
2. get_orders_df(user): Loads customer orders into a pandas DataFrame for order tracking.
3. get_offers_df(): Loads active promo codes from Offer model into a pandas DataFrame.
4. detect_intent(message): Matches user query using regular expressions in strict priority order.
5. extract_entities(message): Extracts brand, color, size, and price constraints.
6. search_products(df, entities): Filters & sorts DataFrame with boolean indexing.
7. get_reply(message, user): Main function returning JSON-compatible dict with text & product cards.
"""

import re
import difflib
try:
    import pandas as pd
except ImportError:
    pd = None
from django.db.models import Q
from accounts.models import Product, Order, WishlistItem
from .models import Offer


# ==============================================================================
# 1. DATA LOADER FUNCTIONS (Django ORM -> pandas DataFrames)
# ==============================================================================

def get_df():
    """
    Loads active in-stock products into a pandas DataFrame.
    Adds lowercase helper columns for fast case-insensitive filtering.
    Handles empty database gracefully without crashing.
    """
    columns = [
        'id', 'name', 'brand', 'price', 'color', 'size',
        'category', 'gender', 'stock', 'sales', 'rating', 'main_image', 'description'
    ]
    try:
        products = Product.objects.filter(is_active=True, is_in_stock=True)
        data = []
        for p in products:
            # Extract color hints from name, tag, or description
            full_text = f"{p.name} {p.tag} {p.description or ''}".lower()
            detected_colors = []
            for c in ['black', 'white', 'red', 'blue', 'green', 'pink', 'silver', 'cream', 'orange', 'purple', 'grey', 'yellow', 'brown']:
                if c in full_text:
                    detected_colors.append(c)
            color_str = ", ".join(detected_colors) if detected_colors else (p.tag or '')

            data.append({
                'id': p.code or str(p.id),
                'name': p.name,
                'brand': p.brand or 'Sneaker Squad',
                'price': float(p.price),
                'color': color_str,
                'size': p.size or p.sizes_list or 'UK 6, UK 7, UK 8, UK 9, UK 10, UK 11',
                'category': (p.category.slug if hasattr(p.category, 'slug') else str(p.category or 'sneaker')).lower(),
                'gender': str(p.gender or 'men').lower(),
                'stock': p.stock_quantity,
                'sales': p.reviews_count or 0,  # Proxy for popularity/sales
                'rating': float(p.rating or 4.5),
                'main_image': p.image_url or p.image or p.main_image or '/static/img/shoe-1.jpg',
                'description': p.description or ''
            })

        if not data:
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(data)

        # Pre-compute lowercase helper columns for fast regex & string matching
        df['name_lower'] = df['name'].str.lower()
        df['brand_lower'] = df['brand'].str.lower()
        df['category_lower'] = df['category'].astype(str).str.lower()
        df['gender_lower'] = df['gender'].astype(str).str.lower()
        df['color_lower'] = df['color'].str.lower()
        df['size_lower'] = df['size'].str.lower()
        return df

    except Exception as e:
        print(f"[Chatbot Engine] Error loading products DataFrame: {e}")
        return pd.DataFrame(columns=columns)


def get_orders_df(user):
    """
    Loads orders of a logged-in user into a pandas DataFrame.
    """
    columns = ['order_id', 'status', 'created_at', 'expected_delivery', 'total_amount', 'courier_partner', 'tracking_number', 'items_summary']
    if not user or not user.is_authenticated:
        return pd.DataFrame(columns=columns)

    try:
        user_orders = Order.objects.filter(
            Q(user=user) | Q(email__iexact=user.email)
        ).prefetch_related('items').order_by('-created_at')

        data = []
        for o in user_orders:
            items_list = [f"{item.product_name} (Size: {item.size or 'Standard'})" for item in o.items.all()]
            data.append({
                'order_id': o.order_id,
                'status': o.status,
                'created_at': o.created_at.strftime("%d %b %Y"),
                'expected_delivery': o.estimated_delivery or '2-4 Business Days',
                'total_amount': float(o.total_amount),
                'courier_partner': o.courier_partner or 'Blue Dart Express',
                'tracking_number': o.tracking_number or 'BD-00000000',
                'items_summary': ", ".join(items_list) if items_list else "Sneaker Squad Kicks"
            })

        if not data:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(data)

    except Exception as e:
        print(f"[Chatbot Engine] Error loading orders DataFrame: {e}")
        return pd.DataFrame(columns=columns)


def get_offers_df():
    """
    Loads active promotional coupons from the Offer table.
    """
    columns = ['code', 'description', 'discount_percent', 'active']
    try:
        offers = Offer.objects.filter(active=True)
        data = []
        for off in offers:
            data.append({
                'code': off.code,
                'description': off.description,
                'discount_percent': off.discount_percent,
                'active': off.active
            })
        if not data:
            # Fallback static offers if database has none
            data = [
                {'code': 'SQUAD20', 'description': 'Flat 20% discount on entire cart', 'discount_percent': 20, 'active': True},
                {'code': 'FIRST10', 'description': '10% instant off on your first order', 'discount_percent': 10, 'active': True},
                {'code': 'FREESHIP', 'description': 'Free express shipping on all orders over ₹2,999', 'discount_percent': 0, 'active': True}
            ]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"[Chatbot Engine] Error loading offers DataFrame: {e}")
        return pd.DataFrame(columns=columns)


# ==============================================================================
# 2. STATIC FAQ KNOWLEDGE BASE
# ==============================================================================

FAQ_KNOWLEDGE_BASE = {
    'shipping': (
        "🚚 **Delivery & Shipping Details:**\n"
        "• Hum poore India me **Blue Dart Air Express** se deliver karte hain.\n"
        "• Delivery time: **2 se 4 business days** lagte hain.\n"
        "• **Shipping Charges:** ₹2,999 se upar ke orders par shipping bilkul **FREE** hai! (Baki orders par ₹150 flat fee lagti hai).\n"
        "• Har order ke dispatch hone ke baad SMS aur Email par tracking number mil jata hai."
    ),
    'return': (
        "🔄 **Return & Exchange Policy:**\n"
        "• Agar size fit nahi hua ya design pasand nahi aaya, toh **7 Days Easy Return & Exchange** available hai!\n"
        "• Sneakers unused aur original box/tags ke saath hone chahiye.\n"
        "• Exchange request ke liye aap direct Dashboard ya support par WhatsApp/Call kar sakte hain.\n"
        "• Refund item pick-up hone ke **24-48 hours** ke andar aapke bank account / UPI me credit ho jata hai."
    ),
    'payment': (
        "💳 **Payment Options:**\n"
        "• **Cash on Delivery (COD)** available hai.\n"
        "• **Instant Online Payment:** UPI (GPay, PhonePe, Paytm), Debit/Credit Cards (Visa, Mastercard, RuPay), aur NetBanking.\n"
        "• ⚠️ **Agar paisa kat gaya aur order place nahi hua:** Chinta mat kijiye! Banking switch delay ki wajah se 2-3 ghante me refund ho jata hai, ya aap transaction screenshot ke sath support number par WhatsApp karein."
    ),
    'support': (
        "📞 **Sneaker Squad Customer Support:**\n"
        "• **Phone / WhatsApp:** +91 74882 91737 (Subah 10:00 AM se Shaam 8:00 PM)\n"
        "• **Official Email:** chandankumarsharma813@gmail.com\n"
        "• Hamari support team aapke queries ko 24 ghante ke andar solve karti hai!"
    ),
    'size_chart': (
        "📏 **Sneaker Squad Standard Size Guide:**\n\n"
        "| UK / IND | US Men | Euro (EU) | Foot Length |\n"
        "|---|---|---|---|\n"
        "| **UK 6**  | US 7.0  | EU 40.0   | 25.0 cm     |\n"
        "| **UK 7**  | US 8.0  | EU 41.0   | 26.0 cm     |\n"
        "| **UK 8**  | US 9.0  | EU 42.5   | 27.0 cm     |\n"
        "| **UK 9**  | US 10.0 | EU 44.0   | 28.0 cm     |\n"
        "| **UK 10** | US 11.0 | EU 45.0   | 29.0 cm     |\n"
        "| **UK 11** | US 12.0 | EU 46.0   | 30.0 cm     |\n\n"
        "💡 *Tip: Sneakers true-to-size fit karte hain. Wide feet ke liye half size up le sakte hain.*"
    ),
    'account': (
        "🔐 **Account & Password Help:**\n"
        "• Password reset karne ke liye aap [Forgot Password Page](/reset-password/) open karke registered email par 6-digit OTP mangwa sakte hain.\n"
        "• New account banana bohot aasan hai — header par Profile icon dabayein aur 'Create Account' par click karein!"
    ),
    'original': (
        "🛡️ **100% Authenticity Guarantee:**\n"
        "• Humare platform ke saare sneakers **100% Deadstock Verified & Authentic** hote hain.\n"
        "• Har pair dispatch se pehle hamare squad specialists se multi-point physical verification ke baad hi ship hota hai."
    )
}


# ==============================================================================
# 3. INTENT DETECTION & ENTITY EXTRACTION
# ==============================================================================

def detect_intent(message):
    """
    Detects user intent using regular expressions.
    PRIORITY ORDER:
    0. SNEAKER FINDER QUIZ (Decision Tree)
    0. SNEAKER COMPARISON (Side-by-side Head-to-Head)
    0. VALUE FOR MONEY (VFM Deal Finder)
    0. SIMILAR SNEAKERS (Content-based Similarity)
    1. RECOMMENDATION
    2. PRODUCT SEARCH
    3. ORDER STATUS
    4. OFFERS / DISCOUNT
    5. DELIVERY / SHIPPING
    6. RETURN / EXCHANGE / REFUND
    7. PAYMENT
    8. PRODUCT DETAIL / AUTHENTICITY / SIZE CHART
    9. ACCOUNT / SUPPORT
    10. GREETING
    11. FALLBACK
    """
    msg = message.lower().strip()

    # 0. SNEAKER FINDER QUIZ (Interactive Decision Tree)
    if msg.startswith('quiz:') or msg == 'quiz' or re.search(r'\b(quiz|finder|find\s*my\s*sneaker|sneaker\s*finder|perfect\s*shoe|dhundho|dhundo|suggest\s*for\s*me)\b', msg):
        return 'quiz'

    # 0. SNEAKER COMPARISON (Side-by-side Head-to-Head)
    if re.search(r'\b(compare|vs|versus|difference\s*between|kaunsa\s*behtar|kaun\s*sa\s*accha|konsa\s*acha|better\s*kaun|which\s*is\s*better)\b', msg):
        return 'compare'

    # 0. VALUE FOR MONEY (VFM Deal Finder)
    if re.search(r'\b(vfm|value\s*for\s*money|paisa\s*vasool|best\s*deal|best\s*value|value\s*deal|budget\s*optimizer)\b', msg):
        return 'vfm'

    # 0. CONTENT-BASED SIMILAR SNEAKERS
    if msg.startswith('similar:') or re.search(r'\b(similar\s*to|like\s*this|aisa\s*aur|milta\s*julta|same\s*type)\b', msg):
        return 'similar'

    # 1. RECOMMENDATION (Must run before search so 'recommend shoes' is not treated as search)
    rec_pattern = r'\b(recommend|recommendation|suggest|suggestion|trending|popular|best\s*seller|bestseller|best\s*selling|top\s*rated|new\s*arrival|latest\s*drop|similar|gift|kuch\s*acha|kya\s*lu|kya\s*khareedu|kya\s*kharidu|acha\s*shoe|choice|batao|options)\b'
    if re.search(rec_pattern, msg):
        return 'recommendation'

    # 2. ORDER STATUS
    order_pattern = r'\b(order|track|tracking|kahan\s*hai|kab\s*aayega|status|cancel|package|delivery\s*status|pata\s*karo|mera\s*joota|parcel|aaya\s*nahi)\b'
    if re.search(order_pattern, msg) and not re.search(r'\b(place\s*order|order\s*karna)\b', msg):
        return 'order_status'

    # 3. OFFERS / DISCOUNT
    offer_pattern = r'\b(offer|offers|discount|coupon|promo|voucher|code|deal|loot|discounts|squad20|kam\s*karo|chhoot|koi\s*code|kam\s*karwao)\b'
    if re.search(offer_pattern, msg):
        return 'offers'

    # 4. DELIVERY / SHIPPING
    delivery_pattern = r'\b(delivery|shipping|ship|courier|dispatch|pincode|charge|charges|kitne\s*din|free\s*shipping|kab\s*milega)\b'
    if re.search(delivery_pattern, msg):
        return 'delivery'

    # 5. RETURN / EXCHANGE / REFUND
    return_pattern = r'\b(return|exchange|refund|replace|replacement|fit\s*nahi|size\s*problem|return\s*policy|wapas|badalna)\b'
    if re.search(return_pattern, msg):
        return 'return'

    # 6. PAYMENT
    payment_pattern = r'\b(payment|pay|cod|cash\s*on\s*delivery|upi|qr|gpay|phonepe|paytm|card|netbanking|paisa\s*kat|fail|failed)\b'
    if re.search(payment_pattern, msg):
        return 'payment'

    # 7. PRODUCT DETAIL / AUTHENTICITY / SIZE CHART
    detail_pattern = r'\b(original|authentic|asli|fake|size\s*chart|chart|material|leather|quality|running|comfort|gym|basketball)\b'
    if re.search(detail_pattern, msg):
        return 'product_detail'

    # 8. ACCOUNT / SUPPORT
    support_pattern = r'\b(account|login|signup|register|password|bhool|reset|support|care|customer\s*care|contact|phone\s*number|call|email|help|madad)\b'
    if re.search(support_pattern, msg):
        return 'support'

    # 9. GREETING
    greeting_pattern = r'^(hi|hello|hey|namaste|pranam|halo|good\s*morning|good\s*evening|sup|yo|hii|hiii|hola)\b'
    if re.search(greeting_pattern, msg):
        return 'greeting'

    # 10. PRODUCT SEARCH (Brands, Colors, Prices, Keywords)
    search_keywords = r'\b(shoe|shoes|sneaker|sneakers|kicks|joota|joote|juta|daam|rate|keemat|price|nike|jordan|adidas|puma|asics|balenciaga|converse|new\s*balance|under|below|sasta|saste|cheapest|upto|above|dikhao|available|stock|size|white|black|red|blue|green|pink)\b'
    if re.search(search_keywords, msg):
        return 'product_search'

    # Fuzzy check: If user typed brand with typo (e.g. 'addidas', 'pooma', 'naiki')
    known_brands_quick = ['nike', 'jordan', 'adidas', 'puma', 'asics', 'balenciaga', 'converse', 'new balance']
    words_quick = re.findall(r'[a-zA-Z]+', msg)
    for w in words_quick:
        if difflib.get_close_matches(w, known_brands_quick, n=1, cutoff=0.72):
            return 'product_search'

    # 11. FALLBACK
    return 'fallback'


def extract_entities(message):
    """
    Extracts structured entities from user query:
    - brand (with fuzzy difflib matching)
    - color (with fuzzy difflib matching)
    - size
    - min_price, max_price
    - cheapest (boolean flag)
    """
    msg = message.lower()
    entities = {
        'brand': None,
        'color': None,
        'size': None,
        'min_price': None,
        'max_price': None,
        'cheapest': False
    }

    # Brand extraction (Exact Regex First)
    known_brands = ['nike', 'jordan', 'adidas', 'puma', 'asics', 'balenciaga', 'converse', 'new balance', 'squad']
    for b in known_brands:
        if re.search(rf'\b{b}\b', msg):
            entities['brand'] = b
            break

    # Brand Fuzzy Fallback (Handles typos like 'addidas', 'pooma', 'naiki', 'jordn')
    if not entities['brand']:
        words = re.findall(r'[a-zA-Z]+', msg)
        for w in words:
            fuzzy_match = difflib.get_close_matches(w, known_brands, n=1, cutoff=0.72)
            if fuzzy_match:
                entities['brand'] = fuzzy_match[0]
                break

    # Color extraction (Exact Regex First, including Hindi/Hinglish colors)
    hindi_colors = {
        'safed': 'white', 'chitta': 'white',
        'kaala': 'black', 'kala': 'black',
        'laal': 'red', 'lal': 'red',
        'neela': 'blue', 'nila': 'blue',
        'peela': 'yellow', 'pila': 'yellow',
        'gulabi': 'pink', 'pinki': 'pink',
        'hara': 'green', 'sabz': 'green',
        'bhura': 'brown', 'bhoora': 'brown'
    }
    for h_col, eng_col in hindi_colors.items():
        if re.search(rf'\b{h_col}\b', msg):
            entities['color'] = eng_col
            break

    if not entities['color']:
        known_colors = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'pink', 'grey', 'gray', 'silver', 'cream', 'orange', 'purple', 'brown']
        for c in known_colors:
            if re.search(rf'\b{c}\b', msg):
                entities['color'] = 'grey' if c == 'gray' else c
                break

    # Color Fuzzy Fallback (Handles typos like 'wite', 'blck', 'gren')
    if not entities['color']:
        words = re.findall(r'[a-zA-Z]+', msg)
        for w in words:
            fuzzy_c = difflib.get_close_matches(w, known_colors, n=1, cutoff=0.75)
            if fuzzy_c:
                matched_c = fuzzy_c[0]
                entities['color'] = 'grey' if matched_c == 'gray' else matched_c
                break

    # Size extraction (e.g. "size 8", "uk 9", "size 10")
    size_match = re.search(r'\b(?:size|uk)\s*([6-9]|1[0-2])\b', msg)
    if size_match:
        entities['size'] = f"UK {size_match.group(1)}"
    else:
        # Standalone number matching sneaker sizes
        stand_match = re.search(r'\b([6-9]|1[0-2])\s*(?:no|number)?\b', msg)
        if stand_match and ('under' not in msg and 'below' not in msg and 'rs' not in msg and '₹' not in msg):
            # Only consider as size if it's not a price
            entities['size'] = f"UK {stand_match.group(1)}"

    # Price extraction
    # Case A: "under 3000", "below 5000", "upto 4000", "3000 ke andar", "< 4000"
    max_match = re.search(r'(?:under|below|upto|less\s*than|ke\s*andar|<\s*)\s*(?:rs\.?|inr|₹)?\s*(\d{3,6})', msg)
    if max_match:
        entities['max_price'] = float(max_match.group(1))

    # Case B: "above 2000", "more than 3000", "> 2000"
    min_match = re.search(r'(?:above|more\s*than|greater\s*than|se\s*jyada|>\s*)\s*(?:rs\.?|inr|₹)?\s*(\d{3,6})', msg)
    if min_match:
        entities['min_price'] = float(min_match.group(1))

    # Case C: "between 2000 and 5000"
    between_match = re.search(r'between\s*(\d{3,6})\s*(?:and|to|-)\s*(\d{3,6})', msg)
    if between_match:
        entities['min_price'] = float(between_match.group(1))
        entities['max_price'] = float(between_match.group(2))

    # Case D: "Cheapest" / "Sasta" / Hinglish Slang
    if re.search(r'\b(cheapest|sasta|saste|sabse\s*sasta|low\s*price|lowest\s*price|kam\s*daam|kam\s*rate|kam\s*paisa|kam\s*budget|saste\s*me|paisa\s*kam|budget\s*me)\b', msg):
        entities['cheapest'] = True

    return entities


# ==============================================================================
# 4. PANDAS FILTERING & SEARCH ENGINE
# ==============================================================================

def search_products(df, entities):
    """
    Filters and sorts the products DataFrame using pandas boolean indexing.
    Returns top 5 matched products as list of dictionaries.
    """
    if df.empty:
        return []

    filtered_df = df.copy()

    # 1. Filter by Brand
    if entities.get('brand'):
        b = entities['brand'].lower()
        filtered_df = filtered_df[filtered_df['brand_lower'].str.contains(b, na=False) | filtered_df['name_lower'].str.contains(b, na=False)]

    # 2. Filter by Color
    if entities.get('color'):
        c = entities['color'].lower()
        filtered_df = filtered_df[
            filtered_df['color_lower'].str.contains(c, na=False) |
            filtered_df['name_lower'].str.contains(c, na=False)
        ]

    # 3. Filter by Size
    if entities.get('size'):
        s = entities['size'].lower()
        filtered_df = filtered_df[filtered_df['size_lower'].str.contains(s, na=False)]

    # 4. Filter by Max Price
    if entities.get('max_price') is not None:
        filtered_df = filtered_df[filtered_df['price'] <= entities['max_price']]

    # 5. Filter by Min Price
    if entities.get('min_price') is not None:
        filtered_df = filtered_df[filtered_df['price'] >= entities['min_price']]

    # If strict filtering returned nothing, relax filters slightly for beginner-friendly UX
    if filtered_df.empty:
        # Fallback to brand or price only
        if entities.get('brand'):
            b = entities['brand'].lower()
            filtered_df = df[df['brand_lower'].str.contains(b, na=False)]
        elif entities.get('max_price'):
            filtered_df = df[df['price'] <= entities['max_price']]
        else:
            filtered_df = df.head(5)

    # 6. Sorting
    if entities.get('cheapest'):
        filtered_df = filtered_df.sort_values(by='price', ascending=True)
    else:
        # Sort by rating and popularity
        filtered_df = filtered_df.sort_values(by=['rating', 'sales', 'price'], ascending=[False, False, True])

    top_5 = filtered_df.head(5)

    results = []
    for _, row in top_5.iterrows():
        results.append({
            'id': row['id'],
            'name': row['name'],
            'brand': row['brand'],
            'price': int(row['price']),
            'color': row['color'],
            'rating': float(row['rating']),
            'image': row['main_image'],
            'url': f"/product-detail?id={row['id']}"
        })
    return results


# ==============================================================================
# 5. RECOMMENDATION ENGINE (PANDAS-BASED)
# ==============================================================================

def get_recommendations(df, message, user=None):
    """
    Computes personalized or trending sneaker recommendations using pandas.
    - If user is logged in and has wishlist/orders, personalizes recommendations!
    - "trending" / "bestseller" -> sorts by sales (reviews count).
    - "top rated" -> sorts by rating descending.
    - "new arrival" -> sorts by id/created order.
    """
    if df.empty:
        return "Filhal koi recommendations available nahi hain.", []

    msg = message.lower()
    rec_df = df.copy()

    # 1. Personalized Recommendation for Logged-In Users
    if user and user.is_authenticated:
        try:
            wishlist_ids = list(WishlistItem.objects.filter(user=user).values_list('product_id', flat=True))
            if wishlist_ids:
                # Find categories of shoes in user's wishlist
                fav_prods = df[df['id'].isin(wishlist_ids)]
                if not fav_prods.empty:
                    fav_brands = fav_prods['brand_lower'].tolist()
                    personalized = rec_df[rec_df['brand_lower'].isin(fav_brands) & ~rec_df['id'].isin(wishlist_ids)]
                    if not personalized.empty:
                        top_items = personalized.sort_values(by='rating', ascending=False).head(4)
                        prods = [{
                            'id': r['id'], 'name': r['name'], 'brand': r['brand'],
                            'price': int(r['price']), 'rating': float(r['rating']),
                            'color': r['color'], 'image': r['main_image'],
                            'url': f"/product-detail?id={r['id']}"
                        } for _, r in top_items.iterrows()]
                        return f"Aapke wishlist preferences ke basis par humne yeh premium kicks shortlist kiye hain, {user.first_name or user.username}:", prods
        except Exception:
            pass

    # 2. Top Rated
    if 'top rated' in msg or 'best rating' in msg or 'highest rated' in msg:
        top_rated = rec_df.sort_values(by=['rating', 'sales'], ascending=[False, False]).head(5)
        prods = [{
            'id': r['id'], 'name': r['name'], 'brand': r['brand'],
            'price': int(r['price']), 'rating': float(r['rating']),
            'color': r['color'], 'image': r['main_image'],
            'url': f"/product-detail?id={r['id']}"
        } for _, r in top_rated.iterrows()]
        return "Ye rahe Sneaker Squad ke **Highest Rated (4.9★+)** kicks:", prods

    # 3. New Arrival / Latest
    if 'new arrival' in msg or 'latest' in msg or 'fresh' in msg:
        new_kicks = rec_df.tail(5)  # Recent additions
        prods = [{
            'id': r['id'], 'name': r['name'], 'brand': r['brand'],
            'price': int(r['price']), 'rating': float(r['rating']),
            'color': r['color'], 'image': r['main_image'],
            'url': f"/product-detail?id={r['id']}"
        } for _, r in new_kicks.iterrows()]
        return "⚡ Ye rahe hamare **Latest Drops & New Arrivals**:", prods

    # 4. Default Trending / Bestseller (Sort by sales/reviews count)
    trending = rec_df.sort_values(by=['sales', 'rating'], ascending=[False, False]).head(5)
    prods = [{
        'id': r['id'], 'name': r['name'], 'brand': r['brand'],
        'price': int(r['price']), 'rating': float(r['rating']),
        'color': r['color'], 'image': r['main_image'],
        'url': f"/product-detail?id={r['id']}"
    } for _, r in trending.iterrows()]
    return "🔥 Ye rahe Sneaker Squad ke sabse **Trending & Bestselling Kicks**:", prods


# ==============================================================================
# 5B. SNEAKER COMPARISON ENGINE (Head-to-Head Comparison Table & Verdict)
# ==============================================================================

def compare_sneakers(df, message):
    """
    Compares two sneakers side-by-side using DataFrame extraction and ranking.
    Generates a Markdown comparison table and an explainable AI verdict.
    """
    if df.empty:
        return "Comparison ke liye catalog me sneakers uplabdh nahi hain.", []

    msg = message.lower()
    cleaned = re.sub(r'\b(compare|sneakers?|kicks|shoes?|b/w|between)\b', '', msg).strip()
    parts = re.split(r'\b(?:vs|versus|and|aur|ya|,)\b', cleaned)

    found_rows = []
    if len(parts) >= 2:
        part1 = parts[0].strip()
        part2 = parts[1].strip()

        # Match Part 1
        m1 = df[df['name_lower'].str.contains(part1, regex=False, na=False) | df['brand_lower'].str.contains(part1, regex=False, na=False)]
        if m1.empty and len(part1) > 2:
            matches = difflib.get_close_matches(part1, df['name_lower'].tolist(), n=1, cutoff=0.45)
            if matches:
                m1 = df[df['name_lower'] == matches[0]]

        # Match Part 2
        m2 = df[df['name_lower'].str.contains(part2, regex=False, na=False) | df['brand_lower'].str.contains(part2, regex=False, na=False)]
        if m2.empty and len(part2) > 2:
            matches = difflib.get_close_matches(part2, df['name_lower'].tolist(), n=1, cutoff=0.45)
            if matches:
                m2 = df[df['name_lower'] == matches[0]]

        if not m1.empty:
            found_rows.append(m1.iloc[0])
        if not m2.empty:
            for _, r2 in m2.iterrows():
                if not found_rows or str(r2['id']) != str(found_rows[0]['id']):
                    found_rows.append(r2)
                    break

    # Smart Fallback if 2 specific shoes were not named
    if len(found_rows) < 2:
        top_2 = df.sort_values(by=['sales', 'rating'], ascending=[False, False]).head(2)
        if len(top_2) >= 2:
            found_rows = [top_2.iloc[0], top_2.iloc[1]]
            note = "*(Tip: Aap direct 'Compare Jordan 1 and Jordan 4' likh kar kisi bhi 2 shoes ko compare kar sakte hain!)*\n\n"
        else:
            return "Kripya 2 sneakers ke naam batayein jinhe compare karna hai, jaise: **'Compare Air Jordan 1 vs Nike Air Force 1'**.", []
    else:
        note = ""

    s1 = found_rows[0]
    s2 = found_rows[1]

    p1 = int(s1['price'])
    p2 = int(s2['price'])
    r1 = float(s1['rating'])
    r2 = float(s2['rating'])

    price_diff = abs(p1 - p2)
    if p1 < p2:
        price_verdict = f"**{s1['name']}** ₹{price_diff:,} sasta aur budget-friendly hai"
    elif p2 < p1:
        price_verdict = f"**{s2['name']}** ₹{price_diff:,} sasta aur budget-friendly hai"
    else:
        price_verdict = "Dono shoes ka price barabar hai"

    if r1 > r2:
        rating_verdict = f"**{s1['name']}** ki customer rating behtar hai ({r1}★ vs {r2}★)"
    elif r2 > r1:
        rating_verdict = f"**{s2['name']}** ki customer rating behtar hai ({r2}★ vs {r1}★)"
    else:
        rating_verdict = f"Dono kicks ki rating barabar hai ({r1}★)"

    table = (
        f"| Feature | {s1['name'][:24]} | {s2['name'][:24]} |\n"
        f"|---|---|---|\n"
        f"| **Brand** | {s1['brand']} | {s2['brand']} |\n"
        f"| **Price** | ₹{p1:,} | ₹{p2:,} |\n"
        f"| **Rating** | ⭐ {r1} / 5.0 | ⭐ {r2} / 5.0 |\n"
        f"| **Category** | {s1['category'].title()} | {s2['category'].title()} |\n"
        f"| **Colors** | {s1['color'].title() or 'Classic'} | {s2['color'].title() or 'Classic'} |\n"
    )

    verdict = (
        f"⚖️ **Sneaker Squad Head-to-Head Comparison:**\n\n"
        f"{note}"
        f"{table}\n"
        f"💡 **AI Recommendation & Verdict:**\n"
        f"• **Pricing:** {price_verdict}.\n"
        f"• **Rating:** {rating_verdict}.\n"
        f"• **Style Advice:** Daily comfort aur versatility ke liye **{s1['name']}** aur iconic high-profile streetwear vibe ke liye **{s2['name']}** pick karein!"
    )

    prods = [
        {
            'id': s1['id'], 'name': s1['name'], 'brand': s1['brand'],
            'price': p1, 'rating': r1, 'color': s1['color'],
            'image': s1['main_image'], 'url': f"/product-detail?id={s1['id']}"
        },
        {
            'id': s2['id'], 'name': s2['name'], 'brand': s2['brand'],
            'price': p2, 'rating': r2, 'color': s2['color'],
            'image': s2['main_image'], 'url': f"/product-detail?id={s2['id']}"
        }
    ]
    return verdict, prods


# ==============================================================================
# 5C. 3-STEP SNEAKER FINDER QUIZ (Interactive Decision Tree)
# ==============================================================================

def handle_quiz(df, message):
    """
    3-Step Interactive Decision Tree Sneaker Finder.
    Branches:
    quiz:res:<g>:<s>:<b> -> Evaluates DataFrame and returns top matches.
    quiz:style:<s>:<g> -> Step 3 (Budget)
    quiz:men / women / unisex -> Step 2 (Occasion/Style)
    quiz:start (default) -> Step 1 (Gender)
    """
    msg = message.strip()

    # Step 4: Final Decision Tree Evaluation (Checked first for precise match)
    res_match = re.match(r'quiz:res:([a-z]+):([a-z]+):(\d+)', msg)
    if res_match:
        g, s, b_str = res_match.groups()
        budget = int(b_str)

        q_df = df.copy()
        # Branch 1: Gender Filter
        if g in ['men', 'women']:
            q_df = q_df[q_df['gender_lower'].isin([g, 'unisex'])]

        # Branch 2: Budget Filter
        if budget == 3500:
            b_df = q_df[q_df['price'] <= 3500]
        elif budget == 6500:
            b_df = q_df[(q_df['price'] >= 3000) & (q_df['price'] <= 6500)]
        else:
            b_df = q_df[q_df['price'] >= 5000]

        if not b_df.empty:
            q_df = b_df

        # Branch 3: Style / Category Filter
        style_keywords = {
            'streetwear': ['streetwear', 'retro', 'jordan', 'dunk', 'high', 'air force'],
            'running': ['running', 'zoom', 'pegasus', 'air max', 'cushion', 'runner', 'sport'],
            'retro': ['retro', 'vintage', 'classic', 'og', 'jordan', 'chicago'],
            'minimalist': ['white', 'minimal', 'clean', 'stan smith', 'classic', 'low']
        }
        kw_list = style_keywords.get(s, [s])
        kw_pattern = '|'.join(kw_list)
        s_df = q_df[q_df['name_lower'].str.contains(kw_pattern, regex=True, na=False) | q_df['description'].str.lower().str.contains(kw_pattern, regex=True, na=False)]
        if not s_df.empty:
            q_df = s_df

        top_kicks = q_df.sort_values(by=['rating', 'sales'], ascending=[False, False]).head(3)
        if top_kicks.empty:
            top_kicks = df.head(3)

        prods = [{
            'id': r['id'], 'name': r['name'], 'brand': r['brand'],
            'price': int(r['price']), 'rating': float(r['rating']),
            'color': r['color'], 'image': r['main_image'],
            'url': f"/product-detail?id={r['id']}"
        } for _, r in top_kicks.iterrows()]

        text = (
            f"🎉 **Perfect Match Found! (Decision Tree Result)**\n\n"
            f"Aapke preferences (**{g.capitalize()} • {s.title()} • ₹{budget:,} budget**) ke mutabiq "
            f"ye rahe **98% Lifestyle Match** kicks:"
        )
        quick = [
            {"label": "🔄 Retake Quiz", "query": "quiz:start"},
            {"label": "🔥 Trending Kicks", "query": "Trending sneakers dikhao"},
            {"label": "⚖️ Compare These", "query": f"Compare {prods[0]['name']} and {prods[1]['name']}" if len(prods) > 1 else "quiz:start"}
        ]
        return text, prods, quick

    # Step 3: Style chosen -> Choose Budget
    style_match = re.match(r'quiz:style:([a-z]+):([a-z]+)', msg)
    if style_match:
        s, g = style_match.groups()
        s_label = s.title()
        text = (
            f"🎯 **Sneaker Squad Smart Finder (Step 3 of 3) — [{s_label}]**\n\n"
            "Aapka budget kitna hai? 👇"
        )
        quick = [
            {"label": "💰 Under ₹3,500", "query": f"quiz:res:{g}:{s}:3500"},
            {"label": "✨ ₹3,500 - ₹6,500", "query": f"quiz:res:{g}:{s}:6500"},
            {"label": "💎 Premium (₹6,500+)", "query": f"quiz:res:{g}:{s}:99999"}
        ]
        return text, [], quick

    # Step 2: Gender chosen -> Choose Style/Occasion
    if msg in ['quiz:men', 'quiz:women', 'quiz:unisex']:
        g = msg.replace('quiz:', '')
        g_label = "Men" if g == 'men' else ("Women" if g == 'women' else "Unisex")
        text = (
            f"🎯 **Sneaker Squad Smart Finder (Step 2 of 3) — [{g_label}]**\n\n"
            "Aapko kis style ya occasion ke liye sneaker chahiye? 👇"
        )
        quick = [
            {"label": "🔥 Daily Streetwear", "query": f"quiz:style:streetwear:{g}"},
            {"label": "🏃 Running & Gym", "query": f"quiz:style:running:{g}"},
            {"label": "🎉 Retro Classics", "query": f"quiz:style:retro:{g}"},
            {"label": "👟 Minimalist Clean", "query": f"quiz:style:minimalist:{g}"}
        ]
        return text, [], quick

    # Step 1: Start Quiz (Default for 'quiz:start', 'quiz', or any quiz trigger)
    text = (
        "🎯 **Sneaker Squad Smart Finder (Step 1 of 3)**\n\n"
        "Aap kiske liye sneaker dhoondh rahe hain? Neeche diye kisi option par click karein: 👇"
    )
    quick = [
        {"label": "👨 Men's Kicks", "query": "quiz:men"},
        {"label": "👩 Women's Kicks", "query": "quiz:women"},
        {"label": "⚡ Anyone / Unisex", "query": "quiz:unisex"}
    ]
    return text, [], quick


# ==============================================================================
# 5D. VALUE-FOR-MONEY (VFM) BUDGET OPTIMIZER
# ==============================================================================

def get_vfm_deals(df, message):
    """
    Computes algorithmic Value-For-Money (VFM) score:
    VFM = (Rating * (Sales + 15)) / (Price / 1000)
    Ranks sneakers providing maximum customer satisfaction per rupee spent.
    """
    if df.empty:
        return "Filhal koi VFM deals available nahi hain.", []

    vfm_df = df.copy()
    entities = extract_entities(message)
    if entities.get('max_price'):
        vfm_df = vfm_df[vfm_df['price'] <= entities['max_price']]

    vfm_df['vfm_score'] = (vfm_df['rating'] * (vfm_df['sales'] + 15)) / (vfm_df['price'] / 1000.0)
    top_vfm = vfm_df.sort_values(by='vfm_score', ascending=False).head(3)

    prods = [{
        'id': r['id'], 'name': r['name'], 'brand': r['brand'],
        'price': int(r['price']), 'rating': float(r['rating']),
        'color': r['color'], 'image': r['main_image'],
        'url': f"/product-detail?id={r['id']}"
    } for _, r in top_vfm.iterrows()]

    budget_text = f" (Under ₹{int(entities['max_price']):,})" if entities.get('max_price') else ""
    text = (
        f"💡 **Top Paisa-Vasool (VFM) Kicks{budget_text}:**\n\n"
        f"Humne algorithmic price-to-performance ratio analyze kiya hai. Ye sneakers sabse kam budget me "
        f"highest customer rating (4.8★+) aur durability deliver karte hain:"
    )
    return text, prods


# ==============================================================================
# 5E. CONTENT-BASED SIMILAR SNEAKERS (Multi-Attribute Distance)
# ==============================================================================

def get_similar_sneakers(df, message):
    """
    Content-Based Multi-Attribute Distance algorithm:
    Brand match: +30 pts
    Category match: +25 pts
    Color overlap: +25 pts
    Price proximity: +20 pts
    """
    if df.empty:
        return "Catalog empty hai.", []

    msg = message.lower()
    clean = re.sub(r'\b(similar:|similar\s*to|like\s*this|aisa\s*aur|milta\s*julta|same\s*type)\b', '', msg).strip()

    ref_match = df[df['name_lower'].str.contains(clean, regex=False, na=False) | (df['id'].astype(str) == clean)]
    if ref_match.empty and len(clean) > 2:
        matches = difflib.get_close_matches(clean, df['name_lower'].tolist(), n=1, cutoff=0.45)
        if matches:
            ref_match = df[df['name_lower'] == matches[0]]

    if ref_match.empty:
        ref_shoe = df.iloc[0]
    else:
        ref_shoe = ref_match.iloc[0]

    ref_id = str(ref_shoe['id'])
    ref_brand = str(ref_shoe['brand_lower'])
    ref_color = str(ref_shoe['color_lower'])
    ref_cat = str(ref_shoe['category_lower'])
    ref_price = float(ref_shoe['price'])

    candidates = df[df['id'].astype(str) != ref_id].copy()
    if candidates.empty:
        return "Similar sneakers nahi mile.", []

    def calc_score(row):
        score = 0
        if row['brand_lower'] == ref_brand:
            score += 30
        if row['category_lower'] == ref_cat:
            score += 25
        c_words = set(re.findall(r'[a-z]+', str(row['color_lower'])))
        ref_words = set(re.findall(r'[a-z]+', ref_color))
        if c_words and ref_words and c_words.intersection(ref_words):
            score += 25
        p = float(row['price'])
        max_p = max(p, ref_price, 1)
        proximity = 1.0 - (abs(p - ref_price) / max_p)
        score += max(0, proximity * 20)
        return score

    candidates['similarity'] = candidates.apply(calc_score, axis=1)
    top_sim = candidates.sort_values(by='similarity', ascending=False).head(3)

    prods = [{
        'id': r['id'], 'name': r['name'], 'brand': r['brand'],
        'price': int(r['price']), 'rating': float(r['rating']),
        'color': r['color'], 'image': r['main_image'],
        'url': f"/product-detail?id={r['id']}"
    } for _, r in top_sim.iterrows()]

    text = (
        f"🔍 **Similar Kicks to '{ref_shoe['name']}':**\n\n"
        f"Silhouette style, colorway aur price bracket ke comparison se shortlist kiye gaye top alternatives:"
    )
    return text, prods


# ==============================================================================
# 6. MASTER REPLY GENERATOR (get_reply)
# ==============================================================================

DEFAULT_QUICK_REPLIES = [
    {"label": "🎯 Sneaker Quiz", "query": "quiz:start"},
    {"label": "⚖️ Compare Kicks", "query": "Compare Air Jordan 1 and Air Jordan 4"},
    {"label": "💡 Paisa-Vasool Deals", "query": "Paisa vasool value for money sneakers"},
    {"label": "🔥 Trending Kicks", "query": "Trending sneakers dikhao"},
    {"label": "👟 Nike under 5000", "query": "Nike shoes under 5000"},
    {"label": "💰 Saste Shoes", "query": "Sabse saste shoes dikhao"},
    {"label": "📦 Mera Order", "query": "Mera order kahan hai?"},
    {"label": "🎉 Discount Coupons", "query": "Koi coupon code hai?"},
    {"label": "📏 Size Chart Guide", "query": "Size chart dikhao"}
]


def get_reply(message, user=None, page_context=None):
    """
    Main entry point for Chatbot:
    Takes message string, Django request.user, and page_context ('man', 'woman', 'accessory')
    Returns dictionary: {"text": str, "products": list, "quick_replies": list}
    """
    if pd is None:
        return {
            'text': "Welcome to **Sneaker Squad**! 👟 Our chatbot assistant is warming up. Please browse our latest kicks using the top menu!",
            'products': []
        }
    clean_msg = message.strip()
    if not clean_msg:
        return {
            'text': "Kripya apna sawaal poochein, jaise: *'Nike shoes under 3000'* ya *'Mera order kahan hai?'*",
            'products': []
        }

    intent = detect_intent(clean_msg)
    df = get_df()

    if intent == 'quiz':
        # Quiz manages its own decision tree filtering across the complete catalog
        reply_text, products, quick_replies = handle_quiz(df, clean_msg)
        return {'text': reply_text, 'products': products, 'quick_replies': quick_replies}

    # Apply strict Page Context & Category Rules:
    # 1. man/men context: ONLY gender in ['men', 'unisex'] (non-accessories)
    # 2. woman/women context: ONLY gender in ['women', 'unisex'] (non-accessories)
    # 3. accessory context: ONLY category matching 'accessory'
    ctx = (page_context or '').lower().strip()
    msg_l = clean_msg.lower()

    if ctx in ['man', 'men'] or re.search(r'\b(men|man|mens|gents|male)\b', msg_l):
        df = df[df['gender_lower'].isin(['men', 'unisex']) & (~df['category_lower'].str.contains('accessor', na=False))]
    elif ctx in ['woman', 'women'] or re.search(r'\b(women|woman|womens|ladies|female)\b', msg_l):
        df = df[df['gender_lower'].isin(['women', 'unisex']) & (~df['category_lower'].str.contains('accessor', na=False))]
    elif ctx in ['accessory', 'accessories'] or re.search(r'\b(accessory|accessories|care|cleaner|lace|laces|insole|brush|spray|shoe bag)\b', msg_l):
        df = df[df['category_lower'].str.contains('accessor', na=False)]

    # --------------------------------------------------------------------------
    # INTENT: COMPARE (Side-by-Side Head-to-Head Comparison)
    # --------------------------------------------------------------------------
    if intent == 'compare':
        reply_text, products = compare_sneakers(df, clean_msg)
        return {'text': reply_text, 'products': products}

    # --------------------------------------------------------------------------
    # INTENT: VFM (Value For Money Deal Finder)
    # --------------------------------------------------------------------------
    if intent == 'vfm':
        reply_text, products = get_vfm_deals(df, clean_msg)
        return {'text': reply_text, 'products': products}

    # --------------------------------------------------------------------------
    # INTENT: SIMILAR (Content-Based Attribute Matching)
    # --------------------------------------------------------------------------
    if intent == 'similar':
        reply_text, products = get_similar_sneakers(df, clean_msg)
        return {'text': reply_text, 'products': products}

    # --------------------------------------------------------------------------
    # INTENT 1: RECOMMENDATION
    # --------------------------------------------------------------------------
    if intent == 'recommendation':
        reply_text, products = get_recommendations(df, clean_msg, user=user)
        return {'text': reply_text, 'products': products}

    # --------------------------------------------------------------------------
    # INTENT 2: PRODUCT SEARCH
    # --------------------------------------------------------------------------
    if intent == 'product_search':
        entities = extract_entities(clean_msg)
        products = search_products(df, entities)

        if not products:
            return {
                'text': "Maaf kijiye, aapke search criteria ke mutabiq filhal koi sneaker nahi mila. Aise search karein: *'Adidas under 5000'* ya *'White sneakers size 8'*.",
                'products': []
            }

        # Format pleasant response text
        filters_used = []
        if entities.get('brand'):
            filters_used.append(f"Brand: **{entities['brand'].capitalize()}**")
        if entities.get('color'):
            filters_used.append(f"Color: **{entities['color'].capitalize()}**")
        if entities.get('size'):
            filters_used.append(f"Size: **{entities['size']}**")
        if entities.get('max_price'):
            filters_used.append(f"Under: **₹{int(entities['max_price']):,}**")
        if entities.get('min_price'):
            filters_used.append(f"Above: **₹{int(entities['min_price']):,}**")

        summary = " (" + ", ".join(filters_used) + ")" if filters_used else ""
        intro = "Sabse saste aur best deals ye rahe:" if entities.get('cheapest') else "Aapke search ke mutabiq top kicks ye rahe:"
        return {
            'text': f"👟 {intro}{summary}",
            'products': products
        }

    # --------------------------------------------------------------------------
    # INTENT 3: ORDER STATUS (Logged-in check)
    # --------------------------------------------------------------------------
    if intent == 'order_status':
        if not user or not user.is_authenticated:
            return {
                'text': "🔒 **Order dekhne ke liye pehle login karo.**\n\nAap website ke header me profile icon par click karke login kar sakte hain.",
                'products': []
            }

        orders_df = get_orders_df(user)
        if orders_df.empty:
            return {
                'text': f"Hi {user.first_name or user.username}, aapke account par abhi koi active order nahi mila! Jab aap order karenge toh uska live tracking yahan dikhega.",
                'products': []
            }

        # Check if user asked to cancel
        if 'cancel' in clean_msg.lower():
            return {
                'text': (
                    "⚠️ **Order Cancellation Guide:**\n"
                    "Automated cancellation chatbot se nahi hoti taaki galti se cancel na ho.\n"
                    "Aap direct apne [My Orders Dashboard](/dashboard#orders) par jaakar **Cancel Order** button par click kar sakte hain ya customer support ko message kar sakte hain."
                ),
                'products': []
            }

        # Get latest order
        latest = orders_df.iloc[0]
        status_badges = {
            'CONFIRMED': '✅ Confirmed (Packing in progress)',
            'PACKED': '📦 Packed & Handed over to Courier',
            'SHIPPED': '🚚 Shipped (In Transit)',
            'OUT_FOR_DELIVERY': '🛵 Out for Delivery Today',
            'DELIVERED': '🎉 Delivered Successfully',
            'CANCELLED': '❌ Cancelled'
        }
        status_text = status_badges.get(latest['status'], latest['status'])

        reply = (
            f"📦 **Aapka Latest Order Details:**\n"
            f"• **Order ID:** #{latest['order_id']}\n"
            f"• **Items:** {latest['items_summary']}\n"
            f"• **Total Amount:** ₹{latest['total_amount']:,.2f}\n"
            f"• **Current Status:** {status_text}\n"
            f"• **Expected Delivery:** {latest['expected_delivery']}\n"
            f"• **Courier Partner:** {latest['courier_partner']} (AWB: `{latest['tracking_number']}`)\n\n"
            f"Aap poori invoice aur live tracking [My Orders Dashboard](/dashboard#orders) par dekh sakte hain."
        )
        return {'text': reply, 'products': []}

    # --------------------------------------------------------------------------
    # INTENT 4: OFFERS & DISCOUNTS
    # --------------------------------------------------------------------------
    if intent == 'offers':
        offers_df = get_offers_df()
        if offers_df.empty:
            return {
                'text': "Filhal koi special coupon active nahi hai. Par code **SQUAD20** laga kar aap 20% discount pa sakte hain!",
                'products': []
            }

        offer_lines = []
        for _, row in offers_df.iterrows():
            disc = f"{row['discount_percent']}% OFF" if row['discount_percent'] > 0 else "Free Shipping"
            offer_lines.append(f"• **`{row['code']}`** — {disc} ({row['description']})")

        reply = (
            "🎉 **Active Sneaker Squad Discount Coupons:**\n" +
            "\n".join(offer_lines) +
            "\n\n👉 Checkout page par promo code box me yeh code daal kar **Apply** dabayein!"
        )
        return {'text': reply, 'products': []}

    # --------------------------------------------------------------------------
    # INTENT 5: DELIVERY & SHIPPING
    # --------------------------------------------------------------------------
    if intent == 'delivery':
        return {'text': FAQ_KNOWLEDGE_BASE['shipping'], 'products': []}

    # --------------------------------------------------------------------------
    # INTENT 6: RETURN & EXCHANGE
    # --------------------------------------------------------------------------
    if intent == 'return':
        return {'text': FAQ_KNOWLEDGE_BASE['return'], 'products': []}

    # --------------------------------------------------------------------------
    # INTENT 7: PAYMENT
    # --------------------------------------------------------------------------
    if intent == 'payment':
        return {'text': FAQ_KNOWLEDGE_BASE['payment'], 'products': []}

    # --------------------------------------------------------------------------
    # INTENT 8: PRODUCT DETAIL / SIZE CHART / AUTHENTICITY
    # --------------------------------------------------------------------------
    if intent == 'product_detail':
        msg_l = clean_msg.lower()
        if 'size chart' in msg_l or 'chart' in msg_l or 'size' in msg_l:
            return {'text': FAQ_KNOWLEDGE_BASE['size_chart'], 'products': []}
        if 'original' in msg_l or 'authentic' in msg_l or 'fake' in msg_l or 'asli' in msg_l:
            return {'text': FAQ_KNOWLEDGE_BASE['original'], 'products': []}
        return {
            'text': (
                "👟 **Product Quality & Materials:**\n"
                "Hamare sabhi sneakers breathable upper leather, high-abrasion non-slip rubber soles, aur high-energy cushioning ke saath aate hain.\n"
                "Aap kisi specific shoe ke detail page par jakar 'Technical Specs' aur 'Shoe Features' tab me poori details padh sakte hain!"
            ),
            'products': []
        }

    # --------------------------------------------------------------------------
    # INTENT 9: ACCOUNT & SUPPORT
    # --------------------------------------------------------------------------
    if intent == 'support':
        msg_l = clean_msg.lower()
        if 'password' in msg_l or 'login' in msg_l or 'account' in msg_l:
            return {'text': FAQ_KNOWLEDGE_BASE['account'], 'products': []}
        return {'text': FAQ_KNOWLEDGE_BASE['support'], 'products': []}

    # --------------------------------------------------------------------------
    # INTENT 10: GREETING
    # --------------------------------------------------------------------------
    if intent == 'greeting':
        user_name = f", {user.first_name}" if user and user.is_authenticated and user.first_name else ""
        return {
            'text': (
                f"Hello{user_name}! 👋 Main **Sneaker Squad AI Assistant** hoon.\n\n"
                "Aapko exact words bolne ki zaroorat nahi hai—aap aam bhasha me pooch sakte hain ya neeche diye gaye kisi bhi option par click kar sakte hain! 👇"
            ),
            'products': [],
            'quick_replies': DEFAULT_QUICK_REPLIES
        }

    # --------------------------------------------------------------------------
    # INTENT 11: FALLBACK
    # --------------------------------------------------------------------------
    return {
        'text': (
            "🤔 Mujhe aapki exact query samajh nahi aayi, par koi baat nahi!\n\n"
            "Kya aap inme se kuch dhoondh rahe hain? Direct tap karein: 👇"
        ),
        'products': [],
        'quick_replies': DEFAULT_QUICK_REPLIES
    }

