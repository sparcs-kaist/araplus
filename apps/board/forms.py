# -*- coding: utf-8
from apps.board.models import *
from apps.session.models import UserProfile
from django.forms import ModelForm, Textarea, BooleanField, CharField
from django.db.models import Q
import random
from django.forms.models import modelformset_factory
import datetime
from django_summernote.widgets import SummernoteWidget


prefix = [u'잔인한', u'츤츤대는', u'멋진', u'운좋은', u'귀여운']
name = [u'양아치', u'루저', u'외톨', u'올빼미', u'밤비']


class BoardForm(ModelForm):
    class Meta:
        model = Board
        fields = [
            'kor_name',
            'eng_name',
            'url',
            'description',
            'is_public',
            ]

    def __init__(self, *args, **kwargs):
        super(BoardForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.admin = kwargs.pop('admin')
        super(BoardForm, self).save(*args, **kwargs)
        return self.instance

    def clean(self):
        cleaned_data = super(BoardForm, self).clean()
        if 'url' in cleaned_data:
            url = cleaned_data['url']
            if url == 'all':
                msg = u'Invalid url'
                self.add_error('url', msg)
        return cleaned_data


class BoardMemberForm(ModelForm):
    class Meta:
        model = BoardMember
        fields = {
            'member',
            'write', }

    def __init__(self, *args, **kwargs):
        self.board = kwargs.pop('board', None)
        super(BoardMemberForm, self).__init__(*args, **kwargs)
        self.fields['member'] = CharField(required=True)

    def save(self, *args, **kwargs):
        self.instance.board = self.board
        super(BoardMemberForm, self).save(*args, **kwargs)
        return self.instance

    def clean(self):
        cleaned_data = super(BoardMemberForm, self).clean()
        if cleaned_data.get('member', ''):
            try:
                member = UserProfile.objects.get(
                    nickname=cleaned_data['member'])
                if BoardMember.objects.filter(board=self.board, member=member):
                    msg = u'Aleady added'
                    self.add_error('member', msg)
                cleaned_data['member'] = member
            except:
                msg = u'User not exist'
                self.add_error('member', msg)
        return cleaned_data


class BoardContentForm(ModelForm):
    class Meta:
        model = BoardContent
        exclude = ['is_deleted', 'modify_log']
        widgets = {
            'content': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        is_modify = kwargs.pop('is_modify', False)
        self.author = kwargs.pop('author', None)
        super(BoardContentForm, self).__init__(*args, **kwargs)
        self.fields['is_anonymous'] = BooleanField(required=False)
        if is_modify:
            del self.fields['is_anonymous']

    def save(self, *args, **kwargs):
        board_post = kwargs.pop('post', None)
        try:
            if self.cleaned_data['is_anonymous']:
                self.instance.is_anonymous = _get_name(self.author,
                                                       board_post)
            else:
                self.instance.is_anonymous = None
        except:
            self.cleaned_data['is_anonymous'] = self.instance.is_anonymous
        super(BoardContentForm, self).save(*args, **kwargs)
        return self.instance

    def clean(self, *args, **kwargs):
        cleaned_data = super(BoardContentForm, self).clean()
        if cleaned_data.get('is_anonymous', ''):
            today = datetime.datetime.now().date()
            tomorrow = today + datetime.timedelta(1)
            if BoardContent.objects.filter(
                    ~Q(is_anonymous=None),
                    Q(board_post__author=self.author)
                    | Q(board_comment__author=self.author),
                    created_time__gte=today,
                    created_time__lt=tomorrow).count() > 4:
                msg = u'exceed anonymous post limits'
                self.add_error('is_anonymous', msg)
        return cleaned_data


class BoardPostForm(ModelForm):
    class Meta:
        model = BoardPost
        fields = ['title', 'board_category', 'is_notice', ]
        labels = {
            'board_category': 'Category',
        }

    def __init__(self, *args, **kwargs):
        is_modify = kwargs.pop('is_modify', False)
        is_staff = kwargs.pop('is_staff', False)
        super(BoardPostForm, self).__init__(*args, **kwargs)
        self.fields['board_category'].queryset = BoardCategory.objects.all()
        if is_modify or not is_staff:
            del self.fields['is_notice']

    def save(self, *args, **kwargs):
        self.instance.author = kwargs.pop('author')
        self.instance.board_content = kwargs.pop('content')
        self.instance.board = kwargs.pop('board')
        return super(BoardPostForm, self).save(*args, **kwargs)

    """def clean(self):
        cleaned_data = super(BoardPostForm, self).clean()
        print cleaned_data
        if 'board' in cleaned_data:
            board = cleaned_data['board']
            board_category = cleaned_data['board_category']
            if (board_category and
                    board_category.board != board):
                msg = u"Invalid Selection"
                self.add_error('board_category', msg)
            if board.is_deleted:
                msg = u"Deleted Board"
                self.add_error('board', msg)
        else:
            msg = u"Select Board first"
            self.add_error('board_category', msg)
        return cleaned_data"""


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


class BoardAttachmentForm(ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', ]

#    def save(self, *args, **kwargs):
#        self.instance.board_content = kwargs.pop('content')
#        retsuper(BoardAttachmentForm


AttachmentFormSet = modelformset_factory(
    model=Attachment,
    form=BoardAttachmentForm,
    can_delete=True,
    max_num=5,
    validate_max=True)


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
