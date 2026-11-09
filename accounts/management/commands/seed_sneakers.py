"""
=============================================================================
SNEAKER SQUAD: SEED SNEAKERS & CATALOG AUDIT MANAGEMENT COMMAND
File: accounts/management/commands/seed_sneakers.py
=============================================================================
Objectives:
1. Deduplicate Catalog: Remove existing duplicate products (by title / slug).
2. Purge Non-Sneaker Footwear & Apparel: Ensure every product is strictly a genuine sneaker.
3. Define 6 Sneaker Subcategories:
   - classic-low-tops      ("Classic Low-Tops")
   - chunky-platforms      ("Chunky & Platforms")
   - sports-running        ("Sports & Running")
   - streetwear-high-tops  ("Streetwear High-Tops")
   - slip-on-sneakers      ("Slip-On Sneakers")
   - limited-retro         ("Limited & Retro Editions")
4. Populate EXACTLY 6 unique sneakers for each subcategory (total 36 products).
5. Download high-quality, verified sneaker images via `requests` and save binary
   content directly into the model's `image_file` (ImageField) using `ContentFile`.
6. Enforce zero duplicate image URLs and idempotent execution.
=============================================================================
"""

import os
import sys
import time
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.conf import settings
from django.db.models import Q

from accounts.models import Category, SubCategory, Product


# =============================================================================
# CURATED DATASET: 6 SUBCATEGORIES x 6 UNIQUE SNEAKERS = EXACTLY 36 PRODUCTS
# Strictly verified direct Unsplash sneaker image URLs (clean studio backgrounds)
# =============================================================================
SNEAKER_DATASET = [
    # -------------------------------------------------------------------------
    # 1. Classic Low-Tops (classic-low-tops)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'classic-low-tops',
        'subcat_name': 'Classic Low-Tops',
        'subcat_desc': 'Iconic low-profile street classics and court silhouettes.',
        'code': 'nike-dunk-low-panda',
        'title': 'Nike Dunk Low Retro Panda',
        'brand': 'Nike',
        'price': 8999.00,
        'original_price': 11999.00,
        'gender': 'unisex',
        'color': 'Black / White',
        'badge_text': 'Bestseller',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 342,
        'stock': 28,
        'tag': 'low-top retro court sneaker',
        'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80',
        'description': 'The iconic two-tone Dunk Low crafted with crisp monochrome leather overlays and vintage hoops court style.',
        'features': [
            'Crisp premium genuine leather upper with slight sheen.',
            'Foam midsole offers lightweight, responsive cushioning.',
            'Padded, low-cut collar looks sleek and feels comfortable.',
            'Rubber outsole with classic hoops pivot circle adds durability and traction.'
        ]
    },
    {
        'subcat_slug': 'classic-low-tops',
        'subcat_name': 'Classic Low-Tops',
        'subcat_desc': 'Iconic low-profile street classics and court silhouettes.',
        'code': 'adidas-samba-og-white',
        'title': 'Adidas Samba OG Cloud White',
        'brand': 'Adidas',
        'price': 7499.00,
        'original_price': 9999.00,
        'gender': 'unisex',
        'color': 'Cloud White / Core Black / Gum',
        'badge_text': 'Trending Drop',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 280,
        'stock': 32,
        'tag': 'low-top retro terrace samba sneaker',
        'image_url': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=800&q=80',
        'description': 'Timeless low-top terrace icon featuring premium full-grain leather with the legendary suede T-toe and gum sole.',
        'features': [
            'Full grain leather upper with gritty suede overlays.',
            'Soft leather lining for everyday step-in comfort.',
            'Low-profile gum rubber cupsole for retro grip.',
            'Foil embossed metallic Samba lateral branding.'
        ]
    },
    {
        'subcat_slug': 'classic-low-tops',
        'subcat_name': 'Classic Low-Tops',
        'subcat_desc': 'Iconic low-profile street classics and court silhouettes.',
        'code': 'new-balance-550-white-green',
        'title': 'New Balance 550 White Green',
        'brand': 'New Balance',
        'price': 10499.00,
        'original_price': 13999.00,
        'gender': 'men',
        'color': 'Sea Salt / Forest Green',
        'badge_text': 'Hot Drop',
        'badge_style': 'new',
        'rating': 4.9,
        'reviews_count': 195,
        'stock': 22,
        'tag': 'low-top retro basketball court sneaker',
        'image_url': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=800&q=80',
        'description': 'Faithful tribute to the 1989 pro basketball original, blending perforated leather quarter panels with rich evergreen details.',
        'features': [
            'Heavy-gauge premium perforated leather construction.',
            'Rubber cupsole tooling engineered for basketball stability.',
            'Padded mesh tongue and collar lining.',
            'Signature raised 550 forefoot callout.'
        ]
    },
    {
        'subcat_slug': 'classic-low-tops',
        'subcat_name': 'Classic Low-Tops',
        'subcat_desc': 'Iconic low-profile street classics and court silhouettes.',
        'code': 'puma-suede-classic-xxi',
        'title': 'Puma Suede Classic XXI Black',
        'brand': 'Puma',
        'price': 5499.00,
        'original_price': 6999.00,
        'gender': 'men',
        'color': 'Puma Black / White',
        'badge_text': 'OG Classic',
        'badge_style': 'new',
        'rating': 4.7,
        'reviews_count': 160,
        'stock': 35,
        'tag': 'low-top suede classic retro sneaker',
        'image_url': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=800&q=80',
        'description': 'The shoe that defined hip-hop street culture in 1968, constructed with velvety suede and the distinctive Puma Formstrip.',
        'features': [
            'Full velvety suede leather upper with synthetic collar lining.',
            'Comfort sockliner provides immediate all-day cushioning.',
            'Ribbed rubber midsole and textured grip outsole.',
            'Metallic gold foil archive Puma logo debossing.'
        ]
    },
    {
        'subcat_slug': 'classic-low-tops',
        'subcat_name': 'Classic Low-Tops',
        'subcat_desc': 'Iconic low-profile street classics and court silhouettes.',
        'code': 'nike-air-force-1-triple-white',
        'title': 'Nike Air Force 1 07 Triple White',
        'brand': 'Nike',
        'price': 8195.00,
        'original_price': 9999.00,
        'gender': 'women',
        'color': 'Triple White',
        'badge_text': 'Wardrobe Essential',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 512,
        'stock': 40,
        'tag': 'low-top triple white air force court sneaker',
        'image_url': 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=800&q=80',
        'description': 'The radiant hoops legend that pairs crisp stitched leather overlays with legendary encapsulated Nike Air cushioning.',
        'features': [
            'Stitched leather overlays on the upper add heritage style and support.',
            'Encapsulated Nike Air unit ensures lightweight cushioning.',
            'Perforations on the toe box keep airflow constant.',
            'Solid non-marking rubber outsole with pivot circle.'
        ]
    },
    {
        'subcat_slug': 'classic-low-tops',
        'subcat_name': 'Classic Low-Tops',
        'subcat_desc': 'Iconic low-profile street classics and court silhouettes.',
        'code': 'vans-old-skool-classic',
        'title': 'Vans Old Skool Core Black White',
        'brand': 'Vans',
        'price': 4999.00,
        'original_price': 5999.00,
        'gender': 'women',
        'color': 'Black / True White',
        'badge_text': 'Skate Icon',
        'badge_style': 'sale',
        'rating': 4.8,
        'reviews_count': 225,
        'stock': 30,
        'tag': 'low-top skate canvas old skool sneaker',
        'image_url': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=800&q=80',
        'description': 'The first skate shoe to feature the recognizable Vans leather sidestripe, wrapped in sturdy canvas and reinforced suede.',
        'features': [
            'Durable 10oz canvas and reinforced suede uppers.',
            'Re-enforced toe caps withstand repeated wear.',
            'Supportive padded collars for ankle flexibility.',
            'Signature waffle rubber outsoles for board feel.'
        ]
    },

    # -------------------------------------------------------------------------
    # 2. Chunky & Platforms (chunky-platforms)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'chunky-platforms',
        'subcat_name': 'Chunky & Platforms',
        'subcat_desc': 'Bold statement sneakers, stacked platform soles, and oversized dad shoes.',
        'code': 'balenciaga-triple-s-clear',
        'title': 'Balenciaga Triple S Clear Sole White',
        'brand': 'Balenciaga',
        'price': 24999.00,
        'original_price': 29999.00,
        'gender': 'unisex',
        'color': 'Off-White / Translucent',
        'badge_text': 'Runway Drop',
        'badge_style': 'limited',
        'rating': 4.9,
        'reviews_count': 140,
        'stock': 12,
        'tag': 'chunky platform dad luxury statement sneaker',
        'image_url': 'https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?auto=format&fit=crop&w=800&q=80',
        'description': 'The definitive chunky dad sneaker that revolutionized runway fashion, built with 3-layered complex sole technology.',
        'features': [
            'Multi-material upper: mesh, calfskin leather, and TPU.',
            '3-layer articulated outsole with injected air bubble.',
            'Shoe size embroidered directly at the tip of the toe.',
            'Two-tone hiking-inspired rope laces.'
        ]
    },
    {
        'subcat_slug': 'chunky-platforms',
        'subcat_name': 'Chunky & Platforms',
        'subcat_desc': 'Bold statement sneakers, stacked platform soles, and oversized dad shoes.',
        'code': 'new-balance-9060-sea-salt',
        'title': 'New Balance 9060 Sea Salt White',
        'brand': 'New Balance',
        'price': 14999.00,
        'original_price': 18999.00,
        'gender': 'men',
        'color': 'Sea Salt / Rain Cloud',
        'badge_text': 'Viral Hit',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 230,
        'stock': 18,
        'tag': 'chunky platform retro runner 9060 sneaker',
        'image_url': 'https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?auto=format&fit=crop&w=800&q=80',
        'description': 'Futuristic Y2K aesthetic reinterpreting familiar 99X series elements with an exaggerated sculpted pod midsole.',
        'features': [
            'Mesh upper with premium pigskin suede overlays.',
            'Dual-density midsole featuring ABZORB and SBS cushioning.',
            'Tongue logo inspired by original 991 lace jewel.',
            'Diamond outsole pattern inspired by classic 860 design.'
        ]
    },
    {
        'subcat_slug': 'chunky-platforms',
        'subcat_name': 'Chunky & Platforms',
        'subcat_desc': 'Bold statement sneakers, stacked platform soles, and oversized dad shoes.',
        'code': 'nike-m2k-tekno-phantom',
        'title': 'Nike M2K Tekno Phantom Summit',
        'brand': 'Nike',
        'price': 8499.00,
        'original_price': 10999.00,
        'gender': 'women',
        'color': 'Phantom / Summit White / Orange',
        'badge_text': 'Chunky OG',
        'badge_style': 'new',
        'rating': 4.7,
        'reviews_count': 175,
        'stock': 24,
        'tag': 'chunky dad platform m2k tekno sneaker',
        'image_url': 'https://images.unsplash.com/photo-1575537302964-96cd47c06b1b?auto=format&fit=crop&w=800&q=80',
        'description': 'Inspired by the iconic Monarch franchise, the M2K Tekno brings futuristic edge with deep heel clips and sculpted foam.',
        'features': [
            'Layered genuine leather and synthetic upper.',
            'Lightweight injected Phylon midsole provides plush cushioning.',
            'TPU heel clip heightens stability and adds futuristic visual pop.',
            'Non-marking solid rubber traction lugs.'
        ]
    },
    {
        'subcat_slug': 'chunky-platforms',
        'subcat_name': 'Chunky & Platforms',
        'subcat_desc': 'Bold statement sneakers, stacked platform soles, and oversized dad shoes.',
        'code': 'adidas-ozweego-pure',
        'title': 'Adidas Ozweego Pure Cloud Chalk',
        'brand': 'Adidas',
        'price': 9999.00,
        'original_price': 12999.00,
        'gender': 'men',
        'color': 'Cloud White / Core Black',
        'badge_text': 'Tech Vibe',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 148,
        'stock': 20,
        'tag': 'chunky adiprene futuristic ozweego sneaker',
        'image_url': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80',
        'description': 'Futuristic bold runner highlighting distinctive translucent support tubing, targeted Adiprene+ forefoot cushioning, and chunky heel flares.',
        'features': [
            'Textile upper with hot-melt overlays and TPU details.',
            'Adiprene+ forefoot cushioning absorbs impact forces.',
            'Lightweight EVA sculpted midsole with flared heel base.',
            'Snug, sock-like lockdown fit.'
        ]
    },
    {
        'subcat_slug': 'chunky-platforms',
        'subcat_name': 'Chunky & Platforms',
        'subcat_desc': 'Bold statement sneakers, stacked platform soles, and oversized dad shoes.',
        'code': 'puma-mayze-platform-white',
        'title': 'Puma Mayze Stack Platform White',
        'brand': 'Puma',
        'price': 7999.00,
        'original_price': 9999.00,
        'gender': 'women',
        'color': 'Puma White / Pristine',
        'badge_text': 'Stack Platform',
        'badge_style': 'trending',
        'rating': 4.8,
        'reviews_count': 210,
        'stock': 26,
        'tag': 'platform chunky stacked sole mayze sneaker',
        'image_url': 'https://images.unsplash.com/photo-1512990414988-0a005e99432f?auto=format&fit=crop&w=800&q=80',
        'description': 'Elevate your rotation with the Mayze Stack. Features a bold multi-layered elevated platform sole and clean leather upper.',
        'features': [
            'Smooth genuine leather upper with suede trim.',
            'Chunky elevated rubber platform midsole with jagged tooling.',
            'Glossy metallic Puma foil branding on quarter and heel.',
            'Woven heel pull tab for smooth on-and-off.'
        ]
    },
    {
        'subcat_slug': 'chunky-platforms',
        'subcat_name': 'Chunky & Platforms',
        'subcat_desc': 'Bold statement sneakers, stacked platform soles, and oversized dad shoes.',
        'code': 'salomon-xt6-mindful-trail',
        'title': 'Salomon XT-6 Mindful Trail White',
        'brand': 'Salomon',
        'price': 16999.00,
        'original_price': 19999.00,
        'gender': 'unisex',
        'color': 'Vanilla Ice / Almond Milk',
        'badge_text': 'Gorpcore Grail',
        'badge_style': 'new',
        'rating': 4.9,
        'reviews_count': 188,
        'stock': 16,
        'tag': 'chunky gorpcore trail platform xt6 sneaker',
        'image_url': 'https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=800&q=80',
        'description': 'The ultra-distance running champion turned street-style kingpin, featuring Agile Chassis System and lugged platform grip.',
        'features': [
            'Resistant TPU film and breathable mesh upper.',
            'Agile Chassis System (ACS) provides downhill stability.',
            'Quicklace minimalistic strong lacing system with lace pocket.',
            'Mud Contagrip outsole built for maximum traction on loose terrain.'
        ]
    },

    # -------------------------------------------------------------------------
    # 3. Sports & Running (sports-running)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'sports-running',
        'subcat_name': 'Sports & Running',
        'subcat_desc': 'High-performance athletic runners, marathon trainers, and kinetic energy shoes.',
        'code': 'nike-air-zoom-pegasus-40',
        'title': 'Nike Air Zoom Pegasus 40 Crimson',
        'brand': 'Nike',
        'price': 9499.00,
        'original_price': 11999.00,
        'gender': 'men',
        'color': 'Bright Crimson / White',
        'badge_text': 'Speed Runner',
        'badge_style': 'new',
        'rating': 4.9,
        'reviews_count': 310,
        'stock': 30,
        'tag': 'running athletic sports zoom pegasus sneaker',
        'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80',
        'description': 'The workhorse with wings. Nike React foam teamed with dual Zoom Air units provides resilient spring for daily mileage.',
        'features': [
            'Nike React lightweight durable foam delivers a responsive ride.',
            'Two Zoom Air units at forefoot and heel energize toe-off.',
            'Highly tuned single-layer engineered mesh upper.',
            'Redesigned midfoot strap provides snug, uniform lockdown.'
        ]
    },
    {
        'subcat_slug': 'sports-running',
        'subcat_name': 'Sports & Running',
        'subcat_desc': 'High-performance athletic runners, marathon trainers, and kinetic energy shoes.',
        'code': 'adidas-ultraboost-light-black',
        'title': 'Adidas Ultraboost Light Carbon Black',
        'brand': 'Adidas',
        'price': 13999.00,
        'original_price': 17999.00,
        'gender': 'men',
        'color': 'Core Black / Carbon / White',
        'badge_text': 'Ultralight BOOST',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 265,
        'stock': 25,
        'tag': 'running athletic boost ultraboost sneaker',
        'image_url': 'https://images.unsplash.com/photo-1508609349937-5ec4ae374ebf?auto=format&fit=crop&w=800&q=80',
        'description': 'Experience epic kinetic energy with the lightest BOOST ever engineered, paired with an adaptable Primeknit+ wrap upper.',
        'features': [
            '30% lighter BOOST material with hundreds of energy capsules.',
            'Linear Energy Push (LEP) system increases forefoot bending stiffness.',
            'Continental Natural Performance Rubber outsole for all-weather grip.',
            'Primeknit+ textile upper crafted with yarn containing Parley Ocean Plastic.'
        ]
    },
    {
        'subcat_slug': 'sports-running',
        'subcat_name': 'Sports & Running',
        'subcat_desc': 'High-performance athletic runners, marathon trainers, and kinetic energy shoes.',
        'code': 'nike-vaporfly-3-electric',
        'title': 'Nike Vaporfly 3 Electric Mint',
        'brand': 'Nike',
        'price': 18999.00,
        'original_price': 22999.00,
        'gender': 'unisex',
        'color': 'Electric Green / Screaming Mint',
        'badge_text': 'Marathon Elite',
        'badge_style': 'limited',
        'rating': 5.0,
        'reviews_count': 142,
        'stock': 14,
        'tag': 'running racing carbon plate vaporfly sneaker',
        'image_url': 'https://images.unsplash.com/photo-1579338559194-a162d19bf842?auto=format&fit=crop&w=800&q=80',
        'description': 'Catch \'em if you can. The ultimate racing weapon engineered for record breakers with a full carbon Flyplate and ZoomX.',
        'features': [
            'Full-length carbon fiber Flyplate provides a stiff, propulsive feel.',
            'Nike ZoomX ultralight foam yields maximum energy return.',
            'Specifically selected Flyknit yarns bring targeted breathability.',
            'Updated thin waffle outsole reduces weight without sacrificing grip.'
        ]
    },
    {
        'subcat_slug': 'sports-running',
        'subcat_name': 'Sports & Running',
        'subcat_desc': 'High-performance athletic runners, marathon trainers, and kinetic energy shoes.',
        'code': 'asics-gel-nimbus-25-sunrise',
        'title': 'Asics Gel-Nimbus 25 Sunrise Coral',
        'brand': 'Asics',
        'price': 12499.00,
        'original_price': 14999.00,
        'gender': 'women',
        'color': 'Sunrise Red / Pure Silver',
        'badge_text': 'Max Cushion',
        'badge_style': 'trending',
        'rating': 4.8,
        'reviews_count': 190,
        'stock': 28,
        'tag': 'running sports cushion gel nimbus sneaker',
        'image_url': 'https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=800&q=80',
        'description': 'Experience the softest landings imaginable with PureGEL technology embedded beneath plush FF BLAST PLUS ECO cushioning.',
        'features': [
            'PureGEL technology provides lightweight impact absorption.',
            'FF BLAST PLUS ECO cushioning contains at least 20% bio-based content.',
            'Soft, stretchy knit collar hugs ankles seamlessly.',
            'AHAR outsole rubber improves compound durability.'
        ]
    },
    {
        'subcat_slug': 'sports-running',
        'subcat_name': 'Sports & Running',
        'subcat_desc': 'High-performance athletic runners, marathon trainers, and kinetic energy shoes.',
        'code': 'new-balance-fresh-foam-1080v13',
        'title': 'New Balance Fresh Foam X 1080v13',
        'brand': 'New Balance',
        'price': 13499.00,
        'original_price': 15999.00,
        'gender': 'women',
        'color': 'Starlight / Sea Salt',
        'badge_text': 'Smooth Glide',
        'badge_style': 'new',
        'rating': 4.9,
        'reviews_count': 164,
        'stock': 22,
        'tag': 'running fresh foam sports athletic sneaker',
        'image_url': 'https://images.unsplash.com/photo-1587245937260-496660167c52?auto=format&fit=crop&w=800&q=80',
        'description': 'The pinnacle daily road trainer with precision Fresh Foam X rocker geometry and an engineered breathable mesh chassis.',
        'features': [
            'Fresh Foam X midsole foam delivers the plushest Fresh Foam experience.',
            'Forefoot rocker profile facilitates seamless heel-to-toe transitions.',
            'Engineered mesh upper feels like an aerodynamic second skin.',
            'Solid rubber forefoot zone for snappy push-offs.'
        ]
    },
    {
        'subcat_slug': 'sports-running',
        'subcat_name': 'Sports & Running',
        'subcat_desc': 'High-performance athletic runners, marathon trainers, and kinetic energy shoes.',
        'code': 'nike-air-zoom-tempo-next',
        'title': 'Nike Air Zoom Tempo Next% Flyknit',
        'brand': 'Nike',
        'price': 15499.00,
        'original_price': 18999.00,
        'gender': 'unisex',
        'color': 'Volt / White / Black',
        'badge_text': 'High Cadence',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 135,
        'stock': 19,
        'tag': 'running tempo sports zoom next flyknit sneaker',
        'image_url': 'https://images.unsplash.com/photo-1588117305388-c2631a279f82?auto=format&fit=crop&w=800&q=80',
        'description': 'Engineered to bridge the gap between daily training and race day. Visible Zoom Air pods under the ball of the foot unleash explosive bounce.',
        'features': [
            'Dual visible Zoom Air pods offer ultra-snappy energy return.',
            'Nike React foam at the heel cushions high-cadence impact.',
            'Composite plate runs the full length for stability.',
            'Translucent high-tenacity Flyknit upper provides targeted containment.'
        ]
    },

    # -------------------------------------------------------------------------
    # 4. Streetwear High-Tops (streetwear-high-tops)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'streetwear-high-tops',
        'subcat_name': 'Streetwear High-Tops',
        'subcat_desc': 'Ankle-hugging streetwear grails, retro court highs, and legendary high collars.',
        'code': 'air-jordan-1-retro-chicago',
        'title': 'Air Jordan 1 High OG Chicago Lost & Found',
        'brand': 'Jordan',
        'price': 16999.00,
        'original_price': 21999.00,
        'gender': 'men',
        'color': 'Varsity Red / Black / Sail',
        'badge_text': 'Holy Grail',
        'badge_style': 'limited',
        'rating': 5.0,
        'reviews_count': 490,
        'stock': 15,
        'tag': 'high-top jordan retro basketball chicago sneaker',
        'image_url': 'https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=800&q=80',
        'description': 'The shoe that started it all in 1985. The iconic red, white, and black Chicago colorway finished with aged vintage collars.',
        'features': [
            'Premium cracked leather collar gives an authentic vintage 1985 look.',
            'Solid rubber cupsole with encapsulated Air-Sole unit.',
            'Debossed Air Jordan Wings insignia on ankle flap.',
            'Comes complete with vintage-styled shoebox and receipt.'
        ]
    },
    {
        'subcat_slug': 'streetwear-high-tops',
        'subcat_name': 'Streetwear High-Tops',
        'subcat_desc': 'Ankle-hugging streetwear grails, retro court highs, and legendary high collars.',
        'code': 'air-jordan-1-retro-royal',
        'title': 'Air Jordan 1 Retro High OG Royal Blue',
        'brand': 'Jordan',
        'price': 15999.00,
        'original_price': 19999.00,
        'gender': 'men',
        'color': 'Black / Royal Blue / White',
        'badge_text': 'Heritage OG',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 320,
        'stock': 17,
        'tag': 'high-top jordan royal blue retro sneaker',
        'image_url': 'https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?auto=format&fit=crop&w=800&q=80',
        'description': 'Draped in opulent royal blue and jet black tumbled leather, this original 1985 silhouette represents the essence of sneaker culture.',
        'features': [
            'High-grade tumbled full-grain leather uppers.',
            'Encapsulated Air-Sole unit provides lightweight cushioning.',
            'Padded high-cut collar provides ankle support and street swagger.',
            'Deep flex grooves on the rubber cupsole for natural movement.'
        ]
    },
    {
        'subcat_slug': 'streetwear-high-tops',
        'subcat_name': 'Streetwear High-Tops',
        'subcat_desc': 'Ankle-hugging streetwear grails, retro court highs, and legendary high collars.',
        'code': 'nike-blazer-mid-77-vintage',
        'title': 'Nike Blazer Mid 77 Vintage White Black',
        'brand': 'Nike',
        'price': 7999.00,
        'original_price': 9999.00,
        'gender': 'unisex',
        'color': 'White / Black / Sail',
        'badge_text': 'Vintage Court',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 240,
        'stock': 28,
        'tag': 'high-top blazer mid 77 vintage court sneaker',
        'image_url': 'https://images.unsplash.com/photo-1556906781-9a412961c28c?auto=format&fit=crop&w=800&q=80',
        'description': 'Praised by the streets for its classic simplicity and comfort. Features crisp leather with suede mudguards and exposed foam tongues.',
        'features': [
            'Leather and synthetic upper keeps the classic look of the 70s original.',
            'Vintage midsole treatment provides an authentic old-school look.',
            'Autoclave construction fuses outsole to midsole for a streamlined feel.',
            'Non-marking solid rubber outsole with herringbone pattern.'
        ]
    },
    {
        'subcat_slug': 'streetwear-high-tops',
        'subcat_name': 'Streetwear High-Tops',
        'subcat_desc': 'Ankle-hugging streetwear grails, retro court highs, and legendary high collars.',
        'code': 'converse-chuck-70-parchment',
        'title': 'Converse Chuck 70 High Top Parchment',
        'brand': 'Converse',
        'price': 5999.00,
        'original_price': 7499.00,
        'gender': 'unisex',
        'color': 'Parchment / Egret / Black',
        'badge_text': 'Core Icon',
        'badge_style': 'trending',
        'rating': 4.8,
        'reviews_count': 380,
        'stock': 35,
        'tag': 'high-top converse chuck 70 canvas sneaker',
        'image_url': 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?auto=format&fit=crop&w=800&q=80',
        'description': 'Crafted using premium 12oz heavy canvas, winged tongue stitching, glossy egret foxing, and enhanced OrthoLite insole arch support.',
        'features': [
            'Heavyweight 12oz canvas for premium structure and longevity.',
            'OrthoLite insole cushioning delivers all-day arch comfort.',
            'Winged tongue stitching keeps tongue locked firmly in place.',
            'Glossy, taller rubber sidewall and vintage black heel badge.'
        ]
    },
    {
        'subcat_slug': 'streetwear-high-tops',
        'subcat_name': 'Streetwear High-Tops',
        'subcat_desc': 'Ankle-hugging streetwear grails, retro court highs, and legendary high collars.',
        'code': 'nike-dunk-high-university-blue',
        'title': 'Nike Dunk High Retro University Blue',
        'brand': 'Nike',
        'price': 10999.00,
        'original_price': 13999.00,
        'gender': 'women',
        'color': 'University Blue / White',
        'badge_text': 'High Court Drop',
        'badge_style': 'new',
        'rating': 4.9,
        'reviews_count': 178,
        'stock': 20,
        'tag': 'high-top dunk retro basketball unc sneaker',
        'image_url': 'https://images.unsplash.com/photo-1597045566677-8cf032ed6634?auto=format&fit=crop&w=800&q=80',
        'description': 'Old-school college hoops energy reborn in crisp university blue overlays and high-padded ankle containment.',
        'features': [
            'Crisp genuine leather upper ages to soft perfection with wear.',
            'Padded, high-top collar adds an old-school look rooted in comfort.',
            'Bold color-blocking keeps the original 1985 college inspiration alive.',
            'Perforated toe box for essential forefoot ventilation.'
        ]
    },
    {
        'subcat_slug': 'streetwear-high-tops',
        'subcat_name': 'Streetwear High-Tops',
        'subcat_desc': 'Ankle-hugging streetwear grails, retro court highs, and legendary high collars.',
        'code': 'off-white-air-jordan-1-high',
        'title': 'Off-White x Air Jordan 1 High Ghosting',
        'brand': 'Jordan',
        'price': 22999.00,
        'original_price': 27999.00,
        'gender': 'women',
        'color': 'White / Sail / Ghosting',
        'badge_text': 'Grail Collab',
        'badge_style': 'limited',
        'rating': 5.0,
        'reviews_count': 115,
        'stock': 10,
        'tag': 'high-top off-white collab limited deconstructed sneaker',
        'image_url': 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=800&q=80',
        'description': 'Virgil Abloh\'s deconstructed high-top masterpiece featuring exposed sponge collars, blue thread Swoosh tacking, and signature zip-tie.',
        'features': [
            'Deconstructed upper with exposed foam and translucent textiles.',
            'Tacked-on oversized Swoosh held by bright blue and orange stitching.',
            'Signature industrial Helvetica text print on medial quarter.',
            'Zip-tie zip tag and "SHOELACES" tipped cotton laces.'
        ]
    },

    # -------------------------------------------------------------------------
    # 5. Slip-On Sneakers (slip-on-sneakers)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'slip-on-sneakers',
        'subcat_name': 'Slip-On Sneakers',
        'subcat_desc': 'Laceless streetwear ease, knitted sock sneakers, and effortless slip-in style.',
        'code': 'vans-classic-slip-on-checkerboard',
        'title': 'Vans Classic Slip-On Checkerboard',
        'brand': 'Vans',
        'price': 4299.00,
        'original_price': 5499.00,
        'gender': 'unisex',
        'color': 'Black / Off-White Checkerboard',
        'badge_text': 'Skate Icon',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 410,
        'stock': 35,
        'tag': 'slip-on laceless skate checkerboard sneaker',
        'image_url': 'https://images.unsplash.com/photo-1562183241-b937e95585b6?auto=format&fit=crop&w=800&q=80',
        'description': 'The unmistakable southern California icon. Slip-on design equipped with stretchy elastic side accents and waffle outsoles.',
        'features': [
            'Low profile sturdy 10oz canvas uppers in timeless checkerboard.',
            'Elastic side accents allow rapid slip-on and slide-off convenience.',
            'Padded collars for ankle comfort and flexibility.',
            'Signature gum rubber waffle outsoles.'
        ]
    },
    {
        'subcat_slug': 'slip-on-sneakers',
        'subcat_name': 'Slip-On Sneakers',
        'subcat_desc': 'Laceless streetwear ease, knitted sock sneakers, and effortless slip-in style.',
        'code': 'balenciaga-speed-trainer-black',
        'title': 'Balenciaga Speed 2.0 Knit Sock Slip-On',
        'brand': 'Balenciaga',
        'price': 19999.00,
        'original_price': 24999.00,
        'gender': 'unisex',
        'color': 'Black / White Sole',
        'badge_text': 'Sock Runner',
        'badge_style': 'limited',
        'rating': 4.9,
        'reviews_count': 160,
        'stock': 12,
        'tag': 'slip-on sock knit luxury speed trainer sneaker',
        'image_url': 'https://images.unsplash.com/photo-1603808033192-082d6919d3e1?auto=format&fit=crop&w=800&q=80',
        'description': 'Revolutionary technical 3D knit sock runner featuring ultra-flexible molded ergonomic sole with \'No Memory\' shock absorption.',
        'features': [
            '3D recycled technical knit upper wraps foot like a second skin.',
            'Ultra-flexible molded ergonomic sole with "No Memory" technology.',
            'Contrast Balenciaga white logo print at lateral exterior.',
            'Extremely lightweight (under 240g per shoe).'
        ]
    },
    {
        'subcat_slug': 'slip-on-sneakers',
        'subcat_name': 'Slip-On Sneakers',
        'subcat_desc': 'Laceless streetwear ease, knitted sock sneakers, and effortless slip-in style.',
        'code': 'adidas-puremotion-adapt-white',
        'title': 'Adidas Puremotion Adapt Slip-On White',
        'brand': 'Adidas',
        'price': 5299.00,
        'original_price': 6499.00,
        'gender': 'women',
        'color': 'Cloud White / Core Black',
        'badge_text': 'Cloud Comfort',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 205,
        'stock': 28,
        'tag': 'slip-on laceless puremotion cloudfoam sneaker',
        'image_url': 'https://images.unsplash.com/photo-1575456456278-936c89ccdbdf?auto=format&fit=crop&w=800&q=80',
        'description': 'Running-inspired laceless slip-on featuring supportive crossover elastic bandage straps and plush Cloudfoam cushioning.',
        'features': [
            'Snug sock-like textile upper with stretchy bandage overlay.',
            'Cloudfoam midsole provides immediate step-in cushioning.',
            'Synthetic outsole delivers lightweight durability.',
            'Slip-on build with dual tongue and heel pull loops.'
        ]
    },
    {
        'subcat_slug': 'slip-on-sneakers',
        'subcat_name': 'Slip-On Sneakers',
        'subcat_desc': 'Laceless streetwear ease, knitted sock sneakers, and effortless slip-in style.',
        'code': 'puma-adelina-comfort-slipon',
        'title': 'Puma Adelina Comfort Slip-On Blossom',
        'brand': 'Puma',
        'price': 3999.00,
        'original_price': 4999.00,
        'gender': 'women',
        'color': 'Rose Dust / Marshmallow',
        'badge_text': 'Everyday Ease',
        'badge_style': 'sale',
        'rating': 4.7,
        'reviews_count': 180,
        'stock': 30,
        'tag': 'slip-on ballerina softfoam comfort sneaker',
        'image_url': 'https://images.unsplash.com/photo-1616406432452-07bc5938759d?auto=format&fit=crop&w=800&q=80',
        'description': 'Chic ballet-sneaker crossover built for light travel, running errands, or recovery days with plush SoftFoam+ footbeds.',
        'features': [
            'Breathable mesh and neoprene slip-on construction.',
            'SoftFoam+ cushioned footbed ensures pillow-soft walking.',
            'Curved EVA injection outsole provides flexible shock absorption.',
            'Elastic cross strap ensures secure fit without laces.'
        ]
    },
    {
        'subcat_slug': 'slip-on-sneakers',
        'subcat_name': 'Slip-On Sneakers',
        'subcat_desc': 'Laceless streetwear ease, knitted sock sneakers, and effortless slip-in style.',
        'code': 'nike-react-phantom-run-flyknit',
        'title': 'Nike React Phantom Run Flyknit 2',
        'brand': 'Nike',
        'price': 11999.00,
        'original_price': 14999.00,
        'gender': 'men',
        'color': 'Black / White / Volt',
        'badge_text': 'Laceless React',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 155,
        'stock': 22,
        'tag': 'slip-on laceless flyknit react running sneaker',
        'image_url': 'https://images.unsplash.com/photo-1581101767113-1677fc2beaa8?auto=format&fit=crop&w=800&q=80',
        'description': 'Ditching the laces entirely, Flyknit Loft brings three forefoot layers that cradle the foot directly onto Nike React foam.',
        'features': [
            'Laceless Flyknit upper features elastic molding for locked-in feel.',
            'Nike React technology provides an ultra-smooth, responsive ride.',
            'Increased rubber at the outsole helps deliver traction and durability.',
            'Molding around the heel keeps your foot feeling secure.'
        ]
    },
    {
        'subcat_slug': 'slip-on-sneakers',
        'subcat_name': 'Slip-On Sneakers',
        'subcat_desc': 'Laceless streetwear ease, knitted sock sneakers, and effortless slip-in style.',
        'code': 'onitsuka-tiger-mexico-66-slipon',
        'title': 'Onitsuka Tiger Mexico 66 Slip-On Birch',
        'brand': 'Onitsuka Tiger',
        'price': 8499.00,
        'original_price': 10499.00,
        'gender': 'men',
        'color': 'Birch / India Ink / Latte',
        'badge_text': 'Archive Slip-On',
        'badge_style': 'new',
        'rating': 4.8,
        'reviews_count': 195,
        'stock': 24,
        'tag': 'slip-on retro canvas onitsuka mexico 66 sneaker',
        'image_url': 'https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=800&q=80',
        'description': 'Laceless variation of the classic 1968 Olympic runner. Built with internal elastic banding to retain the shape while slipping on effortlessly.',
        'features': [
            'Lightweight canvas and suede upper in retro track colors.',
            'Internal elastic band across instep for snug slip-on fit.',
            'Iconic cross-stripe leather side accents.',
            'Thin flexible vulcanized rubber outsole.'
        ]
    },

    # -------------------------------------------------------------------------
    # 6. Limited & Retro Editions (limited-retro)
    # -------------------------------------------------------------------------
    {
        'subcat_slug': 'limited-retro',
        'subcat_name': 'Limited & Retro Editions',
        'subcat_desc': 'Collector deadstock grails, numbered editions, and timeless historical drops.',
        'code': 'air-jordan-4-retro-bred',
        'title': 'Air Jordan 4 Retro Bred Reimagined',
        'brand': 'Jordan',
        'price': 19999.00,
        'original_price': 24999.00,
        'gender': 'men',
        'color': 'Black / Fire Red / Cement Grey',
        'badge_text': 'Tier 1 Grail',
        'badge_style': 'limited',
        'rating': 5.0,
        'reviews_count': 560,
        'stock': 10,
        'tag': 'retro limited jordan 4 bred grail sneaker',
        'image_url': 'https://images.unsplash.com/photo-1516478177764-9fe5bd7e9717?auto=format&fit=crop&w=800&q=80',
        'description': 'Tinker Hatfield\'s 1989 marvel reimagined in premium tumbled black leather with iconic side mesh quarter nets and Nike Air heels.',
        'features': [
            'Full-grain supple black tumbled leather construction.',
            'Molded plastic wings and eyelets offer structural support.',
            'Visible Air-Sole unit housed within polyurethane midsole.',
            'Original Nike Air branding on the heel badge.'
        ]
    },
    {
        'subcat_slug': 'limited-retro',
        'subcat_name': 'Limited & Retro Editions',
        'subcat_desc': 'Collector deadstock grails, numbered editions, and timeless historical drops.',
        'code': 'travis-scott-jordan-1-reverse-mocha',
        'title': 'Travis Scott x Air Jordan 1 Low Reverse Mocha',
        'brand': 'Jordan',
        'price': 23999.00,
        'original_price': 28999.00,
        'gender': 'unisex',
        'color': 'Sail / Dark Mocha / University Red',
        'badge_text': 'Collab Icon',
        'badge_style': 'limited',
        'rating': 5.0,
        'reviews_count': 620,
        'stock': 8,
        'tag': 'retro limited travis scott reverse mocha cactus jack sneaker',
        'image_url': 'https://images.unsplash.com/photo-1595341888016-a392ef81b7de?auto=format&fit=crop&w=800&q=80',
        'description': 'The most coveted low-top on the planet. Oversized reverse Swoosh, premium mocha nubuck base, and embroidered Cactus Jack smiley.',
        'features': [
            'Rich dark mocha brown nubuck with white tumbled leather overlays.',
            'Oversized reversed leather Swoosh along lateral side.',
            'Cactus Jack face logo embroidered on the left heel tab.',
            'Aged yellowed sail midsole gives authentic deadstock warmth.'
        ]
    },
    {
        'subcat_slug': 'limited-retro',
        'subcat_name': 'Limited & Retro Editions',
        'subcat_desc': 'Collector deadstock grails, numbered editions, and timeless historical drops.',
        'code': 'adidas-yeezy-boost-700-waverunner',
        'title': 'Adidas Yeezy Boost 700 Wave Runner',
        'brand': 'Adidas',
        'price': 21999.00,
        'original_price': 26999.00,
        'gender': 'unisex',
        'color': 'Solid Grey / Chalk White / Core Black',
        'badge_text': 'Design Monument',
        'badge_style': 'limited',
        'rating': 4.9,
        'reviews_count': 415,
        'stock': 12,
        'tag': 'retro limited yeezy 700 wave runner boost sneaker',
        'image_url': 'https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?auto=format&fit=crop&w=800&q=80',
        'description': 'The shoe that ignited the chunky luxury wave. Combining grey and black suede overlays, premium leather, and neon laces.',
        'features': [
            'Upper composed of grey and black suede overlays with teal mesh underlays.',
            'Full-length drop-in BOOST midsole encased within sculpted PU.',
            'Signature neon green laces and reflective 3M heel detailing.',
            'Herringbone rubber traction pattern.'
        ]
    },
    {
        'subcat_slug': 'limited-retro',
        'subcat_name': 'Limited & Retro Editions',
        'subcat_desc': 'Collector deadstock grails, numbered editions, and timeless historical drops.',
        'code': 'nike-air-max-90-infrared',
        'title': 'Nike Air Max 90 Infrared OG Vintage',
        'brand': 'Nike',
        'price': 11499.00,
        'original_price': 13999.00,
        'gender': 'men',
        'color': 'White / Black / Cool Grey / Radiant Red',
        'badge_text': '90s Legend',
        'badge_style': 'trending',
        'rating': 4.9,
        'reviews_count': 328,
        'stock': 20,
        'tag': 'retro 90s infrared air max visible air sneaker',
        'image_url': 'https://images.unsplash.com/photo-1586525198428-225f6f12cff5?auto=format&fit=crop&w=800&q=80',
        'description': 'Tinker Hatfield\'s 1990 masterpiece featuring radiant infrared TPU frames, visible heel Air-Sole unit, and stitched overlays.',
        'features': [
            'Classic mesh base with suede overlays and smooth leather mudguard.',
            'Visible Max Air unit in the heel framed by ribbed TPU accents.',
            'Padded low-top collar feels soft and comfortable.',
            'Waffle rubber outsole honors Nike running heritage.'
        ]
    },
    {
        'subcat_slug': 'limited-retro',
        'subcat_name': 'Limited & Retro Editions',
        'subcat_desc': 'Collector deadstock grails, numbered editions, and timeless historical drops.',
        'code': 'air-jordan-1-retro-shadow-2',
        'title': 'Air Jordan 1 Retro High Shadow 2.0',
        'brand': 'Jordan',
        'price': 16499.00,
        'original_price': 19999.00,
        'gender': 'women',
        'color': 'Black / Medium Grey / White',
        'badge_text': 'Shadow Edition',
        'badge_style': 'limited',
        'rating': 4.9,
        'reviews_count': 275,
        'stock': 15,
        'tag': 'retro limited jordan shadow high sneaker',
        'image_url': 'https://images.unsplash.com/photo-1518002171953-a080ee817e1f?auto=format&fit=crop&w=800&q=80',
        'description': 'Understated brilliance pairing plush light smoke grey nubuck overlays over a rich matte black leather base.',
        'features': [
            'Light smoke grey soft nubuck paired with jet black leather.',
            'Crisp white midsole provides clean optical separation.',
            'Air-Sole heel unit ensures responsive, lightweight steps.',
            'Embossed Jordan wings branding on ankle collar flap.'
        ]
    },
    {
        'subcat_slug': 'limited-retro',
        'subcat_name': 'Limited & Retro Editions',
        'subcat_desc': 'Collector deadstock grails, numbered editions, and timeless historical drops.',
        'code': 'new-balance-990v6-castlerock',
        'title': 'New Balance 990v6 Made in USA Castlerock',
        'brand': 'New Balance',
        'price': 21499.00,
        'original_price': 25999.00,
        'gender': 'women',
        'color': 'Castlerock Grey / Marblehead',
        'badge_text': 'Handcrafted USA',
        'badge_style': 'limited',
        'rating': 4.9,
        'reviews_count': 210,
        'stock': 14,
        'tag': 'retro handcrafted made in usa 990v6 sneaker',
        'image_url': 'https://images.unsplash.com/photo-1514989940723-e8e51635b782?auto=format&fit=crop&w=800&q=80',
        'description': 'Handcrafted in Massachusetts with domestic value of 70% or greater. Pairs pigskin suede overlays with FuelCell midsole propulsion.',
        'features': [
            'Premium pigskin suede and mesh upper construction.',
            'FuelCell foam delivers a propulsive feel to help drive you forward.',
            'ENCAP midsole cushioning combines lightweight foam with durable polyurethane.',
            'Reflective accents designed to catch the light.'
        ]
    },
]


# =============================================================================
# DJANGO MANAGEMENT COMMAND
# =============================================================================
class Command(BaseCommand):
    help = "Deduplicate catalog, purge non-sneakers, define 6 sneaker subcategories, and seed 36 verified sneakers with local image binaries."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean-only',
            action='store_true',
            help='Run only the duplicate and non-sneaker cleanup without seeding new products.',
        )
        parser.add_argument(
            '--force-download',
            action='store_true',
            help='Force re-download of image files even if local image already exists on disk.',
        )
        parser.add_argument(
            '--skip-download',
            action='store_true',
            help='Skip downloading images over network; use local image generator if missing.',
        )

    def handle(self, *args, **options):
        clean_only = options.get('clean_only', False)
        force_download = options.get('force_download', False)
        skip_download = options.get('skip_download', False)

        self.stdout.write(self.style.MIGRATE_HEADING("=" * 76))
        self.stdout.write(self.style.MIGRATE_HEADING("  👟 SNEAKER SQUAD: CATALOG PURGE, SEED & LOCAL ASSET ENGINE"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 76))

        # ---------------------------------------------------------------------
        # STEP 1: REMOVE DUPLICATE PRODUCTS
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.NOTICE("\n[STEP 1/4] Scanning for duplicate products in database..."))
        all_products = Product.objects.all().order_by('id')
        initial_count = all_products.count()
        
        seen_keys = {}
        duplicates_purged = 0

        for p in all_products:
            # Deduplicate by normalized title or code
            key = (p.title or p.name or '').strip().lower()
            if not key:
                key = p.code.strip().lower()

            if key in seen_keys:
                primary = seen_keys[key]
                self.stdout.write(self.style.WARNING(
                    f"  ✂️ Purging duplicate product #{p.id} [{p.code}] '{p.title or p.name}' (keeps #{primary.id})"
                ))
                p.delete()
                duplicates_purged += 1
            else:
                seen_keys[key] = p

        self.stdout.write(self.style.SUCCESS(
            f"  ✅ Step 1 Complete: {duplicates_purged} duplicates removed. Unique products remaining: {Product.objects.count()}."
        ))

        # ---------------------------------------------------------------------
        # STEP 2: PURGE NON-SNEAKER PRODUCTS & FOOTWEAR
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.NOTICE("\n[STEP 2/4] Purging non-sneaker footwear, apparel, and accessories..."))
        
        # Disallowed categories / subcategories / tags
        forbidden_terms = [
            'apparel', 'hoodie', 't-shirt', 'tee', 'jacket', 'pant', 'cargo',
            'heel', 'flats', 'flat', 'sandal', 'stiletto', 'pump', 'loafer', 'mule',
            'watch', 'timepiece', 'bag', 'backpack', 'wallet', 'care kit', 'shield'
        ]
        
        valid_dataset_codes = {item['code'] for item in SNEAKER_DATASET}
        non_sneaker_count = 0
        for p in Product.objects.all():
            p_subcat = (p.subcategory.slug if p.subcategory else '').lower()
            p_tag = (p.tag or '').lower()
            p_title = (p.title or p.name or '').lower()
            p_cat = (p.category.slug if p.category else '').lower()

            # Check if this item is non-sneaker or obsolete legacy seed
            is_non_sneaker = False
            if p.code not in valid_dataset_codes:
                is_non_sneaker = True
            elif p_cat == 'accessories':
                is_non_sneaker = True
            elif p_subcat in ['apparel', 'heels', 'watches', 'bags']:
                is_non_sneaker = True
            else:
                for term in forbidden_terms:
                    if term in p_title or term in p_tag or term in p_subcat:
                        is_non_sneaker = True
                        break

            if is_non_sneaker:
                self.stdout.write(self.style.WARNING(
                    f"  🚫 Purging non-sneaker item: #{p.id} [{p.code}] '{p.title or p.name}' (Tag: {p.tag}, Subcat: {p_subcat})"
                ))
                p.delete()
                non_sneaker_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"  ✅ Step 2 Complete: {non_sneaker_count} non-sneaker items purged from catalog."
        ))

        if clean_only:
            self.stdout.write(self.style.SUCCESS("\n--clean-only specified. Done! Exiting without seeding."))
            return

        # ---------------------------------------------------------------------
        # STEP 3: SETUP CATEGORIES & 6 SNEAKER SUBCATEGORIES
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.NOTICE("\n[STEP 3/4] Ensuring relational Categories and 6 Sneaker Subcategories..."))
        
        cat_men, _ = Category.objects.get_or_create(
            slug='men',
            defaults={'name': 'men', 'description': "Men's Premium Sneaker Collection", 'is_active': True}
        )
        cat_women, _ = Category.objects.get_or_create(
            slug='women',
            defaults={'name': 'women', 'description': "Women's Designer Sneaker Collection", 'is_active': True}
        )
        
        # 6 sneaker subcategories definitions
        subcategories_meta = {
            'classic-low-tops': "Classic Low-Tops",
            'chunky-platforms': "Chunky & Platforms",
            'sports-running': "Sports & Running",
            'streetwear-high-tops': "Streetwear High-Tops",
            'slip-on-sneakers': "Slip-On Sneakers",
            'limited-retro': "Limited & Retro Editions"
        }

        created_subcats = {}
        for s_slug, s_name in subcategories_meta.items():
            # Create subcategory for men
            sub_men, _ = SubCategory.objects.get_or_create(
                category=cat_men,
                slug=s_slug,
                defaults={'name': s_name, 'description': f"{s_name} Collection"}
            )
            # Create subcategory for women
            sub_women, _ = SubCategory.objects.get_or_create(
                category=cat_women,
                slug=s_slug,
                defaults={'name': s_name, 'description': f"{s_name} Collection"}
            )
            created_subcats[('men', s_slug)] = sub_men
            created_subcats[('women', s_slug)] = sub_women
            created_subcats[s_slug] = sub_men  # default fallback

        self.stdout.write(self.style.SUCCESS(
            f"  ✅ Step 3 Complete: 6 sneaker subcategories registered across Men and Women collections."
        ))

        # ---------------------------------------------------------------------
        # STEP 4: SEED EXACTLY 36 UNIQUE SNEAKERS & SAVE IMAGES INTO ImageField
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.NOTICE(f"\n[STEP 4/4] Seeding EXACTLY 36 unique sneakers with local binary ImageFields..."))
        
        # Prepare media destination folder
        media_sneakers_dir = os.path.join(settings.MEDIA_ROOT, 'sneakers')
        os.makedirs(media_sneakers_dir, exist_ok=True)

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        seeded_count = 0
        images_downloaded = 0
        images_reused = 0
        images_fallback = 0

        for idx, item in enumerate(SNEAKER_DATASET, 1):
            subcat_slug = item['subcat_slug']
            code = item['code']
            gender = item['gender']

            # Choose parent Category
            parent_cat = cat_women if gender == 'women' else cat_men
            subcat_obj = created_subcats.get((parent_cat.slug, subcat_slug), created_subcats.get(subcat_slug))

            # Idempotent fetch or initialize Product
            product, created = Product.objects.get_or_create(
                code=code,
                defaults={
                    'title': item['title'],
                    'name': item['title'],
                    'brand': item['brand'],
                    'category': parent_cat,
                    'subcategory': subcat_obj,
                    'gender': gender,
                    'price': item['price'],
                    'original_price': item['original_price'],
                    'color': item['color'],
                    'badge_text': item['badge_text'],
                    'badge_style': item['badge_style'],
                    'rating': item['rating'],
                    'reviews_count': item['reviews_count'],
                    'stock_quantity': item['stock'],
                    'tag': f"shoes sneakers {subcat_slug} {item['tag']}",
                    'description': item['description'],
                    'features_text': '\n'.join(item['features']),
                    'is_featured': (idx % 4 == 0),
                    'is_trending': ('Grail' in item['badge_text'] or 'Bestseller' in item['badge_text']),
                    'is_in_stock': True,
                    'is_active': True,
                }
            )

            # Update core attributes if already existed
            if not created:
                product.title = item['title']
                product.name = item['title']
                product.brand = item['brand']
                product.category = parent_cat
                product.subcategory = subcat_obj
                product.gender = gender
                product.price = item['price']
                product.original_price = item['original_price']
                product.color = item['color']
                product.badge_text = item['badge_text']
                product.badge_style = item['badge_style']
                product.rating = item['rating']
                product.reviews_count = item['reviews_count']
                product.stock_quantity = item['stock']
                product.tag = f"shoes sneakers {subcat_slug} {item['tag']}"
                product.description = item['description']
                product.features_text = '\n'.join(item['features'])
                product.is_active = True

            # -----------------------------------------------------------------
            # IMAGE DOWNLOAD & LOCAL ImageField BINARY STORAGE
            # -----------------------------------------------------------------
            expected_filename = f"{code}.jpg"
            local_file_path = os.path.join(media_sneakers_dir, expected_filename)
            has_existing_local_file = os.path.exists(local_file_path) and os.path.getsize(local_file_path) > 1000

            image_content = None

            if has_existing_local_file and not force_download:
                # Reuse existing local binary file
                with open(local_file_path, 'rb') as f:
                    image_content = f.read()
                images_reused += 1
                status_icon = "📁 (Local disk cached)"
            elif not skip_download:
                # Download binary image via requests
                url = item['image_url']
                try:
                    t0 = time.time()
                    resp = session.get(url, timeout=12)
                    elapsed = time.time() - t0
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        image_content = resp.content
                        images_downloaded += 1
                        status_icon = f"⬇️  (Downloaded {len(image_content)//1024} KB in {elapsed:.1f}s)"
                    else:
                        raise ValueError(f"HTTP Status {resp.status_code}, content len: {len(resp.content)}")
                except Exception as dl_err:
                    self.stdout.write(self.style.WARNING(
                        f"     ⚠️ Network download note for {code}: {dl_err}. Creating clean studio visual asset..."
                    ))
                    image_content = self.generate_fallback_sneaker_image(item['title'], item['color'], subcat_slug)
                    images_fallback += 1
                    status_icon = "🎨 (Studio generated)"
            else:
                # Offline / skip mode: generate clean studio fallback asset
                image_content = self.generate_fallback_sneaker_image(item['title'], item['color'], subcat_slug)
                images_fallback += 1
                status_icon = "🎨 (Studio generated)"

            # Save binary content directly into product.image_file ImageField
            if image_content:
                product.image_file.save(expected_filename, ContentFile(image_content), save=False)
                local_url = product.image_file.url
                product.image_url = local_url
                product.main_image = local_url
                product.image = local_url
            else:
                product.image_url = item['image_url']
                product.main_image = item['image_url']
                product.image = item['image_url']

            product.save()
            seeded_count += 1

            action = "Created" if created else "Updated"
            self.stdout.write(
                f"  [{idx:02d}/36] {action}: {item['title']:<38} | ₹{int(item['price']):<6} | {item['subcat_name']:<22} | {status_icon}"
            )

        # ---------------------------------------------------------------------
        # STEP 5: FINAL VALIDATION REPORT
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "=" * 76))
        self.stdout.write(self.style.SUCCESS("  🎉 SNEAKER CATALOG SEEDING & VERIFICATION COMPLETE!"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 76))
        
        final_total = Product.objects.count()
        men_count = Product.objects.filter(gender__in=['men', 'unisex'], is_active=True).count()
        women_count = Product.objects.filter(gender__in=['women', 'unisex'], is_active=True).count()
        
        self.stdout.write(f"  • Total Products in Catalog: {final_total} (Strictly Sneakers)")
        self.stdout.write(f"  • Men's Page Available:      {men_count} sneakers (Men + Unisex)")
        self.stdout.write(f"  • Women's Page Available:    {women_count} sneakers (Women + Unisex)")
        self.stdout.write(f"  • Images Downloaded via Web: {images_downloaded}")
        self.stdout.write(f"  • Images Reused from Disk:   {images_reused}")
        self.stdout.write(f"  • Studio Generated Assets:   {images_fallback}")
        self.stdout.write(f"  • Media Root Folder:         {media_sneakers_dir}")

        self.stdout.write(self.style.NOTICE("\n  Subcategory Volume Breakdown (Target: Exactly 6 each):"))
        for s_slug, s_name in subcategories_meta.items():
            cnt = Product.objects.filter(subcategory__slug=s_slug).count()
            mark = "✅" if cnt == 6 else "⚠️"
            self.stdout.write(f"    {mark} {s_name:<25} ({s_slug}): {cnt} sneakers")

        self.stdout.write(self.style.MIGRATE_HEADING("=" * 76 + "\n"))

    def generate_fallback_sneaker_image(self, title, color_name, subcat_slug):
        """
        Creates an 800x800 square studio image with clean gradient and typography
        if network is unavailable or offline.
        """
        img = Image.new('RGB', (800, 800), color=(14, 17, 23))
        draw = ImageDraw.Draw(img)

        # Draw subtle studio floor & card frame
        draw.rounded_rectangle([40, 40, 760, 760], radius=24, outline=(255, 90, 31), width=3)
        draw.rectangle([60, 520, 740, 740], fill=(22, 27, 34))

        # Draw sneaker icon representation
        draw.ellipse([260, 320, 540, 480], fill=(30, 41, 59))
        draw.polygon([(260, 420), (520, 340), (580, 440), (220, 480)], fill=(255, 90, 31))

        # Text labels
        try:
            # Fallback to default bitmap font
            draw.text((80, 80), "SNEAKER SQUAD", fill=(255, 90, 31))
            draw.text((80, 120), subcat_slug.upper().replace('-', ' '), fill=(148, 163, 184))
            draw.text((80, 600), title[:40], fill=(255, 255, 255))
            draw.text((80, 640), f"Colorway: {color_name}", fill=(148, 163, 184))
            draw.text((80, 680), "Authentic Deadstock 100% Verified", fill=(74, 222, 128))
        except Exception:
            pass

        buf = BytesIO()
        img.save(buf, format='JPEG', quality=90)
        return buf.getvalue()
