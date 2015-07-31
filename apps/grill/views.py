# -*- coding: utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import GrillComment, Grill, GrillCommentVote
from apps.session.models import UserProfile
from .forms import GrillAddForm, CommentAddForm
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
import json
import datetime


@login_required(login_url='/session/login/')
def home(request):
    grills = Grill.objects.all().order_by('created_time')  # 나중에 업데이트 순서로 바꾸기?
    return render(request, 'grill/main.html',
                  {
                      'grills': grills,
                  })


@login_required(login_url='/session/login/')
def view_grill(request, grill_id):
    grill = get_object_or_404(Grill, pk=grill_id)
    edit_form = CommentAddForm()
    comments = GrillComment.objects.filter(
        grill=grill_id
    ).order_by('created_time').reverse()
    profile = get_object_or_404(UserProfile, user=request.user)
    user_vote = GrillCommentVote.objects.filter(userprofile=profile)
    for comment in comments:
        # WARNING! 사용자가 HTML 코드를 작성하면 그대로 반영
        comment.content = comment.replace_tags()
        comment.like = GrillCommentVote.objects.filter(
            grill_comment=comment,
            is_up=True
        ).count()
        comment.hate = GrillCommentVote.objects.filter(
            grill_comment=comment,
            is_up=False
        ).count()

        if user_vote.filter(grill_comment=comment):
            comment.vote_disable = True

    return render(request,
                  'grill/view.html',
                  {
                      'form': edit_form,
                      'grill_id': grill_id,
                      'comments': comments,
                      'grill': grill,
                  })


@login_required(login_url='/session/login/')
def add_grill(request):
    if request.method == "GET":
        edit_form = GrillAddForm()
    elif request.method == "POST":
        edit_form = GrillAddForm(request.POST)
        if edit_form.is_valid():
            userprofile = UserProfile.objects.get(user=request.user)
            new_grill = Grill(title=edit_form.cleaned_data['title'],
                              author=userprofile,
                              content=edit_form.cleaned_data['content'])
            new_grill.save()
            return redirect(new_grill.get_absolute_url())

    return render(request,
                  'grill/add_grill.html',
                  {
                      'form': edit_form,
                  })


def add_comment(request, grill_id):
    post_data = request.POST
    grill = get_object_or_404(Grill, pk=grill_id)
    userprofile = UserProfile.objects.get(user=request.user)
    if len(post_data.get('new_content')) > 140:
        raise SuspiciousOperation('Too long content')
    new_comment = GrillComment(
        grill=grill, author=userprofile, content=post_data.get('new_content'))
    new_comment.save()
    new_comment.grill.updated_time = datetime.datetime.now()
    new_comment.grill.save()

    ms = '<li id="comment-' + str(new_comment.order) +\
         '" class="list-group-item">'
    ms += '<div>'
    ms += '<div class="comment-meta">'
    ms += '<span class="col-md-1">' + str(new_comment.order) + '</span>'
    ms += '<strong>' + new_comment.author.nickname.encode('utf-8')
    ms += '</strong>'
    ms += '<span class="pull-right">' + str(new_comment.created_time)
    ms += '</span></div>'
    ms += '<div class="comment-content-container">'
    ms += '<span>' + new_comment.replace_tags().encode('utf8') + '</span>'
    ms += '<div class="comment-vote-container">'
    ms += '<button class="vote-up btn btn-default"> 추천 (+0) </button>'
    ms += '<button class="vote-down btn btn-default"> 반대 (-0)</button>'
    ms += '</div></div></div></li>'
    data = {'html': ms}
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder),
                        content_type="application/json")


def refresh_comment(request, grill_id):
    grill = get_object_or_404(Grill, pk=grill_id)
    # Update Comments
    new_index = request.POST['required_index']
    if not new_index:
        new_index = 1
    comments = GrillComment.objects.filter(
        grill=grill, order__gte=new_index)
    json_comments = map(lambda x: x.to_json(), list(comments))
    data = {'comments': json_comments}

    # Update Votes
    last_update = request.POST['last_update']
    votes = GrillCommentVote.objects.filter(
        grill_comment__grill=grill,
        created_time__gte=last_update
    ).values('grill_comment')
    last_update = datetime.datetime.now()
    votes = votes.annotate(new_count=Count('is_up'))
    # XXX: 어떻게 grill_comment가 알아서 order가 되지?
    # now, elem of votes : {'grill_comment', 'new_count'}
    data['new_votes'] = list(votes)
    data['last_update'] = last_update
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder),
                        content_type="application/json")


def vote_comment(request, grill_id):
    # Input : Grill, GrillCommentOrder, User, is_up이 담긴 POST
    # Process : 1. User가 이 코멘트에 대해 투표했었는지 확인 - 했다면 exception?
    #           2. 투표 처리
    post_data = request.POST
    target_order = post_data['grill_comment_order']
    if post_data['is_up'] == 'true':
        is_up = True
    else:
        is_up = False
    profile = get_object_or_404(UserProfile, user=request.user)
    target_comment = get_object_or_404(GrillComment,
                                       grill__id=grill_id,
                                       order=target_order)
    if GrillCommentVote.objects.filter(grill_comment=target_comment,
                                       userprofile=profile).count():
        return HttpResponse("0")
    new_vote = GrillCommentVote(userprofile=profile,
                                grill_comment=target_comment,
                                is_up=is_up)
    new_vote.save()
    return HttpResponse("1")
