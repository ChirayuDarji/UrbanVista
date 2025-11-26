from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from core.validators import validate_image_file

from .models import TravelExperience, ExperienceComment

# ===========================
# Travel Experience Form
# ===========================
class TravelExperienceForm(forms.ModelForm):
    def __init__(self, *args, experience_type=None, **kwargs):
        """
        Pass experience_type from the view so validation does not rely on
        a user-editable field.
        """
        super().__init__(*args, **kwargs)
        self.experience_type = experience_type  # 'place' | 'activity' | 'story' | 'tip'

        # Small UX tweaks
        self.fields['title'].widget.attrs.setdefault('placeholder', 'Give it a clear title')
        self.fields['location'].widget.attrs.setdefault('placeholder', 'Address or place name')
        self.fields['latitude'].widget.attrs.setdefault('step', '0.000001')
        self.fields['longitude'].widget.attrs.setdefault('step', '0.000001')

    class Meta:
        model = TravelExperience
        # Do NOT expose experience_type here (view enforces it)
        fields = [
            'title',
            'description',
            'category',
            'location',
            'latitude',
            'longitude',
            'country',
            'city',
            'image',
            'visited_on',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'visited_on': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat is None:
            return lat
        try:
            if not (Decimal('-90') <= lat <= Decimal('90')):
                raise ValidationError('Latitude must be between -90 and 90.')
        except TypeError:
            raise ValidationError('Invalid latitude.')
        return lat

    def clean_longitude(self):
        lng = self.cleaned_data.get('longitude')
        if lng is None:
            return lng
        try:
            if not (Decimal('-180') <= lng <= Decimal('180')):
                raise ValidationError('Longitude must be between -180 and 180.')
        except TypeError:
            raise ValidationError('Invalid longitude.')
        return lng

    def clean_image(self):
        """
        Optional: basic file validation. Adjust max size/types as needed.
        """
        image = self.cleaned_data.get('image')
        if not image:
            return image
        validate_image_file(image, max_size=5 * 1024 * 1024)
        return image

    def clean(self):
        cleaned = super().clean()
        location = (cleaned.get('location') or '').strip()
        lat = cleaned.get('latitude')
        lng = cleaned.get('longitude')

        # Require either a human-readable location OR both coordinates
        if not location and not (lat and lng):
            raise ValidationError(
                'Provide either a Location or both Latitude and Longitude.'
            )

        # If one coordinate is present, require the other
        if (lat and not lng) or (lng and not lat):
            self.add_error('latitude', 'Both latitude and longitude are required when using coordinates.')
            self.add_error('longitude', 'Both latitude and longitude are required when using coordinates.')

        return cleaned

# ===========================
# Experience Comment Form
# ===========================
class ExperienceCommentForm(forms.ModelForm):
    class Meta:
        model = ExperienceComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment...'}),
        }
        
        
from django import forms
from .models import ExperienceMedia

class ExperienceMediaForm(forms.ModelForm):
    class Meta:
        model = ExperienceMedia
        fields = ['media_type', 'file', 'caption']

ExperienceMediaFormSet = forms.modelformset_factory(
    ExperienceMedia,
    form=ExperienceMediaForm,
    extra=4,  # Show 4 empty forms by default
    max_num=10,  # Max 10 media files per experience
    can_delete=True,
)        