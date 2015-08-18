# -*- coding: utf-8
from apps.channel.models import *
from django.forms import ModelForm, Textarea


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

    def save(self, *args, **kwargs):
        channel_post = kwargs.pop('post', None)
        author = kwargs.pop('author')
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
