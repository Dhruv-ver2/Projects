from django.http import HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

class GlobalExceptionLoggerMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        print("Exception occurred:", exception)

        return render(
            request,
            "errors/500.html",
            {
                "request_id": request.request_id
            },
            status=500
        )