from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from apps.channel.models import Channel, ChannelPost, ChannelContent

# Create your views here.


@login_required(login_url='/session/login')
def main(request):
    channel_list = Channel.objects.all()
    ctx = {'channel_list': channel_list}

    return render(request, 'channel/main.html', ctx)


@login_required(login_url='/session/login')
def register_channel(request):

    if request.method == 'POST':
        user_profile = request.user.userprofile
        name = request.POST.get('name', '')
        channel_url = request.POST.get('channel_url', '')
        description = request.POST.get('description', '')

        # Handle when name or channel_url is empty
        if name == '' or channel_url == '':
            return redirect('./')

        channel = Channel()
        channel.name = name
        channel.channel_url = channel_url
        channel.description = description
        channel.author = user_profile
        channel.save()
        return redirect('../' + channel_url)

    return render(request, 'channel/register_channel.html')


@login_required(login_url='/session/login')
def view_channel(request, channel_url):
    channel = Channel.objects.get(channel_url=str(channel_url))
    post_list = ChannelPost.objects.filter(channel=channel)
    ctx = {'post_list': post_list}

    return render(request, 'channel/view_channel.html', ctx)


@login_required(login_url='/session/login')
def write_post(request, channel_url, edit_flag=False, channel_post=None):

    channel = Channel.objects.get(channel_url=str(channel_url))

    if request.user.userprofile != channel.author:
        raise PermissionDenied

    if request.method == 'POST':
        title = request.POST.get('post-title', '')
        content = request.POST.get('post-content-textarea', '')

        # Handle when title or content is empty
        if title == '' or content == '':
            return redirect('./')

        if edit_flag is False:
            channel_content = ChannelContent(content=content)
            channel_content.save()
            channel_post = ChannelPost()
            channel_post.channel = channel
            channel_post.title = title
            channel_post.channel_content = channel_content
            channel_post.save()
        else:
            channel_content = channel_post.channel_content
            channel_content.content = content
            channel_content.save()
        return redirect('/channel/' + channel_url + '/' + str(channel_post.id))

    ctx = {'edit_flag': edit_flag, 'channel_post': channel_post}
    return render(request, 'channel/write_post.html', ctx)


@login_required(login_url='/session/login')
def read_post(request, channel_url, channel_post_id):
    channel = Channel.objects.get(channel_url=str(channel_url))
    channel_post = ChannelPost.objects.get(id=channel_post_id)
    channel_content = channel_post.channel_content
    if channel_content.is_deleted:
        return redirect("/channel/" + channel_url)
    content = channel_content.content
    ctx = {'channel': channel,
           'channel_post': channel_post, 'content': content}
    return render(request, 'channel/read_post.html', ctx)


@login_required(login_url='/session/login')
def edit_post(request, channel_url, channel_post_id):
    channel_post = ChannelPost.objects.get(id=channel_post_id)

    return write_post(request, channel_url,
                      edit_flag=True, channel_post=channel_post)


@login_required(login_url='/session/login')
def delete_post(request, channel_url, channel_post_id):
    channel_post = ChannelPost.objects.get(id=channel_post_id)
    channel_content = channel_post.channel_content
    channel_content.is_deleted = True
    channel_content.save()

    return redirect('/channel/' + channel_url)
