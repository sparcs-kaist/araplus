# -*- coding: utf-8
from apps.channel.models import *
from django.forms import ModelForm, Textarea, BooleanField, FileField
import random


prefix = [u'잔인한', u'츤츤대는', u'멋진', u'운좋은', u'귀여운']
name = [u'양아치', u'루저', u'외톨', u'올빼미', u'밤비']


class ChannelForm(ModelForm):
    class Meta:
        model = Channel
        fields = [
                    'kor_name',
                    'eng_name',
                    'url',
                    'description',
                    'is_public',
                 ]

    def __init__(self, *args, **kwargs):
        super(ChannelForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.admin = kwargs.pop('admin')
        super(ChannelForm, self).save(*args, **kwargs)
        return self.instance

    def clean(self):
        cleaned_data = super(ChannelForm, self).clean()
        if 'url' in cleaned_data:
            url = cleaned_data['url']
            if url == 'all':
                msg = u"Invalid url"
                self.add_error('url', msg)
        return cleaned_data


class ChannelContentForm(ModelForm):
    class Meta:
        model = ChannelContent
        exclude = ['is_deleted', 'modify_log']
        widgets = {
            'content': Textarea(attrs={'rows': 15, }),
        }

    def __init__(self, *args, **kwargs):
        is_modify = kwargs.pop('is_modify', False)
        super(ChannelContentForm, self).__init__(*args, **kwargs)
        self.fields['is_anonymous'] = BooleanField(required=False)
        if is_modify:
            del self.fields['is_anonymous']

    def save(self, *args, **kwargs):
        channel_post = kwargs.pop('post', None)
        author = kwargs.pop('author')
        try:
            if self.cleaned_data['is_anonymous']:
                self.instance.is_anonymous = _get_name(author, channel_post)
            else:
                self.instance.is_anonymous = None
        except:
            self.cleaned_data['is_anonymous'] = self.instance.is_anonymous
        super(ChannelContentForm, self).save(*args, **kwargs)
        return self.instance


class ChannelPostForm(ModelForm):
    class Meta:
        model = ChannelPost
        fields = ['title', 'channel', 'is_notice', ]
        
    def __init__(self, *args, **kwargs):
        is_modify = kwargs.pop('is_modify', False)
        super(ChannelPostForm, self).__init__(*args, **kwargs)
        if is_modify:
            del self.fields['is_notice']

    def save(self, *args, **kwargs):
        self.instance.author = kwargs.pop('author')
        self.instance.channel_content = kwargs.pop('content')
        return super(ChannelPostForm, self).save(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ChannelPostForm, self).clean()
        if 'channel' in cleaned_data:
            channel = cleaned_data['channel']
            if channel.is_deleted:
                msg = u"Deleted Channel"
                self.add_error('channel', msg)
        else:
            msg = u"Select Channel first"
        return cleaned_data


class ChannelReportForm(ModelForm):
    class Meta:
        model = ChannelReport
        fields = ['reason', 'content', ]
        widgets = {
            'content': Textarea(attrs={'placeholder': 'Write Something', })
        }

    def save(self, *args, **kwargs):
        self.instance.userprofile = kwargs.pop('user')
        self.instance.channel_content = kwargs.pop('content')
        return super(ChannelReportForm, self).save(*args, **kwargs)

class ChannelAttachmentForm(ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', ]

    def save(self, *args, **kwargs):
        self.instance.file = kwargs.pop('file')
        self.instance.channel_content = kwargs.pop('content')
        return super(ChannelAttachmentForm, self).save(*args, **kwargs)


def _is_anonymous_duplicate(channel_post, name, cache):
    if not channel_post:
        return False, []
    if cache:
        return name in cache, cache
    former_comments = channel_post.channel_comment.all()
    names = [comment.channel_content.is_anonymous
             for comment in former_comments
             if comment.channel_content.is_anonymous]
    names.append(channel_post.channel_content.is_anonymous)
    if name in names:
        return True, names
    else:
        return False, names


def _generate_name(channel_post=None):
    prefix_index = random.randint(0, 4)
    name_index = random.randint(0, 4)
    anonymous_name = prefix[prefix_index] + ' ' + name[name_index]
    ret_val, cache = _is_anonymous_duplicate(channel_post, anonymous_name, [])
    while ret_val:
        prefix_index = random.randint(0, 4)
        name_index = random.randint(0, 4)
        anonymous_name = prefix[prefix_index] + ' ' + name[name_index]
        ret_val, cache = _is_anonymous_duplicate(channel_post, anonymous_name,
                                                 cache)
    return anonymous_name


def _get_name(author, channel_post=None):
    if channel_post:
        if (author == channel_post.author
                and channel_post.channel_content.is_anonymous):
            return channel_post.channel_content.is_anonymous
        else:
            former_comments = channel_post.channel_comment.filter(author=author)
            for comment in former_comments:
                if comment.channel_content.is_anonymous:
                    return comment.channel_content.is_anonymous
            return _generate_name(channel_post)
    else:
        return _generate_name(channel_post)
