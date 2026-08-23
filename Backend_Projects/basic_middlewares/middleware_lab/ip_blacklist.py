from django.http import HttpResponseForbidden

class IPBlacklistMiddleware:

    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request):
        BLACKLIST = {
                        "127.0.0.2",
                    }
        
        ip = request.META.get("REMOTE_ADDR")

        if ip in BLACKLIST:
            return HttpResponseForbidden(f"Access denied !\nFor IP: {ip}")

        
        response = self.get_response(request)

        return response