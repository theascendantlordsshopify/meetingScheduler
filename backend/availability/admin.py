from django.contrib import admin
from .models import (
    WeeklyAvailability, DateOverride, BufferTime, 
    TimeZoneSettings, CalendarIntegration, AvailabilityRule
)


@admin.register(WeeklyAvailability)
class WeeklyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_weekday_display', 'start_time', 'end_time', 'is_available')
    list_filter = ('weekday', 'is_available', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ['user', 'weekday', 'start_time']


@admin.register(DateOverride)
class DateOverrideAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'is_available', 'reason')
    list_filter = ('is_available', 'date', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'reason')
    ordering = ['user', 'date', 'start_time']


@admin.register(BufferTime)
class BufferTimeAdmin(admin.ModelAdmin):
    list_display = ('user', 'before_meeting', 'after_meeting', 'lunch_break_enabled', 'lunch_start_time', 'lunch_end_time')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(TimeZoneSettings)
class TimeZoneSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'timezone', 'auto_detect', 'created_at')
    list_filter = ('timezone', 'auto_detect', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(CalendarIntegration)
class CalendarIntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'calendar_name', 'is_primary', 'sync_status', 'last_sync_at')
    list_filter = ('provider', 'is_primary', 'sync_status', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'calendar_name')
    readonly_fields = ('access_token', 'refresh_token', 'last_sync_at')


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ('user', 'rule_type', 'is_active', 'created_at')
    list_filter = ('rule_type', 'is_active', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')