from django.contrib import admin
from django.utils.html import format_html

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "price",
        "stock",
        "is_active",
        "created_at",
        "admin_image",
    )
    list_display_links = ("id", "name")
    search_fields = ("name", "code", "description")
    list_filter = ("is_active", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "admin_image")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "code", "slug", "description", "comment", "image")}),
        ("Inventario y Precio", {"fields": ("price", "stock", "is_active")}),
        ("Tiempos", {"fields": ("created_at", "updated_at")}),
    )

    def admin_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:100px;"/>', obj.image.url
            )
        return "-"

    admin_image.short_description = "Imagen"


# ...existing code...
