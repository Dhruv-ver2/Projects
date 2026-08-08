from django.db import models
from django.conf import settings

class VisitorLog(models.Model):
    # Identity & Session
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_logs"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # Network & True IP
    ip_address = models.GenericIPAddressField()
    is_vpn_proxy = models.BooleanField(default=False)
    is_tor = models.BooleanField(default=False)
    network_type = models.CharField(max_length=100, null=True, blank=True)  # e.g., "ISP", "Datacenter/VPN", "Tor Exit Node"
    isp = models.CharField(max_length=150, null=True, blank=True)

    # Geolocation Telemetry
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Route Details
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    referer = models.URLField(max_length=500, null=True, blank=True)

    # System & Device Details
    raw_user_agent = models.TextField()
    browser = models.CharField(max_length=100, null=True, blank=True)
    operating_system = models.CharField(max_length=100, null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)

    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Visitor Log"
        verbose_name_plural = "Visitor Logs"

    def __str__(self):
        visitor = self.user.email if self.user else f"Anonymous ({self.ip_address})"
        location = f" - {self.city}, {self.country}" if self.city and self.country else ""
        vpn_tag = " [VPN/Proxy]" if self.is_vpn_proxy else ""
        return f"{visitor}{location}{vpn_tag} - {self.path} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"