from django.http import HttpResponseServerError

class GlobalExceptionLoggerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)

        except Exception as e:
            print("Exception occurred:", e)

            response = HttpResponseServerError("Something went wrong on the server.")
        
        return response