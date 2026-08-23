import time

class PerformanceTimerMiddleware:

    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request):
        start = time.time()

        response = self.get_response(request)

        end = time.time()

        duration = end - start

        print(f"Request Took: {duration:.4f} seconds")

        return response

    