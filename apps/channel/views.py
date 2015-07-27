from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# from django.contrib.auth import authenticate
from apps.channel.backend import _make_channel
# Create your views here.


def post_write(request):
    return render(request, 'channel/post_write.html')


@login_required(login_url='/session/login')
def register_channel(request):
    if request.method == 'POST':
        channel_id = _make_channel(request)
        if channel_id:
            return redirect('../' + str(channel_id))
        else:
            return redirect('../')
    return render(request, 'channel/register_channel.html')
