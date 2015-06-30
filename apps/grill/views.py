# -*- coding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Comment, Grill
from .forms import GrillAddForm, CommentAddForm
from django.core.urlresolvers import reverse_lazy

# Create your views here.
def home(request):
    grills = Grill.objects.all().order_by('created_at') # 나중에 업데이트 순서로 바꾸기?
    return render(request, 'grill/main.html',
        {
            'grills':grills,
        })

def view_grill(request, grill_id):
    edit_form = CommentAddForm()
    comments = Comment.objects.filter(grill = grill_id).order_by('created_at')
    return render(request,
        'grill/view.html',
        {
            'form':edit_form,
            'grill_id':grill_id,
            'comments':comments,
        })

def add_grill(request):
    if request.method == "GET":
        edit_form = GrillAddForm()
    elif request.method == "POST":
        edit_form = GrillAddForm(request.POST)
        if edit_form.is_valid():
            new_grill = Grill(title = edit_form.cleaned_data['title'],
                author = 1, contents = edit_form.cleaned_data['contents'])
            new_grill.save()
            return redirect(new_grill.get_absolute_url())


    return render(request, 
        'grill/add_grill.html', 
        {
            'form':edit_form,
        })


def add_comment(request, grill_id):
    if request.method == "POST":
        add_form = CommentAddForm(request.POST)
        if add_form.is_valid():
            new_comment = Comment(grill = grill_id,author = 1, contents = add_form.cleaned_data['contents'])
            new_comment.save()
            # return redirect(new_comment.get_absolute_url())
            return redirect(reverse_lazy('view_grill', kwargs = {'grill_id':grill_id}))

