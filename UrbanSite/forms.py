# UrbanSite/forms.py
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import UserReport, Authority
from .security import validate_file_upload, validate_content_for_spam

# Ahmedabad pincode range: 380001 to 380060
AHMEDABAD_PINCODES = set(range(380001, 380061))


def validate_ahmedabad_pincode(value):
    """
    Validate that the pincode is within Ahmedabad range (380001-380060).
    """
    try:
        pincode_int = int(value)
        if pincode_int not in AHMEDABAD_PINCODES:
            raise ValidationError(
                f"Reporting is limited to Ahmedabad only. Pincode {value} is not valid. "
                "Please use an Ahmedabad pincode (380001-380060)."
            )
    except (ValueError, TypeError):
        raise ValidationError("Invalid pincode format. Must be 6 digits.")


class UserReportForm(forms.ModelForm):
    """
    Form for submitting civic issue reports.
    Includes Ahmedabad pincode validation and reCAPTCHA placeholder.
    """
    # ReCAPTCHA placeholder (will be integrated with actual keys)
    recaptcha_token = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="reCAPTCHA token"
    )

    class Meta:
        model = UserReport
        fields = [
            'name', 'email', 'phone', 'area', 'pincode', 'address',
            'problem_type', 'description', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 9876543210',
                'required': True,
            }),
            'area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Area/Ward name (e.g., Navrangpura, Satellite)',
                'required': True,
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '380001',
                'maxlength': '6',
                'pattern': '[0-9]{6}',
                'required': True,
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed address (optional)',
            }),
            'problem_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the issue in detail...',
                'required': True,
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['area'].required = True
        self.fields['pincode'].required = True
        self.fields['problem_type'].required = True
        self.fields['description'].required = True

    def clean_pincode(self):
        """
        Validate pincode is in Ahmedabad range.
        """
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            validate_ahmedabad_pincode(pincode)
        return pincode

    def clean_image(self):
        """
        Validate image file using comprehensive security checks.
        """
        image = self.cleaned_data.get('image')
        if image:
            # Use security module for comprehensive validation
            validate_file_upload(image)
        return image
    
    def clean_description(self):
        """
        Validate description for spam content.
        """
        description = self.cleaned_data.get('description')
        if description:
            validate_content_for_spam(description, field_name="description")
        return description

    def clean(self):
        """
        Additional form-level validation.
        """
        cleaned_data = super().clean()
        
        # Store IP address and user agent for spam protection
        if self.request:
            cleaned_data['ip_address'] = self.get_client_ip()
            cleaned_data['user_agent'] = self.request.META.get('HTTP_USER_AGENT', '')
        
        return cleaned_data

    def get_client_ip(self):
        """
        Get client IP address from request.
        """
        if not self.request:
            return None
        
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

