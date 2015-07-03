# -*- coding: utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import GrillComment, Grill, GrillCommentVote
from apps.session.models import UserProfile
from .forms import GrillAddForm, CommentAddForm
from django.core.serializers.json import DjangoJSONEncoder
import json
import datetime


def home(request):
    grills = Grill.objects.all().order_by('created_time')  # 나중에 업데이트 순서로 바꾸기?
    return render(request, 'grill/main.html',
                  {
                      'grills': grills,
                  })


def view_grill(request, grill_id):
    grill = get_object_or_404(Grill, pk=grill_id)

    edit_form = CommentAddForm()
    comments = GrillComment.objects.filter(
        grill=grill_id).order_by('created_time').reverse()
    for comment in comments:
        # WARNING! 사용자가 HTML 코드를 작성하면 그대로 반영
        comment.content = comment.replace_tags()

    return render(request,
                  'grill/view.html',
                  {
                      'form': edit_form,
                      'grill_id': grill_id,
                      'comments': comments,
                      'grill': grill,
                  })


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
    new_comment = GrillComment(
        grill=grill, author=userprofile, content=post_data.get('new_content'))
    new_comment.save()
    new_comment.grill.updated_time = datetime.datetime.now()
    new_comment.grill.save()
    # setattr(grill, 'updated_time', datetime.datetime.now())
    # grill.save()
    data = {'new_content': new_comment.replace_tags()}
    data['order'] = new_comment.order
    data['author'] = 1
    # 날짜 표현방식이 기존 댓글과 다르지만, '몇 초전', 'n분 전' 등으로 바꿀 예정이므로 무시.
    data['commented_at'] = getattr(new_comment, 'created_time')
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder),
                        content_type="application/json")


def refresh_comment(request, grill_id):
    new_index = request.POST['required_index']
    if not new_index:
        new_index = 1
    comments = GrillComment.objects.filter(
        grill__id=grill_id, order__gte=new_index)
    json_comments = map(lambda x: x.to_json(), list(comments))
    data = {'comments': json_comments}
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder),
                        content_type="application/json")


def vote_up(request, grill_id):
    # Input : Grill, GrillCommentOrder, User, is_up이 담긴 POST
    # Process : 1. User가 이 코멘트에 대해 투표했었는지 확인 - 했다면 exception?
    #           2. 투표 처리
    post_data = request.POST
    target_order = post_data['grill_comment_order']
    is_up = post_data['is_up']
    profile = UserProfile.objects.filter(user=request.user)
    target_comment = GrillComment.objects.get_object_or_404(grill__id=grill_id,
                                                            order=target_order)
    if GrillCommentVote.objects.filter(grill_comment=target_comment,
                                       userprofile=profile).count():
        return 0
    new_vote = GrillCommentVote(userprofile=profile,
                                grill_comment=target_comment,
                                is_up=is_up)
    new_vote.save()
    return 0
