from django.contrib import auth
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from producthuntclone.test_utils import CONTEXT_INDEX


class SignUpTests(TestCase):
    def get_post_response(self, data=None):
        return self.client.post(reverse('signup'), data=data or {'username': '', 'password1': '', 'password2': ''})

    def test_get_method_returns_signup_page(self):
        """
        GET method should load 'accounts/signup.html' page.
        """
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_empty_username_raises_error(self):
        """
        If `username` parameter is empty 'accounts/signup.html'
        with `error` parameter should be loaded.
        """
        response = self.get_post_response()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertEqual(response.context[CONTEXT_INDEX]['error'], _('username_empty_error'))

    def test_empty_password1_raises_error(self):
        """
        If `password1` parameter is empty 'accounts/signup.html'
        with `error` parameter should be loaded.
        """
        response = self.get_post_response({'username': 'test', 'password1': '', 'password2': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertEqual(response.context[CONTEXT_INDEX]['error'], _('password_empty_error'))

    def test_empty_password2_raises_error(self):
        """
        If `password2` parameter is empty 'accounts/signup.html'
        with `error` parameter should be loaded.
        """
        response = self.get_post_response({'username': 'test', 'password1': 'test', 'password2': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertEqual(response.context[CONTEXT_INDEX]['error'], _('password_empty_error'))

    def test_different_passwords_raises_error(self):
        """
        If `password1` and `password2` parameters are different
        'accounts/signup.html' with `error` parameter should be loaded.
        """
        pass

    def test_existing_username_raises_error(self):
        """
        If user is already registered  'accounts/signup.html'
        with `error` parameter should be loaded.
        """
        response = self.get_post_response({'username': 'test', 'password1': 'test', 'password2': 'test-different'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertEqual(response.context[CONTEXT_INDEX]['error'], _('passwords_not_equal_error'))

    def test_correct_credentials_create_user(self):
        """
        If `username`, `password1`, `password2` are correct
        new user is created.
        """
        self.get_post_response({'username': 'test', 'password1': 'test', 'password2': 'test'})
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_correct_credentials_redirects_to_home(self):
        """
        If `username`, `password1`, `password2` are correct
        the flow should be redirected to home page.
        """
        response = self.get_post_response({'username': 'test', 'password1': 'test', 'password2': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')


class LoginTests(TestCase):
    def get_post_response(self, data=None):
        return self.client.post(reverse('login'), data=data or {'username': '', 'password': ''})

    def test_get_method_returns_login_page(self):
        """
        GET method should load 'accounts/login.html' page.
        """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_empty_username_raises_error(self):
        """
        If `username` parameter is empty 'accounts/login.html'
        with `error` parameter should be loaded.
        """
        response = self.get_post_response()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertEqual(response.context[CONTEXT_INDEX]['error'], _('username_empty_error'))

    def test_empty_password_raises_error(self):
        """
        If `password` parameter is empty 'accounts/login.html'
        with `error` parameter should be loaded.
        """
        response = self.get_post_response({'username': 'test', 'password': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertEqual(response.context[CONTEXT_INDEX]['error'], _('password_empty_error'))

    def test_wrong_credentials_raises_error(self):
        """
        If user with `username` and `password` does not exist
        'accounts/login.html' with `error` parameter should be loaded.
        """
        response = self.get_post_response({'username': 'test', 'password': 't'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertEqual(response.context[CONTEXT_INDEX]['error'], _('login_or_password_error'))

    def test_correct_credentials_redirects_to_home(self):
        """
        If `username` and `password` are correct
        the flow should be redirected to home page.
        """
        # create user
        self.client.post(reverse('signup'), {'username': 'test', 'password1': 'test', 'password2': 'test'})
        # do the test
        response = self.get_post_response({'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')


class LogoutTests(TestCase):
    def test_get_method_raises_value_error(self):
        try:
            self.client.get(reverse('logout'))
        except ValueError:
            pass

    def test_post_method_logouts_user(self):
        # create and login user
        self.client.post(reverse('signup'), {'username': 'test', 'password1': 'test', 'password2': 'test'})
        # logout them
        self.client.post(reverse('logout'))
        # # make assertions
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_post_method_redirects_to_home(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
