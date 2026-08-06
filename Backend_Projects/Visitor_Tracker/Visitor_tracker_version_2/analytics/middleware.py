from user_agents import parse
from .models import VisitorLog

class VisitorLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Ignore static assets, media, and internal API routes
        excluded_paths = ('/static/', '/media/', '/api/verify-browser/')
        if request.path.startswith(excluded_paths):
            return response

        # 1. IP Resolution
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR', '0.0.0.0')

        # 2. Parse User-Agent
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

        browser_name = f"{user_agent.browser.family} {user_agent.browser.version_string}".strip()
        os_name = f"{user_agent.os.family} {user_agent.os.version_string}".strip()

        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key if hasattr(request, 'session') else None

        # 3. Save silently to Database (No terminal print here)
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
            pass

        return response