#imports is a sign of dodiligence
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from messageboard.models import Board, Topic, Post
from django.core.management import call_command
from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase, Client

class VisitAndCreateTopics(StaticLiveServerTestCase):
    def setUp(self):
        call_command("create_groups")

        self.u = User.objects.create(username="userer", password="raweogihrwr")
        self.u.set_password("raweogihrwr")
        self.u.groups.set([Group.objects.get(name="worker")])
        self.u.save()

        self.b = Board.objects.create(name="g", description="general messages")

        self.browser = webdriver.Firefox()
    
    def tearDown(self):
        self.browser.quit()
    
    def test(self):
        """
        ---------------------------------------------------------------------------------
        | THIS CODE IS SO GODDAMN PRETTY EVEN GOD COULD NOT HAVE WRITTEN IT BETTER!!!!! |
        ---------------------------------------------------------------------------------
        go to messageboard get redirected to login
        login
        click unpinned board
        click newtopic
        add a new pinned topic
        add a reply
        check that both "message" and "reply" are what they should be
        click edit
        edit first post
        check that its been edited
        go back to boards page
        click pinned board
        check that the same pinned topic is in pinned board
        click the topic
        check that messages is what they should be
        click edit button
        click cancel button get redirected back
        click edit button
        click delete
        click pinned board
        check that the board is empty
        check that there is no "new topic" button
        """

        self.browser.get(f'{self.live_server_url}/messageboards/board/')
        inputbox = self.browser.find_elements_by_class_name('form-control  ')
        
        #dont look at this for too long, only quick glances at a time
        for _ in range(2):
            inputbox[0].send_keys(Keys.BACK_SPACE)
            inputbox[1].send_keys(Keys.BACK_SPACE)
        
        inputbox[0].send_keys('userer')
        inputbox[1].send_keys('raweogihrwr')

        login_button = self.browser.find_element_by_name('button')
        login_button.click()
    
        general_button = self.browser.find_element_by_link_text('g')

        general_button.click()

        new_topic_button = self.browser.find_element_by_link_text('New topic')
        new_topic_button.click()

        subject_box = self.browser.find_element_by_name('subject')
        message_box = self.browser.find_element_by_name('message')
        pinned_box = self.browser.find_element_by_name('pinned')
        post_button = self.browser.find_element_by_name('post')

        subject_box.send_keys('newsubject')
        message_box.send_keys('newmessage')

        pinned_box.click()
        post_button.click()

        time.sleep(1)
        
        reply_button = self.browser.find_element_by_name('reply')
        reply_button.click()

        reply_message_box = self.browser.find_element_by_name('message')
        post_reply_button = self.browser.find_element_by_name('postreply')

        reply_message_box.send_keys('newreply')
        post_reply_button.click()

        message_and_reply = self.browser.find_elements_by_name('messages')
   
        self.assertEqual(message_and_reply[0].text, 'newmessage')
        self.assertEqual(message_and_reply[1].text, 'newreply')

        edit_button = self.browser.find_element_by_name('editbutton')
        
        edit_button.click()

        save_button = self.browser.find_element_by_name('savebutton')

        edit_message_box = self.browser.find_element_by_name('message')
        edit_message_box.send_keys('edited')

        save_button.click()

        message_and_reply = self.browser.find_elements_by_name('messages')
        self.assertEqual(message_and_reply[0].text, 'newmessageedited')
        self.assertEqual(message_and_reply[1].text, 'newreply')

        go_back = self.browser.find_element_by_link_text('Boards')
        go_back.click()

        pinned_button = self.browser.find_element_by_name('pinned')
        pinned_button.click()

        same_topic = self.browser.find_element_by_link_text('newsubject')

        self.assertEqual(same_topic.text, 'newsubject')

        same_topic.click()

        message_and_reply = self.browser.find_elements_by_name('messages')
        self.assertEqual(message_and_reply[0].text, 'newmessageedited')
        self.assertEqual(message_and_reply[1].text, 'newreply')

        edit_button = self.browser.find_element_by_name('editbutton')
        edit_button.click()

        cancel_button = self.browser.find_element_by_name('cancel')
        cancel_button.click()

        edit_button = self.browser.find_element_by_name('editbutton')
        edit_button.click()

        del_button = self.browser.find_element_by_name('deletebutton')
        del_button.click()
        
        comfirm_del_button = self.browser.find_element_by_name('deletebutton')
        comfirm_del_button.click()

        pinned_button = self.browser.find_element_by_name('pinned')
        pinned_button.click()
        
        #this should probably be done differently, works though
        failure = False
        try:
            same_topic = self.browser.find_element_by_link_text('newsubject')
        except:
            failure = True
        self.assertEqual(failure, True)

        failure2 = False
        try:
            new_topic_button = self.browser.find_element_by_link_text('New topic')
        except:
            failure2 = True
        self.assertEqual(failure2, True)


        
        
