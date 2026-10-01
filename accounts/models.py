from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import random
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.FileField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.CharField(max_length=500, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_display_name(self):
        if self.user.first_name:
            if self.user.last_name:
                return f"{self.user.first_name} {self.user.last_name}"
            return self.user.first_name
        return self.user.username

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        if self.avatar_url:
            return self.avatar_url
        # Modern default avatar using UI Avatars with user initials
        initials = (self.user.first_name[:1] + (self.user.last_name[:1] if self.user.last_name else '')).upper()
        if not initials:
            initials = self.user.username[:2].upper()
        return f"https://ui-avatars.com/api/?name={initials}&background=ff5a1f&color=ffffff&bold=true&size=128"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance)


class UserAddress(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('home', 'Home (All day delivery)'),
        ('work', 'Work / Office (Delivery 9 AM - 6 PM)'),
        ('other', 'Other'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='home')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    apartment_suite = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'User Address'
        verbose_name_plural = 'User Addresses'

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.address_type})"

    def save(self, *args, **kwargs):
        # If set as default, ensure other addresses for this user are not default
        if self.is_default:
            UserAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        else:
            # If user has no other addresses, make this first one default
            if not UserAddress.objects.filter(user=self.user).exclude(pk=self.pk).exists():
                self.is_default = True
        super().save(*args, **kwargs)


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=200, blank=True, null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_image = models.CharField(max_length=500, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product_id')
        ordering = ['-added_at']
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'

    def __str__(self):
        return f"{self.user.username} - {self.product_name or self.product_id}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    otp_code = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def is_valid(self):
        # Token valid for 24 hours
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(hours=24)

    def __str__(self):
        return f"Reset Token for {self.user.username} (OTP: {self.otp_code})"


class Order(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Order Placed & Confirmed'),
        ('PACKED', 'Packed & Ready to Ship'),
        ('SHIPPED', 'In Transit / Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash On Delivery'),
        ('UPI', 'Instant UPI / QR'),
        ('CARD', 'Credit / Debit Card'),
        ('NETBANKING', 'Net Banking'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_id = models.CharField(max_length=50, unique=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=20)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, default='110001')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_status = models.CharField(max_length=20, default='Pending')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='CONFIRMED')
    
    # Razorpay / Payment Gateway Audit Fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    
    courier_partner = models.CharField(max_length=100, default='Blue Dart Express (Air Speed)', blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Order'
        verbose_name_plural = 'Customer Orders'

    def __str__(self):
        return f"Order #{self.order_id} - {self.full_name} (₹{self.total_amount})"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"SQUAD-{random.randint(10000, 99999)}"
        if not self.tracking_number:
            self.tracking_number = f"BD-{random.randint(10000000, 99999999)}"
        if not self.invoice_number:
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m')}-{random.randint(1000, 9999)}"
        if not self.estimated_delivery:
            est_date = (timezone.now() + timedelta(days=4)).strftime("%d %b %Y")
            self.estimated_delivery = est_date
        super().save(*args, **kwargs)

    def get_progress_step(self):
        steps = {
            'CONFIRMED': 1,
            'PACKED': 2,
            'SHIPPED': 3,
            'OUT_FOR_DELIVERY': 4,
            'DELIVERED': 5,
            'CANCELLED': 0,
        }
        return steps.get(self.status, 1)

    def get_tax_breakup(self):
        """Calculate GST 18% inclusive breakup for invoice"""
        total = float(self.total_amount)
        # Price inclusive of 18% GST: Base = Total / 1.18, Tax = Total - Base
        base_price = round(total / 1.18, 2)
        tax_amount = round(total - base_price, 2)
        cgst = round(tax_amount / 2, 2)
        sgst = round(tax_amount / 2, 2)
        return {
            'base_price': base_price,
            'tax_amount': tax_amount,
            'cgst': cgst,
            'sgst': sgst,
            'total': total
        }



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    product_image = models.CharField(max_length=500, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - Order #{self.order.order_id}"

    def get_total_price(self):
        return self.product_price * self.quantity


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Category Name (e.g. Kids, Running, Streetwear, Limited Edition)")
    slug = models.SlugField(max_length=120, unique=True, blank=True, help_text="URL slug (e.g. kids, running). Auto-generated if left blank.")
    description = models.TextField(blank=True, null=True, help_text="Category description / tagline for banner")
    banner_image = models.CharField(max_length=500, blank=True, null=True, help_text="Optional banner image URL")
    icon_class = models.CharField(max_length=50, default='fa-shoe-prints', help_text="FontAwesome icon class (e.g. fa-fire, fa-child, fa-bolt)")
    is_active = models.BooleanField(default=True, help_text="Check to activate this category on the website")
    show_in_navbar = models.BooleanField(default=True, help_text="Check to automatically add to top navigation bar")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in navbar / menus (lowest first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/{self.slug}.html"


class Product(models.Model):
    GENDER_CHOICES = (
        ('men', 'Men'),
        ('women', 'Women'),
        ('accessories', 'Accessories & Shoe Care'),
        ('kids', 'Kids & Juniors'),
        ('unisex', 'Unisex'),
    )
    BADGE_STYLE_CHOICES = (
        ('new', 'New Drop (Neon Orange)'),
        ('limited', 'Limited Edition (Purple Glow)'),
        ('sale', 'Hot Deal / Sale (Red)'),
        ('trending', 'Trending / Bestseller (Emerald Green)'),
    )

    code = models.CharField(max_length=80, unique=True, blank=True, help_text="Unique Product Code (Auto-generated if left blank)")
    name = models.CharField(max_length=200, help_text="Product Title (e.g. Nike Air Jordan 1)")
    brand = models.CharField(max_length=100, default='Nike / Jordan', help_text="Brand Name")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='men')
    
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling Price in INR (₹)")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Original MRP before discount")
    
    tag = models.CharField(max_length=100, default='high-top', blank=True, help_text="Category tags for filters")
    badge_text = models.CharField(max_length=50, blank=True, null=True, help_text="Badge label on card")
    badge_style = models.CharField(max_length=20, choices=BADGE_STYLE_CHOICES, default='new', blank=True)
    
    main_image = models.CharField(max_length=500, default='/static/img/shoe-1.jpg', help_text="Primary shoe image URL or /static path")
    gallery_images = models.TextField(blank=True, null=True, help_text="Optional gallery image URLs (comma or newline separated)")
    
    description = models.TextField(blank=True, null=True, help_text="Shoe description")
    features_text = models.TextField(blank=True, null=True, help_text="Key features (one per line)")
    specs_json = models.TextField(blank=True, null=True, help_text="Technical specifications")
    sizes_list = models.CharField(max_length=300, default='UK 6, UK 7, UK 8, UK 9, UK 10, UK 11', blank=True, help_text="Available shoe sizes")
    
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8, blank=True)
    reviews_count = models.PositiveIntegerField(default=24, blank=True)
    stock_quantity = models.PositiveIntegerField(default=20, help_text="Stock quantity available")
    
    is_in_stock = models.BooleanField(default=True, help_text="In Stock status")
    is_featured = models.BooleanField(default=False, help_text="Feature on Home Page")
    is_trending = models.BooleanField(default=False, help_text="Highlight as trending drop")
    is_active = models.BooleanField(default=True, help_text="Visible in store")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Sneaker & Product'
        verbose_name_plural = 'Sneakers & Products'

    def __str__(self):
        return f"{self.name} ({self.brand}) - ₹{self.price}"

    def save(self, *args, **kwargs):
        if not self.code:
            from django.utils.text import slugify
            base_slug = slugify(self.name) or "sneaker"
            candidate = base_slug
            counter = 1
            while Product.objects.filter(code=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.code = candidate
        super().save(*args, **kwargs)

    def get_discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            diff = self.original_price - self.price
            return int((diff / self.original_price) * 100)
        return 0

    def get_gallery_list(self):
        images = [self.main_image]
        if self.gallery_images:
            for line in self.gallery_images.replace(',', '\n').split('\n'):
                cleaned = line.strip()
                if cleaned and cleaned not in images:
                    images.append(cleaned)
        return images

    def get_features_list(self):
        if not self.features_text:
            return []
        return [f.strip() for f in self.features_text.split('\n') if f.strip()]

    def get_sizes_array(self):
        if not self.sizes_list:
            return ['UK 7', 'UK 8', 'UK 9', 'UK 10']
        return [s.strip() for s in self.sizes_list.split(',') if s.strip()]

    def to_dict(self):
        """Serialize into identical JSON schema required by products-data.js & cart"""
        import json as json_lib
        discount_pct = self.get_discount_percentage()
        gallery = self.get_gallery_list()
        features = self.get_features_list()
        sizes = self.get_sizes_array()

        specs = {}
        if self.specs_json:
            try:
                specs = json_lib.loads(self.specs_json)
            except Exception:
                for line in self.specs_json.split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        specs[k.strip()] = v.strip()

        return {
            'id': self.code,
            'name': self.name,
            'brand': self.brand,
            'category': self.category.name if self.category else (self.gender.capitalize() + " Footwear"),
            'categoryTag': self.tag,
            'gender': self.gender,
            'price': float(self.price),
            'originalPrice': float(self.original_price) if self.original_price else float(self.price * 1.2),
            'discount': f"-{discount_pct}%" if discount_pct > 0 else '',
            'rating': float(self.rating),
            'reviewsCount': self.reviews_count,
            'badge': self.badge_text or ('Bestseller' if self.is_trending else 'New Drop'),
            'badgeClass': self.badge_style,
            'mainImage': self.main_image,
            'gallery': gallery,
            'description': self.description or f"Authentic deadstock {self.name} engineered with premium materials.",
            'features': features or [
                "Deadstock Certified Authentic: Inspected and authenticated by our squad specialists.",
                "High-Traction Outsole: Precision multi-directional rubber pattern for street grip.",
                "Adaptive Cushioning Core: High-energy return compound absorbs impact.",
                "Breathable Premium Upper: Multi-panel durable construction."
            ],
            'specs': specs or {
                "Brand": self.brand,
                "Closure": "Lace-Up",
                "Upper Material": "Premium Leather & Mesh",
                "Sole": "High-Abrasion Rubber",
                "Authenticity": "100% Deadstock Verified"
            },
            'sizes': sizes,
            'inStock': self.is_in_stock and (self.stock_quantity > 0)
        }


class ContactMessage(models.Model):
    ISSUE_TYPE_CHOICES = (
        ('order_status', 'Order Tracking & Status'),
        ('return_refund', 'Return / Replacement / Refund'),
        ('product_defect', 'Damaged or Wrong Item'),
        ('size_fit', 'Sizing & Fit Query'),
        ('payment_issue', 'Payment & Billing'),
        ('general_feedback', 'General Feedback / Inquiries'),
    )
    STATUS_CHOICES = (
        ('NEW', 'New Inbound Inquiry'),
        ('IN_PROGRESS', 'In Progress / Assigned'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    )

    name = models.CharField(max_length=150, help_text="Customer Full Name")
    email = models.EmailField(help_text="Customer Contact Email")
    phone = models.CharField(max_length=25, blank=True, null=True, help_text="Contact Phone Number")
    order_id = models.CharField(max_length=50, blank=True, null=True, help_text="Related Order ID (if any)")
    issue_type = models.CharField(max_length=40, choices=ISSUE_TYPE_CHOICES, default='order_status')
    subject = models.CharField(max_length=250, blank=True, null=True, help_text="Subject / Short Topic")
    message = models.TextField(help_text="Inquiry or issue details from customer")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    admin_reply = models.TextField(blank=True, null=True, help_text="Internal Admin notes or resolution reply")
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Support Message'
        verbose_name_plural = 'Customer Support Messages'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.name} - {self.get_issue_type_display()} ({self.created_at.strftime('%d %b %Y')})"


class ProductReview(models.Model):
    RATING_CHOICES = (
        (5, '★★★★★ (5/5) - Outstanding / Fire'),
        (4, '★★★★☆ (4/5) - Great Quality'),
        (3, '★★★☆☆ (3/5) - Average / Good'),
        (2, '★★☆☆☆ (2/5) - Below Average'),
        (1, '★☆☆☆☆ (1/5) - Poor / Disappointed'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    product_code = models.CharField(max_length=100, help_text="Product Code / Slug", db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_reviews')
    user_name = models.CharField(max_length=120, help_text="Reviewer Name")
    user_email = models.EmailField(blank=True, default='')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5, help_text="Star Rating (1 to 5)")
    title = models.CharField(max_length=200, blank=True, null=True, help_text="Review Headline / Summary")
    comment = models.TextField(help_text="Detailed review comments")
    review_image = models.FileField(upload_to='review_photos/', blank=True, null=True, help_text="Customer photo of sneaker")
    is_verified_buyer = models.BooleanField(default=True, help_text="Display Verified Buyer Squad Badge")
    is_approved = models.BooleanField(default=True, help_text="Check to make visible on live store")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Sneaker Review'
        verbose_name_plural = 'Customer Sneaker Reviews'

    def __str__(self):
        return f"{self.user_name} - {self.rating}★ for {self.product_code}"

    def get_avatar_url(self):
        if self.user and hasattr(self.user, 'profile') and self.user.profile.avatar:
            return self.user.profile.get_avatar_url()
        initials = ''.join([part[0] for part in self.user_name.split()[:2]]).upper() if self.user_name else 'SQ'
        return f"https://ui-avatars.com/api/?name={initials}&background=ff5a1f&color=ffffff&bold=true&size=100"

    def get_stars_array(self):
        return list(range(1, 6))

    def to_dict(self):
        image_url = ''
        if self.review_image:
            try:
                image_url = self.review_image.url
            except Exception:
                image_url = str(self.review_image)
        return {
            'id': self.id,
            'userName': self.user_name,
            'avatar': self.get_avatar_url(),
            'rating': self.rating,
            'title': self.title or '',
            'comment': self.comment,
            'image': image_url,
            'isVerified': self.is_verified_buyer,
            'date': self.created_at.strftime("%d %b %Y")
        }



