from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Comment
from .forms import CommentAddForm
from django.core.urlresolvers import reverse_lazy

# Create your views here.
def home(request):
    return render(request, 'grill/main.html')

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

def add_comment(request, grill_id):
    if request.method == "POST":
        add_form = CommentAddForm(request.POST)
        if add_form.is_valid():
            new_comment = Comment(grill = grill_id,author = 1, contents = add_form.cleaned_data['contents'])
            new_comment.save()
            # return redirect(new_comment.get_absolute_url())
            return redirect(reverse_lazy('view_grill', kwargs = {'grill_id':grill_id}))

