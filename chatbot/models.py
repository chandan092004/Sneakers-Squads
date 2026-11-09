from django.db import models

class Offer(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Promo/Coupon Code (e.g. SQUAD20)")
    description = models.CharField(max_length=255, help_text="Short description of offer")
    discount_percent = models.PositiveIntegerField(default=10, help_text="Discount percentage (e.g. 20 for 20%)")
    active = models.BooleanField(default=True, help_text="Whether this offer is currently active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-discount_percent', '-created_at']
        verbose_name = 'Special Offer / Coupon'
        verbose_name_plural = 'Special Offers & Coupons'

    def __str__(self):
        return f"{self.code} - {self.discount_percent}% OFF ({self.description})"
