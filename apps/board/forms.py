# -*- coding: utf-8
from apps.board.models import *
from django.forms import ModelForm, Textarea, BooleanField
import random


prefix = [u'잔인한', u'츤츤대는', u'멋진', u'운좋은', u'귀여운']
name = [u'양아치', u'루저', u'외톨', u'올빼미', u'밤비']


class BoardForm(ModelForm):
    class Meta:
        model = Board
        fields = ['kor_name', 'eng_name', 'url', 'description', 'is_public', ]

    def __init__(self, *args, **kwargs):
        super(BoardForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(BoardForm, self).save(*args, **kwargs)
        return self.instance


class BoardContentForm(ModelForm):
    class Meta:
        model = BoardContent
        exclude = ['is_deleted', 'modify_log']
        widgets = {
            'content': Textarea(attrs={'rows': 15, }),
        }

    def __init__(self, *args, **kwargs):
        is_modify = kwargs.pop('is_modify', False)
        super(BoardContentForm, self).__init__(*args, **kwargs)
        self.fields['is_anonymous'] = BooleanField(required=False)
        if is_modify:
            del self.fields['is_anonymous']

    def save(self, *args, **kwargs):
        board_post = kwargs.pop('post', None)
        author = kwargs.pop('author')
        try:
            if self.cleaned_data['is_anonymous']:
                self.instance.is_anonymous = _get_name(author, board_post)
            else:
                self.instance.is_anonymous = None
        except:
            self.cleaned_data['is_anonymous'] = self.instance.is_anonymous
        super(BoardContentForm, self).save(*args, **kwargs)
        return self.instance


class BoardPostForm(ModelForm):
    class Meta:
        model = BoardPost
        fields = ['title', 'board', 'board_category', 'is_notice', ]
        labels = {
            'board_category': 'Category',
        }

    def __init__(self, *args, **kwargs):
        is_modify = kwargs.pop('is_modify', False)
        super(BoardPostForm, self).__init__(*args, **kwargs)
        self.fields['board_category'].queryset = BoardCategory.objects.all()
        if is_modify:
            del self.fields['is_notice']

    def save(self, *args, **kwargs):
        self.instance.author = kwargs.pop('author')
        self.instance.board_content = kwargs.pop('content')
        return super(BoardPostForm, self).save(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BoardPostForm, self).clean()
        if 'board' in cleaned_data:
            board = cleaned_data['board']
            board_category = cleaned_data['board_category']
            if (board_category and
                    board_category.board != board):
                msg = u"Invalid Selection"
                self.add_error('board_category', msg)
        else:
            msg = u"Select Board first"
            self.add_error('board_category', msg)
        return cleaned_data


class BoardReportForm(ModelForm):
    class Meta:
        model = BoardReport
        fields = ['reason', 'content', ]
        widgets = {
            'content': Textarea(attrs={'placeholder': 'Write Something', })
        }

    def save(self, *args, **kwargs):
        self.instance.userprofile = kwargs.pop('user')
        self.instance.board_content = kwargs.pop('content')
        return super(BoardReportForm, self).save(*args, **kwargs)


def _is_anonymous_duplicate(board_post, name, cache):
    if not board_post:
        return False, []
    if cache:
        return name in cache, cache
    former_comments = board_post.board_comment.all()
    names = [comment.board_content.is_anonymous
             for comment in former_comments
             if comment.board_content.is_anonymous]
    names.append(board_post.board_content.is_anonymous)
    if name in names:
        return True, names
    else:
        return False, names


def _generate_name(board_post=None):
    prefix_index = random.randint(0, 4)
    name_index = random.randint(0, 4)
    anonymous_name = prefix[prefix_index] + ' ' + name[name_index]
    ret_val, cache = _is_anonymous_duplicate(board_post, anonymous_name, [])
    while ret_val:
        prefix_index = random.randint(0, 4)
        name_index = random.randint(0, 4)
        anonymous_name = prefix[prefix_index] + ' ' + name[name_index]
        ret_val, cache = _is_anonymous_duplicate(board_post, anonymous_name,
                                                 cache)
    return anonymous_name


def _get_name(author, board_post=None):
    if board_post:
        if (author == board_post.author
                and board_post.board_content.is_anonymous):
            return board_post.board_content.is_anonymous
        else:
            former_comments = board_post.board_comment.filter(author=author)
            for comment in former_comments:
                if comment.board_content.is_anonymous:
                    return comment.board_content.is_anonymous
            return _generate_name(board_post)
    else:
        return _generate_name(board_post)
