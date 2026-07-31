import json
import urllib.request
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VisitorLog

def home_view(request):
    return render(request, 'index.html')

def get_geoip_data(ip):
    """
    Fetches Country, Region, City, and GPS Coordinates for a given public IP address.
    """
    # Skip lookup for local development IPs
    if ip in ('127.0.0.1', 'localhost', '0.0.0.0'):
        return {
            'country': 'Localhost',
            'region': 'Local Area',
            'city': 'Developer PC',
            'latitude': 0.0,
            'longitude': 0.0
        }

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,lat,lon"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': data.get('lat', 0.0),
                    'longitude': data.get('lon', 0.0)
                }
    except Exception as e:
        print(f"⚠️ GeoIP Lookup Error: {e}")

    return {'country': 'Unknown', 'region': 'Unknown', 'city': 'Unknown', 'latitude': 0.0, 'longitude': 0.0}

@csrf_exempt
def update_browser_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            verified_browser = data.get('browser')
            verified_os = data.get('os')
            verified_device = data.get('device')

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR', '')

            # Ignore favicon.ico calls
            latest_log = VisitorLog.objects.filter(ip_address=ip).exclude(path='/favicon.ico').order_by('-timestamp').first()

            if latest_log:
                # 1. Fetch Geolocation Data
                geo_data = get_geoip_data(ip)

                # 2. Update Database Record
                if verified_browser:
                    latest_log.browser = verified_browser
                if verified_os:
                    latest_log.operating_system = verified_os
                if verified_device:
                    latest_log.device_type = verified_device

                latest_log.country = geo_data['country']
                latest_log.region = geo_data['region']
                latest_log.city = geo_data['city']
                latest_log.latitude = geo_data['latitude']
                latest_log.longitude = geo_data['longitude']
                latest_log.save()

                # 3. UNIFIED ENRICHED TERMINAL LOG 🚀
                visitor_name = latest_log.user.username if latest_log.user else "Anonymous"
                print("\n" + "="*55)
                print(f"📥 NEW VISITOR LOG DETECTED")
                print(f"   • IP Address   : {ip}")
                print(f"   • Visitor      : {visitor_name}")
                print(f"   • Device       : {latest_log.device_type}")
                print(f"   • OS / Browser : {latest_log.operating_system} | {latest_log.browser}")
                print(f"   • Location     : {latest_log.city}, {latest_log.region}, {latest_log.country}")
                print(f"   • GPS Coords   : [{latest_log.latitude}, {latest_log.longitude}]")
                print(f"   • Path Hit     : [{latest_log.method}] {latest_log.path}")
                print("="*55 + "\n")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)