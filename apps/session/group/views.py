from django.shortcuts import render, redirect
from apps.session.models import UserProfile, Group, GroupMessage
from django.contrib.auth.decorators import login_required


@login_required(login_url='/session/login/')
def make_group(request):
    if request.method != "POST":
        return render(request, 'session/make_group.html')
    group_name = request.POST['groupname']
    try:
        Group.objects.get(name=group_name)
        return render(request, 'session/make_group.html',
                      {'error':
                          'The name is already being used by other group'})
    except Group.DoesNotExist:
        new_group = Group.objects.create(name=group_name)
    new_group.add_member(request.user.userprofile)
    return redirect('/session/group/message/'+new_group.name+'/manage')


# main view of session/group
@login_required(login_url='/session/login/')
def view_group_list(request):
    mygroups = request.user.userprofile.groups.all()
    if request.method != "POST":
        mygroups = request.user.userprofile.groups.all()
        return render(request, 'session/grouplist.html', {'groups': mygroups})
    return redirect('/session/group/message/'+request.POST['groupname']+'/')


@login_required(login_url='/session/login/')
def group_message(request, groupname):
    try:
        group = Group.objects.get(name=groupname)
    except Group.DoesNotExist:
        return render(request, 'session/group_message.html',
                      {'group': None, 'error': 'The group does not exist'})
    if not (request.user.userprofile in group.members.all()):
        return render(request, 'session/group_message.html',
                      {'group': None,
                       'error': 'You are not a member of this group'})
    messages = GroupMessage.objects.filter(receivers=group)
    messages = messages.order_by('created_time')
    if request.method != "POST":
        return render(request, 'session/group_message.html',
                      {'group': group, 'messages': messages})
    GroupMessage.objects.create(content=request.POST['content'],
                                sender=request.user.userprofile,
                                receivers=group)
    return redirect('/session/group/message/'+group.name+'/')


@login_required(login_url='/session/login/')
def manage(request, groupname):
    try:
        group = Group.objects.get(name=groupname)
    except Group.DoesNotExist:
        return render(request, 'session/group_manage.html',
                      {'group': None, 'error': 'The group does not exist'})
    if not (request.user.userprofile in group.members.all()):
        return render(request, 'session/group_manage.html',
                      {'group': None,
                       'error': 'You are not a member of this group'})
    members = group.members.all()
    if request.method == "GET":
        return render(request, 'session/group_manage.html',
                      {'group': group, 'members': members})

    # DELETE request(remove self)
    if request.method == "DELETE":
        group.remove_member(request.user.userprofile)
        return redirect('/session/group/')

    # POST request(add member)
    try:
        invitee = UserProfile.objects.get(nickname=request.POST['nickname'])
    except UserProfile.DoesNotExist:
        return render(request, 'session/group_manage.html',
                      {'group': group,
                       'members': members,
                       'error': 'The user does not exist'})
    if invitee in members:
        return render(request, 'session/group_manage.html',
                      {'group': group,
                       'members': members,
                       'error': 'The user is already in this group'})
    group.add_member(invitee)
    return redirect('/session/group/message/'+group.name+'/manage/')
