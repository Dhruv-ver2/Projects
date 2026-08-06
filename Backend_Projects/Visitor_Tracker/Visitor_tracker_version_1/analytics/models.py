from django.db import models
from django.conf import settings

class VisitorLog(models.Model):
    # Identity & Session (Nullable so anonymous traffic is logged too)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_logs"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # Network
    ip_address = models.GenericIPAddressField()

    # Route Details
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)  # GET, POST, etc.
    referer = models.URLField(max_length=500, null=True, blank=True)

    # System & Device Details (Parsed from User-Agent)
    raw_user_agent = models.TextField()
    browser = models.CharField(max_length=100, null=True, blank=True)
    operating_system = models.CharField(max_length=100, null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)  # Mobile, Tablet, Desktop, Bot

    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Visitor Log"
        verbose_name_plural = "Visitor Logs"

    def __str__(self):
        visitor = self.user.email if self.user else f"Anonymous ({self.ip_address})"
        return f"{visitor} - {self.path} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"