# -*- coding: utf-8
from apps.channel.models import *
from django.forms import ModelForm, Textarea


class ChannelForm(ModelForm):
    class Meta:
        model = Channel
        exclude = ['admin', 'is_deleted']

    def save(self, *args, **kwargs):
        self.instance.is_deleted = False
        self.instance.admin = kwargs.pop('admin')
        return super(ChannelForm, self).save(*args, **kwargs)


class ChannelContentForm(ModelForm):
    class Meta:
        model = ChannelContent
        exclude = ['is_deleted', 'modify_log']
        widgets = {
            'content': Textarea(attrs={'rows': 15, }),
        }

    def save(self, *args, **kwargs):
        self.instance.is_deleted = False
        return super(ChannelContentForm, self).save(*args, **kwargs)


class ChannelPostForm(ModelForm):
    class Meta:
        model = ChannelPost
        fields = ['title', 'is_notice', 'thumbnail', ]

    def save(self, *args, **kwargs):
        self.instance.channel = kwargs.pop('channel')
        self.instance.author = kwargs.pop('author')
        self.instance.channel_content = kwargs.pop('content')
        return super(ChannelPostForm, self).save(*args, **kwargs)


class ChannelAttachmentForm(ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', ]

    def save(self, *args, **kwargs):
        self.instance.file = kwargs.pop('file')
        self.instance.channel_content = kwargs.pop('content')
        return super(ChannelAttachmentForm, self).save(*args, **kwargs)


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
