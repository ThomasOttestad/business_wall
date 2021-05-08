from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from messageboard.models import Board, Topic, Post
from django.core.management import call_command
from django.contrib.auth.models import User, Group, Permission

class ViewTest(TestCase):
    def setUp(self):
        call_command("create_groups")

        self.u = User.objects.create(username="userer", password="raweogihrwr")
        self.u.set_password("raweogihrwr")
        self.u.groups.set([Group.objects.get(name="worker")])
        self.u.save()

        self.unauth = User.objects.create(username="userer2", password="oiwejfiowejf")
        self.unauth.set_password("oiwejfiowejf")
        self.unauth.groups.set([Group.objects.get(name="worker")])
        self.unauth.save()

        self.unlogged = Client()
        
        self.c = Client()
        login = self.c.login(username="userer", password="raweogihrwr")
        self.assertEqual(login, True, "Failed to login")

        self.un = Client()
        login_un = self.un.login(username="userer2", password="oiwejfiowejf")
        self.assertEqual(login_un, True, "Failed to login")

        self.b = Board.objects.create(name="general", description="general messages")
        
        self.t = Topic.objects.create(
            subject="first subject",
            board=self.b,
            original_poster=self.u,
        )

        self.p = Post.objects.create(
            message="first message",
            topic=self.t,
            created_by=self.u,
        )
    
    #login requirements tests
    def test_assert_loggin_failure_for_unlogged_client_board_home(self):
        response = self.unlogged.get(f'/messageboards/board/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/messageboards/board/')
    
    def test_assert_loggin_failure_for_unlogged_client_board_topics(self):
        response = self.unlogged.get(f'/messageboards/board/{self.b.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/messageboards/board/{self.b.pk}/')
    
    def test_assert_loggin_failure_for_unlogged_client_board_topics_new(self):
        response = self.unlogged.get(f'/messageboards/board/{self.b.pk}/new/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/messageboards/board/{self.b.pk}/new/')
    
    def test_assert_loggin_failure_for_unlogged_client_board_topics_post_overview(self):
        response = self.unlogged.get(f'/messageboards/board/{self.b.pk}/topics/{self.t.pk}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/messageboards/board/{self.b.pk}/topics/{self.t.pk}')

    def test_assert_loggin_failure_for_unlogged_client_board_topics_post_reply(self):
        response = self.unlogged.get(f'/messageboards/board/{self.b.pk}/topics/{self.t.pk}/reply')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/messageboards/board/{self.b.pk}/topics/{self.t.pk}/reply')
    
    def test_assert_loggin_failure_for_unlogged_client_board_topics_post_edit(self):
        response = self.unlogged.get(f'/messageboards/board/{self.b.pk}/topics/{self.t.pk}/posts/{self.p.pk}/edit/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/messageboards/board/{self.b.pk}/topics/{self.t.pk}/posts/{self.p.pk}/edit/')

    def test_assert_loggin_failure_for_unlogged_client_delete_post(self):
        response = self.unlogged.get(f'/messageboards/delete/{self.p.pk}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/messageboards/delete/{self.p.pk}')
    

    #-----------------------------------------------------------------
    #resolve to page tests
    def test_board_resolve_to_board_home_page(self):
        response = self.c.get(f'/messageboards/board/')
        self.assertTemplateUsed(response, 'boards.html')
    
    def test_board_pk_resolve_to_topics_page(self):
        response = self.c.get(f'/messageboards/board/{self.b.pk}/')
        self.assertTemplateUsed(response, 'topics.html')
    
    def test_board_pk_topics_pk_resolve_to_topic_posts_page(self):
        response = self.c.get(f'/messageboards/board/{self.b.pk}/topics/{self.t.pk}')
        self.assertTemplateUsed(response, 'topic_posts.html')
    
    def test_new_topic_resolve_to_newtopic_page(self):
        response = self.c.get(f'/messageboards/board/{self.b.pk}/new/')
        self.assertTemplateUsed(response, 'new_topic.html')
    
    def test_reply_resolve_to_reply_page(self):
        response = self.c.get(f'/messageboards/board/{self.b.pk}/topics/{self.t.pk}/reply')
        self.assertTemplateUsed(response, 'reply_topic.html')
    
    def test_edit_post_resolve_to_edit_page(self):
        response = self.c.get(f'/messageboards/board/{self.b.pk}/topics/{self.t.pk}/posts/{self.p.pk}/edit/')
        self.assertTemplateUsed(response, 'edit_post.html')
    
    def test_delete_post_resolve_to_deletepost_page(self):
        response = self.c.get(f'/messageboards/delete/{self.p.pk}')
        self.assertTemplateUsed(response, 'delete_post.html')
    
    #-----------------------------------------------------------------
    #ownership tests
    
    def test_ownership_of_message_when_deleting_assert_contains_failure_message(self):
        response = self.un.get(f'/messageboards/delete/1')
        self.assertContains(response, "<h1>Something weird happened, please go back!</h1>")

    def test_ownership_of_message_when_deleting_assert_contains_delete_comfirmation(self):
        response = self.c.get(f'/messageboards/delete/1')
        self.assertContains(response, "<h1>Are you sure you want to delete this message? </h1>")

    def test_ownership_edit_post_when_editing_post_success(self):
        response = self.c.get(f'/messageboards/board/{self.b.pk}/topics/{self.t.pk}/posts/{self.p.pk}/edit/')
        self.assertEqual(response.status_code, 200)
    
    def test_ownership_edit_post_when_editing_post_failure(self):
        response = self.un.get(f'/messageboards/board/{self.b.pk}/topics/{self.t.pk}/posts/{self.p.pk}/edit/')
        self.assertEqual(response.status_code, 404)

    #--------------------------------------------------------------------------