from django.shortcuts import render

# Create your views here.


def post_write(request):
    return render(request, 'channel/post_write.html')
