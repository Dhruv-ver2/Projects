from user_agents import parse
from .models import VisitorLog

class VisitorLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip static and media files to keep terminal output clean
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return response

        # 1. Extract IP Address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

        # 2. Extract & Parse User-Agent
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)

        if user_agent.is_bot:
            device_type = "Bot/Crawler"
        elif user_agent.is_mobile:
            device_type = "Mobile"
        elif user_agent.is_tablet:
            device_type = "Tablet"
        elif user_agent.is_pc:
            device_type = "Desktop"
        else:
            device_type = "Unknown"

        # 3. Parse browser & OS versions cleanly
        browser_name = f"{user_agent.browser.family} {user_agent.browser.version_string}".strip()
        os_name = f"{user_agent.os.family} {user_agent.os.version_string}".strip()

        # Fix for Windows 11 User-Agent Reduction
        if user_agent.os.family == "Windows":
            platform_version = request.META.get('HTTP_SEC_CH_UA_PLATFORM_VERSION', '').replace('"', '')
            if platform_version:
                try:
                    # Windows 11 is platform version 13.0.0+
                    major_version = int(platform_version.split('.')[0])
                    if major_version >= 13:
                        os_name = "Windows 11"
                    else:
                        os_name = "Windows 10"
                except ValueError:
                    pass

        # 4. Identity
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key if hasattr(request, 'session') else None

        # 5. Terminal Print Output 🚀
        visitor_name = user.username if user else "Anonymous"
        print("\n" + "="*50)
        print(f"📥 NEW VISITOR LOG DETECTED")
        print(f"   • IP Address : {ip}")
        print(f"   • Visitor    : {visitor_name}")
        print(f"   • Device     : {device_type}")
        print(f"   • OS / Browser: {os_name} | {browser_name}")
        print(f"   • Path Hit   : [{request.method}] {request.path}")
        print("="*50 + "\n")

        # 6. Save to Database
        try:
            VisitorLog.objects.create(
                user=user,
                session_key=session_key,
                ip_address=ip,
                path=request.path[:500],
                method=request.method,
                referer=request.META.get('HTTP_REFERER', '')[:500] or None,
                raw_user_agent=user_agent_string,
                browser=browser_name or "Unknown",
                operating_system=os_name or "Unknown",
                device_type=device_type,
            )
        except Exception as e:
            print(f"⚠️ Failed to log to database: {e}")

        return response