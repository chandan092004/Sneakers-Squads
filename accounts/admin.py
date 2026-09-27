from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserProfile,
    UserAddress,
    WishlistItem,
    PasswordResetToken,
    Order,
    OrderItem,
    Category,
    Product,
    ContactMessage
)

# Customize Admin Site Headers
admin.site.site_header = "SNEAKER SQUAD Admin Control"
admin.site.site_title = "Sneaker Squad Portal"
admin.site.index_title = "Store & Customer Management"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'name',
        'brand',
        'gender',
        'price',
        'stock_quantity',
        'is_in_stock',
        'is_featured',
        'is_active'
    )
    list_display_links = ('image_thumbnail', 'name')
    list_editable = ('price', 'stock_quantity', 'is_in_stock', 'is_featured', 'is_active')
    search_fields = ('name', 'brand', 'code', 'description', 'tag')
    list_filter = ('gender', 'brand', 'category', 'is_in_stock', 'is_featured', 'is_active')
    list_per_page = 20

    fieldsets = (
        ('👟 Essential Product Details (Quick Fill)', {
            'description': 'Sirf ye zaroori details bharein aur Product save karein:',
            'fields': (
                ('name', 'brand'),
                ('price', 'original_price'),
                ('category', 'gender'),
                ('main_image', 'stock_quantity'),
            )
        }),
        ('⚙️ Advanced & Optional Options (Click to Expand)', {
            'classes': ('collapse',),
            'description': 'Advanced settings aur additional styling options:',
            'fields': (
                'code',
                'tag',
                ('badge_text', 'badge_style'),
                'gallery_images',
                'description',
                'features_text',
                'specs_json',
                'sizes_list',
                ('rating', 'reviews_count'),
                ('is_in_stock', 'is_featured', 'is_trending', 'is_active')
            )
        }),
    )

    def image_thumbnail(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="width: 44px; height: 44px; object-fit: cover; border-radius: 6px; border: 1.5px solid #ff5a1f; background: #0b0d13;" />',
                obj.main_image
            )
        return "No Image"
    image_thumbnail.short_description = "Preview"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_id', 'product_name', 'product_price', 'quantity', 'size', 'color')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'full_name',
        'phone',
        'city',
        'total_amount',
        'status',
        'payment_status',
        'created_at'
    )
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_id', 'full_name', 'email', 'phone', 'tracking_number')
    list_editable = ('status', 'payment_status')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('📦 Essential Order Details (Quick Fill)', {
            'description': 'Customer aur Order ki main details:',
            'fields': (
                ('full_name', 'phone'),
                ('city', 'street_address'),
                ('total_amount', 'status', 'payment_status'),
            )
        }),
        ('🚚 Shipping, User & Advanced Info (Optional)', {
            'classes': ('collapse',),
            'fields': (
                'user',
                'order_id',
                'email',
                'pincode',
                ('discount_amount', 'shipping_fee'),
                'payment_method',
                ('courier_partner', 'tracking_number', 'estimated_delivery'),
                ('created_at', 'updated_at')
            )
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'show_in_navbar', 'is_active', 'display_order')
    list_editable = ('show_in_navbar', 'is_active', 'display_order')
    search_fields = ('name', 'slug')
    list_filter = ('is_active', 'show_in_navbar')

    fieldsets = (
        ('🏷️ Essential Category Details', {
            'fields': (
                'name',
                'icon_class',
                ('is_active', 'show_in_navbar')
            )
        }),
        ('🎨 Extra Customization (Optional)', {
            'classes': ('collapse',),
            'fields': (
                'slug',
                'description',
                'banner_image',
                'display_order'
            )
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'status', 'created_at')
    list_filter = ('status', 'issue_type', 'created_at')
    search_fields = ('name', 'email', 'phone', 'order_id', 'subject', 'message')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    fieldsets = (
        ('💬 Essential Inquiry Details', {
            'fields': (
                ('name', 'email'),
                'phone',
                'subject',
                'message',
                ('status', 'admin_reply'),
            )
        }),
        ('🔍 Additional Metadata (Optional)', {
            'classes': ('collapse',),
            'fields': (
                ('order_id', 'issue_type'),
                'user',
                ('created_at', 'updated_at')
            )
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    list_filter = ('is_verified', 'created_at')

    fieldsets = (
        ('👤 Essential Profile Details', {
            'fields': (
                'user',
                ('phone', 'city'),
                'is_verified'
            )
        }),
        ('🖼️ Additional Profile Details (Optional)', {
            'classes': ('collapse',),
            'fields': (
                ('gender', 'state'),
                ('avatar', 'avatar_url')
            )
        }),
    )


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'phone', 'address_type', 'is_default')
    search_fields = ('full_name', 'phone', 'city', 'pincode', 'user__username')
    list_filter = ('address_type', 'is_default')

    fieldsets = (
        ('📍 Essential Address Details', {
            'fields': (
                ('user', 'full_name'),
                ('phone', 'city'),
                'street_address',
                'pincode'
            )
        }),
        ('🏢 Extra Address Details (Optional)', {
            'classes': ('collapse',),
            'fields': (
                'apartment_suite',
                'state',
                ('address_type', 'is_default')
            )
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'otp_code')
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('🔑 Token Details (Essential)', {
            'fields': (
                'user',
                'otp_code',
                'is_used'
            )
        }),
        ('🛡️ System Token (Optional)', {
            'classes': ('collapse',),
            'fields': (
                'token',
                'created_at'
            )
        }),
    )


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_name', 'product_price', 'added_at')
    search_fields = ('user__username', 'product_id', 'product_name')
    list_filter = ('added_at',)
    fields = ('user', 'product_id', 'product_name', 'product_price', 'product_image')
