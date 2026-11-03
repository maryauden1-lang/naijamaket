from django import forms
from django.contrib.auth.models import User
from .models import Listing, SellerProfile, SellerReview, ReportedListing


class UserRegisterForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Full Name',
            'class': 'w-full bg-[#F3F4FB] text-slate-800 placeholder-slate-400 px-4 py-3.5 rounded-lg text-sm border border-transparent focus:border-[#2250EB] focus:bg-white focus:outline-hidden transition-all'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'w-full bg-[#F3F4FB] text-slate-800 placeholder-slate-400 px-4 py-3.5 rounded-lg text-sm border border-transparent focus:border-[#2250EB] focus:bg-white focus:outline-hidden transition-all'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'id': 'regPassword',
            'class': 'w-full bg-[#F3F4FB] text-slate-800 placeholder-slate-400 px-4 py-3.5 rounded-lg text-sm border border-transparent focus:border-[#2250EB] focus:bg-white focus:outline-hidden transition-all pr-11'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password',
            'id': 'regConfirmPassword',
            'class': 'w-full bg-[#F3F4FB] text-slate-800 placeholder-slate-400 px-4 py-3.5 rounded-lg text-sm border border-transparent focus:border-[#2250EB] focus:bg-white focus:outline-hidden transition-all pr-11'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone number (optional)',
            'class': 'w-full bg-[#F3F4FB] text-slate-800 placeholder-slate-400 px-4 py-3.5 rounded-lg text-sm border border-transparent focus:border-[#2250EB] focus:bg-white focus:outline-hidden transition-all'
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        pwd_confirm = cleaned_data.get("confirm_password")

        if pwd and pwd_confirm and pwd != pwd_confirm:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-xs text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 cursor-pointer'
        })
    )
    store_banner = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-xs text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 cursor-pointer'
        })
    )

    class Meta:
        model = SellerProfile
        fields = [
            'avatar',
            'store_banner',
            'phone_number',
            'whatsapp_number',
            'shop_address',
            'state',
            'area',
            'instagram_handle',
            'facebook_handle',
            'tiktok_handle',
            'bio',
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': '08012345678',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'placeholder': '2348012345678',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'shop_address': forms.TextInput(attrs={
                'placeholder': 'e.g. Shop B12, Emab Plaza, Wuse 2, Abuja',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'state': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'area': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'instagram_handle': forms.TextInput(attrs={
                'placeholder': '@yourstore',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'facebook_handle': forms.TextInput(attrs={
                'placeholder': 'facebook.com/yourstore',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'tiktok_handle': forms.TextInput(attrs={
                'placeholder': '@yourstore',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Tell buyers about your shop, warranty, or delivery policies...',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
        }


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'subcategory', 'price', 'condition', 'state', 'area', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. iPhone 14 Pro Max 256GB Gold (Tokunbo)',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'subcategory': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Amount in Naira (e.g. 450000)',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'condition': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'state': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'area': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe your item thoroughly (condition, included accessories, reason for selling)...',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-sm bg-slate-50/50'
            }),
        }


class ReportListingForm(forms.ModelForm):
    class Meta:
        model = ReportedListing
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-rose-500 focus:outline-hidden text-xs bg-slate-50/50'
            }),
            'details': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Provide specific details for moderation review...',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-rose-500 focus:outline-hidden text-xs bg-slate-50/50'
            }),
        }


class SellerReviewForm(forms.ModelForm):
    class Meta:
        model = SellerReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(5, '⭐⭐⭐⭐⭐ (5 Stars)'), (4, '⭐⭐⭐⭐ (4 Stars)'), (3, '⭐⭐⭐ (3 Stars)'), (2, '⭐⭐ (2 Stars)'), (1, '⭐ (1 Star)')],
                attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-xs bg-slate-50/50'}
            ),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share your experience with this seller...',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden text-xs bg-slate-50/50'
            }),
        }