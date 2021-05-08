from django.test import TestCase
from django.core.exceptions import ValidationError
from inbox.models import Message
from django.core.management import call_command
from django.contrib.auth.models import User, Group, Permission
from django.core.validators import MaxLengthValidator

class MessageModelTest(TestCase):
    
    def setUp(self):
        call_command("create_groups")

        self.testUser = User.objects.create(username="workerName", password="testpsrd12?")
        self.testUser.set_password("testpsrd12?")
        self.testUser.groups.set([Group.objects.get(name="worker")])
        self.testUser.save()

        self.testUserTwo = User.objects.create(username="workerNameTwo", password="testpswrd12?")
        self.testUserTwo.set_password("testpswrd12?")
        self.testUserTwo.groups.set([Group.objects.get(name="worker")])
        self.testUserTwo.save()

        self.msg_one = Message.objects.create(
            sender = self.testUser,
            receiver = self.testUserTwo,
            multiple_receivers = 'testUserTwo',
            msg_title = "testMessage",
            msg_content = "This is a model test",
        )

        self.msg_multiple = Message.objects.create(
            sender = self.testUser,
            receiver = self.testUser,
            multiple_receivers = 'testUser, testUserTwo',
            msg_title = 'testMessageMultipleReceivers',
            msg_content = 'testMessageMultipleContent',
        )

        self.msg_multiple_2 = Message.objects.create(
            sender = self.testUser,
            receiver = self.testUserTwo,
            multiple_receivers = 'testUser, testUserTwo',
            msg_title = 'testMessageMultipleReceivers',
            msg_content = 'testMessageMultipleContent',
        )
    
    def test_sender_label(self):
        message = Message.objects.get(id=1)
        field_label = message._meta.get_field('sender').verbose_name
        self.assertEquals(field_label, 'sender')

    def test_receiver_label(self):
        message = Message.objects.get(id=1)
        field_label = message._meta.get_field('receiver').verbose_name
        self.assertEquals(field_label, 'receiver')

    def test_msg_multiple_receivers_label(self):
        message = Message.objects.get(id=1)
        field_label = message._meta.get_field('multiple_receivers').verbose_name
        self.assertEquals(field_label, 'multiple receivers')

    def test_msg_title_label(self):
        message = Message.objects.get(id=1)
        field_label = message._meta.get_field('msg_title').verbose_name
        self.assertEquals(field_label, 'msg title')
       
    def test_msg_content_label(self):
        message = Message.objects.get(id=1)
        field_label = message._meta.get_field('msg_content').verbose_name
        self.assertEquals(field_label, 'msg content')

    def test_sent_label(self):
        message = Message.objects.get(id=1)
        field_label = message._meta.get_field('sent').verbose_name
        self.assertEquals(field_label, 'sent')
    
    def test_read_label(self):
        message = Message.objects.get(id=1)
        field_label = message._meta.get_field('read').verbose_name
        self.assertEquals(field_label, 'read')

    def test_msg_title_max_length(self):
        message = Message.objects.get(id=1)
        max_length = message._meta.get_field('msg_title').max_length
        self.assertEquals(max_length, 56)

    def test_read_field_default_is_false(self):
        self.assertEqual(self.msg_one.read, False)

    

    
        

    # def test_get_last_msg(self):
    #     self.assertEqual(str(self.msg.getLastMsg(), ))