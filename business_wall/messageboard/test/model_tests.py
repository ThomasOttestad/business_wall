from django.test import TestCase
from django.core.exceptions import ValidationError
from messageboard.models import Board, Topic, Post
from django.core.management import call_command
from django.contrib.auth.models import User, Group, Permission
from django.core.validators import MaxLengthValidator

class BoardModelTest(TestCase):

    def setUp(self):
        call_command("create_groups")

        self.w = User.objects.create(username="worker", password="raweogihrwr")
        self.w.set_password("raweogihrwr")
        self.w.groups.set([Group.objects.get(name="worker")])
        self.w.save()

        self.board = Board.objects.create(name="test", description="test")
        self.topic = Topic.objects.create(
            subject="subject",
            board=self.board,
            original_poster=self.w,
        )
        self.post = Post.objects.create(
            message="message",
            topic=self.topic,
            created_by=self.w,
        )
    
    def test_board_duplicate_invalid(self):
        with self.assertRaises(ValidationError):
            same_board = Board(name="test", description="test")
            same_board.validate_unique()
        
    def test_name_invalid(self):
            same_board = Board(
                name="iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",
                description="test"
                )
            max_length = same_board._meta.get_field('name').max_length
            self.assertEquals(max_length, 30)
    
    def test_board_post_count_function(self):
        self.assertEqual(self.board.get_posts_count(), 1)

    def test_board_get_last_post_function(self):
        self.assertEqual(self.board.get_last_post(), self.post)
        
    def test_board_str_function(self):
        self.assertEqual(str(self.board), "test")


class TopicModelTest(TestCase):

    def setUp(self):
        call_command("create_groups")

        self.w = User.objects.create(username="worker", password="raweogihrwr")
        self.w.set_password("raweogihrwr")
        self.w.groups.set([Group.objects.get(name="worker")])
        self.w.save()

        self.board = Board.objects.create(name="test", description="test")
        self.topic = Topic.objects.create(
            subject="subject",
            board=self.board,
            original_poster=self.w,
        )
        self.topic_pinned = Topic.objects.create(
            subject="subject2",
            board=self.board,
            original_poster=self.w,
            pinned=True,
        )
        self.post = Post.objects.create(
            message="message",
            topic=self.topic,
            created_by=self.w,
        )

    def test_topic_duplicate_invalid(self):
        with self.assertRaises(ValidationError):
            same_topic = Topic(
                subject="subject",
                board=self.board,
                original_poster=self.w,
            )
            same_topic.validate_unique()

    def test_topic_subject_max_length(self):
        max_length = self.topic._meta.get_field('subject').max_length
        self.assertEquals(max_length, 100)
    
    def test_topic_pinned_valid(self):
        self.assertEquals(self.topic_pinned.pinned, True)
    
    def test_view_count_zero(self):
        self.assertEquals(self.topic.views, 0)
    
    def test_topic_board_relation_board_is_board(self):
        self.assertEquals(self.topic.board, self.board)
    
    def test_topic_board_relation_boardname(self):
        self.assertEquals(self.topic.board.name, "test")

    def test_topic_original_poster(self):
        self.assertEquals(self.topic.original_poster, self.w)
    
    def test_topic_str_function(self):
        self.assertEquals(str(self.topic), "subject")


class PostModelTest(TestCase):
    def setUp(self):
        call_command("create_groups")

        self.w = User.objects.create(username="worker", password="raweogihrwr")
        self.w.set_password("raweogihrwr")
        self.w.groups.set([Group.objects.get(name="worker")])
        self.w.save()

        self.board = Board.objects.create(name="test", description="test")
        self.topic = Topic.objects.create(
            subject="subject",
            board=self.board,
            original_poster=self.w,
        )
        self.topic_pinned = Topic.objects.create(
            subject="subject2",
            board=self.board,
            original_poster=self.w,
            pinned=True,
        )
        self.post = Post.objects.create(
            message="message",
            topic=self.topic,
            created_by=self.w,
        )
        self.post2 = Post.objects.create(
            message="message2",
            topic=self.topic,
            created_by=self.w,
            reply=True,
        ) 

    def test_post_subject_max_length(self):
        max_length = self.post._meta.get_field('message').max_length
        self.assertEquals(max_length, 4000)
    
    def test_post_reply_false(self):
        self.assertEquals(self.post.reply, False)
    
    def test_post_reply_true(self):
        self.assertEquals(self.post2.reply, True)
    
    def test_post_count_board_function(self):
        self.assertEqual(self.board.get_posts_count(), 2)
    
    def test_post_topic(self):
        self.assertEqual(self.post.topic, self.topic)
    
    def test_default_fields(self):
        self.assertEqual(self.post.updated_at, None)
        self.assertEqual(self.post.updated_by, None)
