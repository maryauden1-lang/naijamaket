from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteSetting,
    StaticPage,
    FAQ,
    State,
    Area,
    Category,
    SubCategory,
    SellerProfile,
    SellerReview,
    Listing,
    ListingImage,
    Favorite,
    Conversation,
    Message,
    ReportedListing,
    StaffProfile,
    StaffActivityLog,
)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = (
        "site_name", 
        "logo_preview", 
        "support_phone", 
        "support_email", 
        "show_announcement", 
        "maintenance_mode"
    )
    readonly_fields = ("logo_preview",)
    fieldsets = (
        ("Branding & Identity", {
            "fields": ("site_name", "tagline", "logo", "logo_preview")
        }),
        ("Customer Support & Location", {
            "fields": ("support_phone", "support_whatsapp", "support_email", "office_address")
        }),
        ("Social Profiles", {
            "fields": ("facebook_url", "twitter_url", "instagram_url")
        }),
        ("Platform Banners & Status", {
            "fields": ("announcement_text", "show_announcement", "maintenance_mode")
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 45px; max-width: 140px; border-radius: 8px; object-fit: contain; background: #5B21B6; padding: 4px;" />',
                obj.logo.url
            )
        return "No logo uploaded"
    logo_preview.short_description = "Live Logo Preview"


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "updated_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order")


class AreaInline(admin.TabularInline):
    model = Area
    extra = 1


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AreaInline]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "is_popular")
    list_filter = ("state", "is_popular")
    search_fields = ("name", "state__name")


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon_name", "order")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubCategoryInline]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug")
    list_filter = ("category",)
    search_fields = ("name", "category__name")


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "is_nin_verified", "is_cac_verified", "state", "area", "is_banned")
    list_editable = ("is_nin_verified", "is_cac_verified")
    list_filter = ("is_nin_verified", "is_cac_verified", "state", "is_banned")
    search_fields = ("user__username", "phone_number", "whatsapp_number", "instagram_handle")


@admin.register(SellerReview)
class SellerReviewAdmin(admin.ModelAdmin):
    list_display = ("seller", "reviewer", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("seller__username", "reviewer__username", "comment")


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "price",
        "category",
        "seller",
        "condition",
        "state",
        "area",
        "status",
        "is_featured",
        "created_at",
    )
    list_filter = ("status", "is_featured", "condition", "state", "category")
    search_fields = ("title", "description", "seller__username")
    list_editable = ("status", "is_featured")
    inlines = [ListingImageInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "created_at")
    search_fields = ("user__username", "listing__title")


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "text", "is_read", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("listing", "buyer", "seller", "updated_at")
    search_fields = ("listing__title", "buyer__username", "seller__username")
    inlines = [MessageInline]


@admin.register(ReportedListing)
class ReportedListingAdmin(admin.ModelAdmin):
    list_display = ("listing", "reason", "reported_by", "created_at", "is_resolved")
    list_filter = ("reason", "is_resolved", "created_at")
    list_editable = ("is_resolved",)


# =========================================================================
# 9. CEO STAFF CONTROLS & IMMUTABLE AUDIT TRAIL (SUPERUSER ONLY)
# =========================================================================
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "get_staff_name", "role", "phone", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("employee_id", "user__username", "user__first_name", "user__last_name", "phone")
    list_editable = ("is_active",)

    def get_staff_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_staff_name.short_description = "Staff Member"


@admin.register(StaffActivityLog)
class StaffActivityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "staff", "action", "target_object_id", "ip_address")
    list_filter = ("action", "timestamp", "staff")
    search_fields = ("staff__username", "target_object_id", "details", "ip_address")
    readonly_fields = ("staff", "action", "target_object_id", "details", "ip_address", "timestamp")

    def has_add_permission(self, request):
        return False  # Audit logs can never be manually forged

    def has_delete_permission(self, request, obj=None):
        return False  # Audit logs can never be deleted