from django.contrib import admin
from .models import Contact, ContactTag, ContactGroup, ContactInteraction, ContactCustomField, ContactCustomFieldValue


class ContactCustomFieldValueInline(admin.TabularInline):
    model = ContactCustomFieldValue
    extra = 0


class ContactInteractionInline(admin.TabularInline):
    model = ContactInteraction
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'company', 'job_title', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'company', 'preferred_contact_method', 'created_at', 'tags')
    search_fields = ('first_name', 'last_name', 'email', 'company', 'job_title')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    inlines = [ContactCustomFieldValueInline, ContactInteractionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Organization', {
            'fields': ('company', 'job_title', 'department')
        }),
        ('Online Presence', {
            'fields': ('website', 'linkedin_url')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('preferred_contact_method', 'timezone', 'language', 'tags')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active', 'last_contacted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactTag)
class ContactTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'user__email')


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'contact_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'user__email')
    filter_horizontal = ('contacts',)


@admin.register(ContactInteraction)
class ContactInteractionAdmin(admin.ModelAdmin):
    list_display = ('contact', 'interaction_type', 'subject', 'interaction_date', 'user')
    list_filter = ('interaction_type', 'interaction_date', 'created_at')
    search_fields = ('contact__first_name', 'contact__last_name', 'subject', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ContactCustomField)
class ContactCustomFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_type', 'user', 'is_required', 'is_active', 'created_at')
    list_filter = ('field_type', 'is_required', 'is_active', 'created_at')
    search_fields = ('name', 'user__email')


@admin.register(ContactCustomFieldValue)
class ContactCustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ('contact', 'custom_field', 'value', 'created_at')
    list_filter = ('custom_field', 'created_at')
    search_fields = ('contact__first_name', 'contact__last_name', 'custom_field__name', 'value')