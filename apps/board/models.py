# -*- coding: utf-8 -*-
from django.db import models
import apps.session.models
from araplus.settings import UPLOAD_DIR
import json
import re
import cgi
from django.core.files.storage import default_storage
from django.core.files import File

hashtag_regex = re.compile(ur'(^|(?<=\s))#(?P<target>\w+)', re.UNICODE)
numtag_regex = re.compile(r'@(?P<target>\d+)')
nicktag_regex = re.compile(ur'@(?P<target>\w+)', re.UNICODE)
# regular expression for matching img src
imtag_regex = re.compile("<img.+?src=[\"'](.+?)[\"'].*?>")


def nick_to_order(nick, comment_nickname_list):
    orders = [item[1] for item in comment_nickname_list if item[0] == nick]
    if orders:
        return str(orders[-1])
    else:
        return False


def nicksub_regex_helper(match, comment_nickname_list):
    nick = match.group(1)
    order = nick_to_order(nick, comment_nickname_list)
    if order:
        return '<a title="comment_' + order + '" class="comment_preview" href="#comment_order_' + order + '">' + match.group() + '</a>'
    else:
        return match.group()


class BoardContent(models.Model):
    content = models.TextField(null=False)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, null=False)
    is_anonymous = models.TextField(default=None, null=True)
    is_adult = models.BooleanField(default=False, null=False)
    modify_log = models.TextField(default='[]')
    use_signiture = models.BooleanField(default=False, null=False)

    def set_log(self, log):
        self.modify_log = json.dumps(log)

    def get_log(self):
        return json.loads(self.modify_log)

    def __str__(self):
        if(self.id % 10 == 1):
            return "%dst content created in %s" % (self.id, self.created_time)
        elif(self.id % 10 == 2):
            return "%dnd content created in %s" % (self.id, self.created_time)
        elif(self.id % 10 == 3):
            return "%dnd content created in %s" % (self.id, self.created_time)
        else:
            return "%dth content created in %s" % (self.id, self.created_time)

    def get_vote(self):
        up = 0
        down = 0
        for content_vote in self.board_content_vote.all():
            if content_vote.is_up:
                up = up + 1
            else:
                down = down + 1
        vote = {}
        vote['up'] = up
        vote['down'] = down
        return vote

    def replace_content_tags(self, type, comment_nickname_list):
        # result = cgi.escape(self.content)
        result = self.content
        result = result.replace("\n", "<br />")
        if type == 'Comment':
            # 댓글 숫자 태그
            result = numtag_regex.sub(
                '<a title="comment_\g<target>" class="comment_preview" href="#comment_order_\g<target>">@\g<target></a>', result)
            # 댓글 닉네임 태그
            result = nicktag_regex.sub(lambda match:
                                       nicksub_regex_helper(
                                           match, comment_nickname_list),
                                       result)
        """else:
            # 글 작성 완료 했을 때 Image tag가 남아있는지 확인
            img_tags = imtag_regex.findall(result)
            print img_tags
            for img_src in img_tags:
                img_src = img_src.split('/')[2]
                print default_storage.url(img_src)
                print default_storage.path(img_src) """
        return hashtag_regex.sub(
            '\1<a href="../?tag=\g<target>">#\g<target></a>',
            result)

    def get_hashtags(self):
        return [tag[1] for tag in hashtag_regex.findall(self.content)]

    def get_numtags(self):
        return [int(tag) for tag in numtag_regex.findall(self.content)]

    def get_taged_order(self, comment_nickname_list):
        tag_list = [tag for tag in nicktag_regex.findall(self.content)]
        tag_list = set(tag_list)
        comment_nickname_list = dict(comment_nickname_list)
        order = [comment_nickname_list[item]
                 for item in comment_nickname_list if item in tag_list]
        return order

    def get_thumbnail(self):
        if self.attachment.exists():
            return self.attachment.all()[0].file.url
        else:
            return 'media/image/default.jpg'


# 이미지 경로를 지정해주기 위한 함수
def get_path(instance, filename):
    return filename


class Attachment(models.Model):
    file = models.FileField(null=False, upload_to=get_path)
    board_content = models.ForeignKey('BoardContent',
                                      related_name="attachment",
                                      null=False)



class BoardComment(models.Model):
    board_content = models.OneToOneField('BoardContent',
                                         related_name="board_comment",
                                         null=False)
    board_post = models.ForeignKey('BoardPost',
                                   related_name="board_comment",
                                   null=True)
    author = models.ForeignKey('session.UserProfile',
                               related_name="board_comment")

    def __str__(self):
        created_time = self.board_content.created_time
        author = self.author.user
        return "created in %s, authored by %s" % (created_time, author)


class BoardContentVote(models.Model):
    board_content = models.ForeignKey('BoardContent',
                                      related_name="board_content_vote",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="board_content_vote")
    is_up = models.BooleanField(null=False)


class BoardContentVoteAdult(models.Model):
    board_content = models.ForeignKey('BoardContent',
                                      related_name="board_content_vote_adult",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="board_content_vote_adult")


class BoardContentVotePolitical(models.Model):
    board_content = models.ForeignKey(
        'BoardContent',
        related_name="board_content_vote_political",
        null=False)
    userprofile = models.ForeignKey(
        'session.UserProfile',
        related_name="board_content_vote_political")


class BoardReport(models.Model):
    Reason1 = u'이유1'
    Reason2 = u'이유2'
    Etc = u'기타'
    Reason_Choice = (
        (Reason1, u'이유1'),
        (Reason2, u'이유2'),
        (Etc, u'기타'))
    reason = models.CharField(max_length=4,
                              choices=Reason_Choice,
                              default=Etc)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    board_content = models.ForeignKey('BoardContent',
                                      related_name="board_report",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="board_report")


class Board(models.Model):
    kor_name = models.CharField(max_length=45, null=False, unique=True)
    eng_name = models.CharField(max_length=45, null=False, unique=True)
    url = models.CharField(max_length=45, null=False, unique=True)
    description = models.CharField(max_length=100, null=False)
    admin = models.ForeignKey('session.UserProfile',
                              related_name="board",
                              null=False)
    is_official = models.BooleanField(default=False)
    is_gallery = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.kor_name


class BoardMember(models.Model):
    board = models.ForeignKey('Board',
                              related_name='board_member',
                              null=False)
    member = models.ForeignKey('session.userprofile',
                               related_name='board_member',
                               null=False)
    write = models.BooleanField(default=False)

    class Meta:
        unique_together = ('board', 'member',)


class BoardCategory(models.Model):
    name = models.CharField(max_length=10, null=False)
    board = models.ForeignKey('Board',
                              related_name='board_category',
                              null=False)


class BoardPost(models.Model):
    title = models.CharField(max_length=45, null=False)
    is_notice = models.BooleanField(default=False, null=False, db_index=True)
    is_best = models.BooleanField(default=False, db_index=True)
    board = models.ForeignKey('Board',
                              related_name='board',
                              null=False,
                              db_index=True)
    author = models.ForeignKey('session.UserProfile',
                               related_name='board_post')
    board_content = models.OneToOneField('BoardContent', null=False,
                                         related_name='board_post')
    board_category = models.ForeignKey('BoardCategory',
                                       related_name='board_post',
                                       null=True,
                                       blank=True)
    modify_log = models.TextField(default='[]')

    class Meta:
        ordering = ['-id']

    def get_is_read(self, request):
        try:
            return self.board_post_is_read.get(
                userprofile=request.user.userprofile)
        except:
            return None

    def set_log(self, log):
        self.modify_log = json.dumps(log)

    def get_log(self):
        return json.loads(self.modify_log)

    def __unicode__(self):
        title = self.title
        created_time = self.board_content.created_time
        author = self.author.user
        return u"title: %s created in %s, authored by %s" % (title,
                                                             created_time,
                                                             author)

    def get_notify_target(self):
        return self.board_post_trace.filter(is_notified=True).select_related("userprofile").prefetch_related("userprofile__user")


class BoardPostIs_read(models.Model):
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name='board_post_is_read')
    board_post = models.ForeignKey('BoardPost',
                                   related_name='board_post_is_read')
    last_read = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('userprofile', 'board_post',)


class BoardPostTrace(models.Model):
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name='board_post_trace')
    board_post = models.ForeignKey('BoardPost',
                                   related_name='board_post_trace')
    is_trace = models.BooleanField(default=True)
    is_notified = models.BooleanField(default=False)
    last_created = models.DateTimeField(auto_now=True)


class HashTag(models.Model):
    tag_name = models.TextField(null=False, db_index=True)
    board_post = models.ForeignKey('BoardPost',
                                   related_name="hashtag",
                                   null=False)
