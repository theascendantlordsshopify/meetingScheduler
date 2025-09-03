from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactTag(models.Model):
    """Tags for organizing contacts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#1D9CA4', help_text="Hex color code")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.full_name})"


class Contact(models.Model):
    """Contact management for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    
    # Basic information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Organization details
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Additional information
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Categorization
    tags = models.ManyToManyField(ContactTag, blank=True, related_name='contacts')
    
    # Preferences
    preferred_contact_method = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('linkedin', 'LinkedIn'),
    ], default='email')
    
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'email']
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in address_parts if part])


class ContactGroup(models.Model):
    """Groups for organizing contacts"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_groups')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#1D9CA4', help_text="Hex color code")
    
    contacts = models.ManyToManyField(Contact, blank=True, related_name='groups')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.full_name})"

    @property
    def contact_count(self):
        return self.contacts.count()


class ContactInteraction(models.Model):
    """Track interactions with contacts"""
    
    INTERACTION_TYPES = [
        ('meeting', 'Meeting'),
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('message', 'Message'),
        ('note', 'Note'),
        ('other', 'Other'),
    ]
    
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_interactions')
    
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    subject = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Meeting reference (if applicable)
    meeting = models.ForeignKey('meetings.Meeting', on_delete=models.SET_NULL, blank=True, null=True)
    
    interaction_date = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-interaction_date']

    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.contact.full_name}"


class ContactCustomField(models.Model):
    """Custom fields for contacts"""
    
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('date', 'Date'),
        ('boolean', 'Yes/No'),
        ('select', 'Select'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_custom_fields')
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    
    # For select fields
    options = models.JSONField(default=list, blank=True, help_text="Options for select fields")
    
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"


class ContactCustomFieldValue(models.Model):
    """Values for custom fields"""
    
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='custom_field_values')
    custom_field = models.ForeignKey(ContactCustomField, on_delete=models.CASCADE)
    value = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['contact', 'custom_field']

    def __str__(self):
        return f"{self.custom_field.name}: {self.value}"