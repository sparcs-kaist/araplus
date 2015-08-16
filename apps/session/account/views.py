from django.shortcuts import render, redirect
from apps.session.models import UserProfile
from django.contrib.auth.decorators import login_required

@login_required(login_url='/session/login/')
def account_info(request):
    account = request.user.userprofile
    account_info = {}
    account_info['nickname'] = account.nickname
    account_info['points'] = account.points
    account_info['gender'] = account.gender
    account_info['birthday'] = account.birthday
    account_info['signiture'] = account.signiture
    return render(request,'session/account_info.html',
            {'account':account_info})

@login_required(login_url='/session/login/')
def account_modify(request):
    account = request.user.userprofile
    if request.method == 'POST':
        account.nickname = request.POST.get('nickname','')
        account.signiture = request.POST.get('signiture','')
        account.save()
        return redirect ('../')
    else:
        account_info = {}
        account_info['nickname'] = account.nickname
        account_info['signiture'] = account.signiture
        return render (request,'session/account_modify.html',
                {'account':account_info})
 
