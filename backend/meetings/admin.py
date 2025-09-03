from django.contrib import admin
from .models import Meeting, MeetingNote, MeetingAttachment, MeetingRescheduleRequest


class MeetingNoteInline(admin.TabularInline):
    model = MeetingNote
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class MeetingAttachmentInline(admin.TabularInline):
    model = MeetingAttachment
    extra = 0
    readonly_fields = ('filename', 'file_size', 'content_type', 'created_at')


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'invitee_name', 'start_time', 'status', 'created_at')
    list_filter = ('status', 'event_type', 'location_type', 'created_at', 'start_time')
    search_fields = ('title', 'invitee_name', 'invitee_email', 'organizer__email')
    readonly_fields = ('confirmation_token', 'created_at', 'updated_at', 'cancelled_at')
    inlines = [MeetingNoteInline, MeetingAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_type', 'organizer', 'title', 'description', 'status')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time', 'timezone')
        }),
        ('Location', {
            'fields': ('location_type', 'location_details', 'meeting_url', 'meeting_id', 'meeting_password')
        }),
        ('Invitee Information', {
            'fields': ('invitee_name', 'invitee_email', 'invitee_phone', 'invitee_timezone')
        }),
        ('Custom Responses', {
            'fields': ('custom_responses',),
            'classes': ('collapse',)
        }),
        ('Status & Tracking', {
            'fields': ('confirmation_token', 'cancellation_reason', 'reminder_sent', 'confirmation_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MeetingNote)
class MeetingNoteAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'author', 'is_private', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('meeting__title', 'author__email', 'content')


@admin.register(MeetingAttachment)
class MeetingAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'meeting', 'uploaded_by', 'file_size', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('filename', 'meeting__title', 'uploaded_by__email')


@admin.register(MeetingRescheduleRequest)
class MeetingRescheduleRequestAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'requested_by', 'new_start_time', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('meeting__title', 'requested_by__email', 'reason')