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
import pandas as pd
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
        'category', 'stock', 'sales', 'rating', 'main_image', 'description'
    ]
    try:
        products = Product.objects.filter(is_active=True, is_in_stock=True)
        data = []
        for p in products:
            # Extract color hints from name, tag, or description
            full_text = f"{p.name} {p.tag} {p.description or ''}".lower()
            detected_colors = []
            for c in ['black', 'white', 'red', 'blue', 'green', 'pink', 'silver', 'cream', 'orange', 'purple', 'grey', 'yellow']:
                if c in full_text:
                    detected_colors.append(c)
            color_str = ", ".join(detected_colors) if detected_colors else (p.tag or '')

            data.append({
                'id': p.code or str(p.id),
                'name': p.name,
                'brand': p.brand or 'Sneaker Squad',
                'price': float(p.price),
                'color': color_str,
                'size': p.sizes_list or 'UK 6, UK 7, UK 8, UK 9, UK 10, UK 11',
                'category': p.category.name if p.category else p.gender,
                'stock': p.stock_quantity,
                'sales': p.reviews_count or 0,  # Proxy for popularity/sales
                'rating': float(p.rating or 4.5),
                'main_image': p.main_image or '/static/img/shoe-1.jpg',
                'description': p.description or ''
            })

        if not data:
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(data)

        # Pre-compute lowercase helper columns for fast regex & string matching
        df['name_lower'] = df['name'].str.lower()
        df['brand_lower'] = df['brand'].str.lower()
        df['category_lower'] = df['category'].astype(str).str.lower()
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
    PRIORITY ORDER (Recommendation check MUST come before generic search):
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

    # Color extraction (Exact Regex First)
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
    if re.search(r'\b(cheapest|sasta|saste|sabse\s*sasta|low\s*price|lowest\s*price|kam\s*daam|kam\s*rate|kam\s*paisa|kam\s*budget|saste\s*me)\b', msg):
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
# 6. MASTER REPLY GENERATOR (get_reply)
# ==============================================================================

DEFAULT_QUICK_REPLIES = [
    {"label": "🔥 Trending Kicks", "query": "Trending sneakers dikhao"},
    {"label": "👟 Nike under 5000", "query": "Nike shoes under 5000"},
    {"label": "💰 Saste Shoes", "query": "Sabse saste shoes dikhao"},
    {"label": "📦 Mera Order", "query": "Mera order kahan hai?"},
    {"label": "🎉 Discount Coupons", "query": "Koi coupon code hai?"},
    {"label": "📏 Size Chart Guide", "query": "Size chart dikhao"}
]


def get_reply(message, user=None):
    """
    Main entry point for Chatbot:
    Takes message string & Django request.user
    Returns dictionary: {"text": str, "products": list}
    """
    clean_msg = message.strip()
    if not clean_msg:
        return {
            'text': "Kripya apna sawaal poochein, jaise: *'Nike shoes under 3000'* ya *'Mera order kahan hai?'*",
            'products': []
        }

    intent = detect_intent(clean_msg)
    df = get_df()

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

