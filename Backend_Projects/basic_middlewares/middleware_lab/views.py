import time
from django. http import HttpResponse

def home(request):
    result = 10 / 0

    return HttpResponse("This will never be reached")