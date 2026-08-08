from django.contrib import admin
from .models import VisitorLog

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    # Columns displayed in the list view
    list_display = (
        'timestamp',
        'get_visitor_identity',
        'ip_address',
        'device_type',
        'browser',
        'operating_system',
        'path',
        'method',
    )

    # Sidebar filters for quick analysis
    list_filter = (
        'device_type',
        'method',
        'browser',
        'operating_system',
        'timestamp',
    )

    # Search bar across multiple fields
    search_fields = (
        'ip_address',
        'path',
        'user__email',
        'user__username',
        'raw_user_agent',
        'session_key',
    )

    # Read-only details view to prevent accidental manual log tampering
    readonly_fields = (
        'timestamp',
        'user',
        'session_key',
        'ip_address',
        'path',
        'method',
        'referer',
        'raw_user_agent',
        'browser',
        'operating_system',
        'device_type',
    )

    # Set default sorting (newest logs first)
    ordering = ('-timestamp',)

    # Display clean visitor identity (Username/Email if logged in, otherwise Anonymous)
    def get_visitor_identity(self, obj):
        if obj.user:
            return f"👤 {obj.user.get_full_name() or obj.user.username}"
        return "🕵️ Anonymous"
    get_visitor_identity.short_description = 'Visitor'