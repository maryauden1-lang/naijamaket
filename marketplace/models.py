from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# ==========================================
# 1. SITE CONFIGURATION & CMS
# ==========================================
class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default="Naijamaket")
    tagline = models.CharField(max_length=255, default="Nigeria's Cleanest Buying & Selling Hub")
    logo = models.ImageField(
        upload_to="site_logos/", 
        blank=True, 
        null=True, 
        help_text="Upload website logo (PNG, SVG, or WebP with transparent background)"
    )
    support_phone = models.CharField(max_length=20, default="+2348000000000")
    support_whatsapp = models.CharField(max_length=20, default="2348000000000")
    support_email = models.EmailField(default="support@naijamaket.com")
    office_address = models.CharField(max_length=255, default="Lagos, Nigeria")
    
    # Social links
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    
    # Alert banner
    announcement_text = models.CharField(
        max_length=255, 
        blank=True, 
        default="⚠️ Tip: Always inspect goods physically in a public location before making payment."
    )
    show_announcement = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Global Site Setting"
        verbose_name_plural = "Global Site Settings"

    def __str__(self):
        return f"{self.site_name} Settings"


class StaticPage(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, help_text="e.g. safety-tips, privacy-policy")
    content = models.TextField(help_text="Full page content or HTML")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Custom Page (Terms, Safety, etc.)"
        verbose_name_plural = "Custom Pages"

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


# ==========================================
# 2. LOCATIONS (STATES & COMMERCIAL HUBS)
# ==========================================
class State(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Area(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="areas")
    name = models.CharField(max_length=100, help_text="e.g. Computer Village, Ikeja, Lekki Phase 1, Wuse 2")
    slug = models.SlugField(max_length=120, blank=True)
    is_popular = models.BooleanField(default=False, help_text="Show in popular quick-filters")

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.state.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.state.name})"


# ==========================================
# 3. CATEGORIES & SUBCATEGORIES
# ==========================================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.ImageField(upload_to="category_icons/", blank=True, null=True, help_text="Upload small PNG, WebP, or SVG icon")
    icon_name = models.CharField(max_length=50, default="tag", blank=True, help_text="Fallback icon name")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    icon = models.ImageField(upload_to="subcategory_icons/", blank=True, null=True, help_text="Upload small subcategory icon")

    class Meta:
        verbose_name_plural = "Sub-Categories"
        unique_together = ("category", "name")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} > {self.name}"


# ==========================================
# 4. USER PROFILES, STOREFRONTS & REVIEWS
# ==========================================
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Storefront Customization
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    store_banner = models.ImageField(upload_to="store_banners/", blank=True, null=True, help_text="Cover banner for store profile")
    shop_address = models.CharField(max_length=255, blank=True, null=True, help_text="Physical store address (e.g. Shop B4, Banex Plaza)")
    
    # Social Media Handles
    facebook_handle = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. facebook.com/username or @username")
    instagram_handle = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. @username")
    tiktok_handle = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. @username")
    
    # Verification & Admin Controls
    is_nin_verified = models.BooleanField(default=False, verbose_name="NIN Verified Badge")
    is_cac_verified = models.BooleanField(default=False, verbose_name="CAC Business Verified")
    id_document = models.FileField(upload_to="verifications/", blank=True, null=True, help_text="NIN Slip or ID card for review")
    cac_document = models.FileField(upload_to="cac_verifications/", blank=True, null=True, help_text="CAC Certificate")
    bio = models.TextField(blank=True, null=True)
    response_time = models.CharField(max_length=50, default="Replies typically within 1 hour")
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({'Verified' if self.is_nin_verified else 'Unverified'})"


class SellerReview(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")
    rating = models.PositiveSmallIntegerField(default=5, help_text="Rating 1 to 5")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review for {self.seller.username} by {self.reviewer.username} ({self.rating}★)"


# ==========================================
# 5. LISTINGS & MULTI-IMAGE MANAGEMENT
# ==========================================
class Listing(models.Model):
    CONDITION_CHOICES = (
        ("brand_new", "Brand New"),
        ("tokunbo", "Foreign Used (Tokunbo)"),
        ("nigerian_used", "Nigerian Used"),
    )

    STATUS_CHOICES = (
        ("active", "Active / Approved"),
        ("pending", "Pending Moderation"),
        ("rejected", "Rejected"),
        ("sold", "Sold"),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)  # In Naira
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="tokunbo")
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    
    # Status & Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Listing.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - ₦{self.price}"


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="listings/%Y/%m/")
    is_cover = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_cover", "id"]

    def __str__(self):
        return f"Image for {self.listing.title}"


# ==========================================
# 6. SAVED ADS / FAVORITES WISHLIST
# ==========================================
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "listing")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.listing.title}"


# ==========================================
# 7. IN-APP MESSAGING SYSTEM (REAL-TIME CHAT)
# ==========================================
class Conversation(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="conversations")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer_conversations")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("listing", "buyer")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Chat for {self.listing.title} ({self.buyer.username} & {self.seller.username})"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.sender.username} at {self.created_at.strftime('%H:%M')}"


# ==========================================
# 8. SAFETY, FRAUD & REPORTING
# ==========================================
class ReportedListing(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reports")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(
        max_length=50,
        choices=(
            ("fraud", "Suspected Scam / Fraud"),
            ("fake_price", "Fake / Unrealistic Price"),
            ("prohibited", "Prohibited / Illegal Item"),
            ("unavailable", "Item is already sold / not available"),
            ("other", "Other Reason"),
        ),
    )
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report: {self.listing.title} ({self.get_reason_display()})"