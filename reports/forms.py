from django import forms
from .models import Report, ReportAttachment, Department

# --- 1. Citizen Report Submission Form ---

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'issue_type',
            'other_issue',  # <-- Add this
            'description',
            'location',
            'latitude',
            'longitude',
            'image',
        ]
        widgets = {
            'issue_type': forms.Select(attrs={'class': 'form-select'}),
            'other_issue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Please specify the issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issue in detail...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., Near Law Garden, Ellis Bridge, Ahmedabad'
            }),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'issue_type': 'Type of Issue',
            'other_issue': 'If Other, please specify',
            'description': 'Description',
            'location': 'Location (Ahmedabad only)',
            'latitude': 'Latitude (optional)',
            'longitude': 'Longitude (optional)',
            'image': 'Photo (optional)',
        }

    def clean_location(self):
        location = self.cleaned_data.get('location', '')
        # Allow blank location if coordinates are provided; otherwise enforce Ahmedabad
        lat = self.data.get('latitude') or self.cleaned_data.get('latitude')
        lng = self.data.get('longitude') or self.cleaned_data.get('longitude')
        if location:
            if "ahmedabad" not in location.lower():
                raise forms.ValidationError("Reports can only be submitted for Ahmedabad.")
        else:
            # If no location text, coordinates may be used instead
            if not (lat and lng):
                # Leave overall error handling to clean(); return empty here
                return location
        return location

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large (max 5MB).")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Only image files are allowed.")
        return image

    def clean(self):
        cleaned_data = super().clean()
        issue_type = cleaned_data.get('issue_type')
        other_issue = cleaned_data.get('other_issue')
        location = cleaned_data.get('location') or ''
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')

        # Enforce either location (Ahmedabad) OR both coordinates
        if not location and not (lat and lng):
            raise forms.ValidationError(
                "Provide either a Location in Ahmedabad or both Latitude and Longitude."
            )

        # If only one coordinate provided, require the other
        if (lat and not lng) or (lng and not lat):
            self.add_error('latitude', "Both latitude and longitude are required when using coordinates.")
            self.add_error('longitude', "Both latitude and longitude are required when using coordinates.")

        if issue_type == 'other' and not other_issue:
            self.add_error('other_issue', "Please specify the issue if you selected 'Other'.")
        return cleaned_data

# --- 2. Authority/Staff Status Update Form ---

class ReportStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['status', 'department', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'status': 'Update Status',
            'department': 'Assign Department',
            'assigned_to': 'Assign Authority',
        }

# --- 3. Attachment Upload Form (for additional uploads) ---

class ReportAttachmentForm(forms.ModelForm):
    class Meta:
        model = ReportAttachment
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'file': 'Upload File',
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            if f.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File too large (max 10MB).")
            if not (f.content_type.startswith('image/') or f.content_type == 'application/pdf'):
                raise forms.ValidationError("Only images or PDFs are allowed.")
        return f

# --- 4. Citizen Feedback Form (after resolution) ---

class ReportFeedbackForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['feedback', 'rating']
        widgets = {
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your feedback about the resolution...'
            }),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }
        labels = {
            'feedback': 'Feedback',
            'rating': 'Rating (1-5)',
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating