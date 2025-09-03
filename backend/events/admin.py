from django.contrib import admin
from .models import EventType, EventTypeAvailability, BookingPage


class EventTypeAvailabilityInline(admin.TabularInline):
    model = EventTypeAvailability
    extra = 0


class BookingPageInline(admin.StackedInline):
    model = BookingPage
    extra = 0


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'duration', 'location_type', 'is_active', 'created_at')
    list_filter = ('duration', 'location_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [EventTypeAvailabilityInline, BookingPageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'duration', 'is_active')
        }),
        ('Location', {
            'fields': ('location_type', 'location_details')
        }),
        ('Scheduling Settings', {
            'fields': ('buffer_time_before', 'buffer_time_after', 'max_bookings_per_day', 'min_notice_time', 'max_advance_time')
        }),
        ('Customization', {
            'fields': ('color', 'image', 'custom_questions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EventTypeAvailability)
class EventTypeAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'get_weekday_display', 'start_time', 'end_time', 'is_available')
    list_filter = ('weekday', 'is_available', 'created_at')
    search_fields = ('event_type__name', 'event_type__user__email')


@admin.register(BookingPage)
class BookingPageAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'page_title', 'show_event_details', 'require_confirmation', 'created_at')
    list_filter = ('show_event_details', 'show_organizer_info', 'require_confirmation', 'created_at')
    search_fields = ('event_type__name', 'page_title', 'event_type__user__email')