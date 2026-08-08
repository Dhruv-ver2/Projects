import json
import urllib.request
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VisitorLog

def get_real_client_ip(request):
    """
    Extracts the true client IP address through reverse proxies, CDNs, and load balancers.
    """
    # 1. Cloudflare header (if active)
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_ip:
        return cf_ip.strip()

    # 2. Standard X-Forwarded-For header
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the left-most (first) IP in the chain
        ip = x_forwarded_for.split(',')[0].strip()
        return ip

    # 3. Direct Connection IP
    return request.META.get('REMOTE_ADDR', '0.0.0.0')

def get_geoip_data(ip):
    """
    Fetches Geolocation and VPN/Proxy/Tor threat intelligence for a given IP.
    """
    if ip in ('127.0.0.1', 'localhost', '0.0.0.0'):
        return {
            'country': 'Localhost',
            'region': 'Local Area',
            'city': 'Developer PC',
            'latitude': 0.0,
            'longitude': 0.0,
            'isp': 'Local Network',
            'is_vpn_proxy': False,
            'is_tor': False,
            'network_type': 'Residential/ISP'
        }

    try:
        # Requesting extended security fields from ip-api.com
        url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,lat,lon,isp,org,hosting,proxy"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('status') == 'success':
                is_hosting = data.get('hosting', False)
                is_proxy = data.get('proxy', False)
                
                # Datacenter / Hosting / Proxy detection
                is_vpn_or_proxy = is_hosting or is_proxy
                
                network_type = "Residential / Mobile ISP"
                if is_vpn_or_proxy:
                    network_type = "VPN / Datacenter Proxy"

                return {
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': data.get('lat', 0.0),
                    'longitude': data.get('lon', 0.0),
                    'isp': data.get('isp', 'Unknown ISP'),
                    'is_vpn_proxy': is_vpn_or_proxy,
                    'is_tor': False,  # Can be expanded with Tor exit lists
                    'network_type': network_type
                }
    except Exception as e:
        print(f"⚠️ Security Lookup Error: {e}")

    return {
        'country': 'Unknown', 'region': 'Unknown', 'city': 'Unknown',
        'latitude': 0.0, 'longitude': 0.0, 'isp': 'Unknown',
        'is_vpn_proxy': False, 'is_tor': False, 'network_type': 'Unknown'
    }

@csrf_exempt
def update_browser_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            verified_browser = data.get('browser')
            verified_os = data.get('os')
            verified_device = data.get('device')

            # Extract True Client IP
            ip = get_real_client_ip(request)

            latest_log = VisitorLog.objects.filter(ip_address=ip).exclude(path='/favicon.ico').order_by('-timestamp').first()

            if latest_log:
                geo_data = get_geoip_data(ip)

                if verified_browser:
                    latest_log.browser = verified_browser
                if verified_os:
                    latest_log.operating_system = verified_os
                if verified_device:
                    latest_log.device_type = verified_device

                # Save Geolocation & Security telemetry
                latest_log.country = geo_data['country']
                latest_log.region = geo_data['region']
                latest_log.city = geo_data['city']
                latest_log.latitude = geo_data['latitude']
                latest_log.longitude = geo_data['longitude']
                latest_log.isp = geo_data['isp']
                latest_log.is_vpn_proxy = geo_data['is_vpn_proxy']
                latest_log.is_tor = geo_data['is_tor']
                latest_log.network_type = geo_data['network_type']
                latest_log.save()

                # ENRICHED TERMINAL LOG WITH SECURITY FLAGS 🚨
                visitor_name = latest_log.user.username if latest_log.user else "Anonymous"
                security_badge = "🛡️ NORMAL TRAFFIC"
                if latest_log.is_vpn_proxy:
                    security_badge = "⚠️ VPN / PROXY DETECTED"
                elif latest_log.is_tor:
                    security_badge = "🚨 TOR EXIT NODE DETECTED"

                print("\n" + "="*60)
                print(f"📥 NEW VISITOR LOG DETECTED [{security_badge}]")
                print(f"   • IP Address   : {ip}")
                print(f"   • Visitor      : {visitor_name}")
                print(f"   • Network / ISP: {latest_log.isp} ({latest_log.network_type})")
                print(f"   • Device       : {latest_log.device_type}")
                print(f"   • OS / Browser : {latest_log.operating_system} | {latest_log.browser}")
                print(f"   • Location     : {latest_log.city}, {latest_log.region}, {latest_log.country}")
                print(f"   • GPS Coords   : [{latest_log.latitude}, {latest_log.longitude}]")
                print(f"   • Path Hit     : [{latest_log.method}] {latest_log.path}")
                print("="*60 + "\n")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"\n❌ EXCEPTION IN VISITOR VERIFICATION: {e}\n")  # <-- ADD THIS PRINT LINE
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)