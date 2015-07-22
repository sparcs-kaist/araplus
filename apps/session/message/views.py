from django.shortcuts import render, redirect
from apps.session.models import UserProfile, Message, Block
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required(login_url='/session/login/')
def send_message(request):
    if request.method != "POST":
        return render(request, 'session/write_message.html')
    sender = request.user.userprofile
    content = request.POST['content']
    try:
        receiver = UserProfile.objects.get(nickname=request.POST['nickname'])
    except UserProfile.DoesNotExist:
        return render(request, 'session/write_message.html',
                      {'error': "The user doesn't exist"})
    Message.objects.create(content=content,
                           sender=sender,
                           receiver=receiver,
                           is_read=False)
    success = "Successfully sent message"
    return render(request, 'session/write_message.html', {'success': success})


@login_required(login_url='/session/login/')
def check_message(request):
    receiver = request.user.userprofile
    blocks = Block.objects.filter(receiver=receiver)
    messages = Message.objects.filter(receiver=receiver)
    for block in blocks:
        messages = messages.exclude(sender=block.sender)
    for message in messages:
        message.read()
    return render(request,
                  'session/check_message.html', {'messages': messages})


@login_required(login_url='/session/login/')
def check_thread(request, nickname):
    receiver = request.user.userprofile
    sender = UserProfile.objects.get(nickname=nickname)
    messages = Message.objects.filter(Q(sender=sender, receiver=receiver) |
                                      Q(receiver=sender, sender=receiver))
    messages = messages.order_by('created_time')
    for message in messages:
        message.read()
    return render(request,
                  'session/message_thread.html', {'sender': sender,
                                                  'receiver': receiver,
                                                  'messages': messages})


@login_required(login_url='/session/login/')
def check_sent_message(request):
    messages = Message.objects.filter(sender=request.user.userprofile)
    return render(request,
                  'session/check_sent_message.html', {'messages': messages})


@login_required(login_url='/session/login')
def block(request):
    if request.method != "POST":
        return render(request, 'session/block.html')
    receiver = request.user.userprofile
    try:
        sender = UserProfile.objects.get(nickname=request.POST['nickname'])
    except UserProfile.DoesNotExist:
        return render(request, 'session/block.html',
                      {'error': "The user doesn't exist"})
    if sender == receiver:
        return render(request, 'session/block.html',
                      {'error': "You can't block yourself"})
    if len(Block.objects.filter(sender=sender, receiver=receiver)) != 0:
        return render(request, 'session/block.html',
                      {'error': "You already blocked the user"})
    Block.objects.create(sender=sender, receiver=receiver)
    success = "block successful"
    return render(request, 'session/block.html', {'success': success})


@login_required(login_url='/session/login')
def show_block_list(request):
    if request.method != "POST":
        blocks = Block.objects.filter(receiver=request.user.userprofile)
        return render(request, 'session/block_list.html', {'blocks': blocks})

    # The rest is unblock
    try:
        blocked_UP = UserProfile.objects.get(nickname=request.POST['nickname'])
    except UserProfile.DoesNotExist:
        return render(request, 'session/block_list.html',
                      {'error': "There are no user with the given nickname"})
    block = Block.objects.get(sender=blocked_UP,
                              receiver=request.user.userprofile)
    block.delete()
    return redirect('/session/message/blocklist')
