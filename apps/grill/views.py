# -*- coding: utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import GrillComment, Grill, GrillCommentVote
from apps.session.models import UserProfile
from .forms import GrillAddForm, CommentAddForm
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
import json
import datetime


def home(request):
    if not request.user.is_authenticated():
        return redirect('/session/login')

    grills = Grill.objects.all().order_by('created_time')  # 나중에 업데이트 순서로 바꾸기?
    return render(request, 'grill/main.html',
                  {
                      'grills': grills,
                  })


def view_grill(request, grill_id):
    if not request.user.is_authenticated():
        return redirect('/session/login')

    grill = get_object_or_404(Grill, pk=grill_id)
    edit_form = CommentAddForm()
    comments = GrillComment.objects.filter(
        grill=grill_id).order_by('created_time').reverse()
    profile = get_object_or_404(UserProfile, user=request.user)
    user_vote = GrillCommentVote.objects.filter(userprofile=profile)
    for comment in comments:
        # WARNING! 사용자가 HTML 코드를 작성하면 그대로 반영
        comment.content = comment.replace_tags()
        comment.like = GrillCommentVote.objects.filter(
            grill_comment=comment,
            is_up=True).count()
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


def add_grill(request):
    if not request.user.is_authenticated():
        return redirect('session/login')

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
    new_comment = GrillComment(
        grill=grill, author=userprofile, content=post_data.get('new_content'))
    new_comment.save()
    new_comment.grill.updated_time = datetime.datetime.now()
    new_comment.grill.save()

    ms = '<li id="comment_' + str(new_comment.order) + \
        '" class="a-comment-of-list">'
    ms += '<div class="a-comment-area">'
    ms += ' <span>' + str(new_comment.order) + '</span>'
    ms += '<div class="a-comment-content">' + \
        new_comment.replace_tags().encode('utf8') + '</div>'
    ms += '<div class="a-comment-info">'
    ms += '<div class="a-comment-author-container">'
    ms += '<span>' + new_comment.author.nickname.encode('utf8') + '</span>'
    ms += '<span class="a-comment-date">' + \
        str(new_comment.created_time) + '</span>'
    ms += '</div>'
    ms += '<div class="a-comment-vote-container">'
    ms += '<button class="vote_up a-comment-vote"> 추천 (+0) </button>'
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
        created_time__gte=last_update).values('grill_comment')
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
    is_up = post_data['is_up']
    profile = get_object_or_404(UserProfile, user=request.user)
    target_comment = get_object_or_404(GrillComment, grill__id=grill_id,
                                       order=target_order)
    if GrillCommentVote.objects.filter(grill_comment=target_comment,
                                       userprofile=profile).count():
        return HttpResponse("0")
    new_vote = GrillCommentVote(userprofile=profile,
                                grill_comment=target_comment,
                                is_up=is_up)
    new_vote.save()
    return HttpResponse("1")
