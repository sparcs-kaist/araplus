from django.shortcuts import render, redirect
from apps.session.models import UserProfile, Group
from django.contrib.auth.decorators import login_required


@login_required(login_url='/session/login/')
def make_group(request):
    if request.method != "POST":
        return render(request, 'session/make_group.html')
    group_name = request.POST['groupname']
    new_group = Group.objects.create(name=group_name)
    new_group.add_member(request.user.userprofile)
    return redirect('/session/group/')


# main view of session/group
@login_required(login_url='/session/login/')
def view_group_list(request):
    mygroups = request.user.userprofile.groups.all()
    return render(request, 'session/grouplist.html', {'groups': mygroups})
