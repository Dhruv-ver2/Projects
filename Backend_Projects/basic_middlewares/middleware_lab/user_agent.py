class UserAgentMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.headers.get("User-Agent")

        if user_agent is None:
            request.is_chrome_detected = False

        elif "Chrome" in user_agent:
            request.is_chrome_detected = True

        else:
            request.is_chrome_detected = False

        response = self.get_response(request)

        return response