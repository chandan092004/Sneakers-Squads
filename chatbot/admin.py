from django.contrib import admin
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active', 'description', 'created_at')
    list_filter = ('active',)
    search_fields = ('code', 'description')
