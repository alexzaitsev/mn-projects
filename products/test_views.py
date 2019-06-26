from django.http import Http404
from django.test import TestCase
from django_bs_test import TestCase as BsTestCase

from producthuntclone.test_utils import *
from products.models import Product


class HomeTests(TestCase):
    PAGE_SIZE = 5

    def test_home_without_params(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/home.html')

    def test_no_products_info_is_shown_if_there_are_no_products(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'There are no products yet.')

    def test_create_btn_is_shown_if_there_are_no_products_and_user_is_authenticated(self):
        create_test_user_with_endpoint(self.client)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Create one')

    def test_signup_and_login_btn_are_shown_if_there_are_no_products_and_user_is_not_authenticated(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'class="btn btn-primary">Sign Up</a>')
        self.assertContains(response, 'class="btn btn-primary">Login</a>')

    def test_pagination_info_is_shown_if_there_are_more_products_to_show(self):
        create_test_user_with_endpoint(self.client)
        create_test_products_in_range(self.client, HomeTests.PAGE_SIZE * 2)

        response = self.client.get(reverse('home'))
        self.assertContains(response, 'page 1 of 2')

    def test_pagination_info_is_not_shown_if_all_products_are_shown(self):
        create_test_user_with_endpoint(self.client)
        create_test_products_in_range(self.client, HomeTests.PAGE_SIZE)

        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'page')

    def test_pagination_info_is_not_shown_if_there_are_no_products(self):
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'page')

    def test_first_page_is_shown_if_incorrect_page_is_passed(self):
        create_test_user_with_endpoint(self.client)
        create_test_products_in_range(self.client, HomeTests.PAGE_SIZE)

        url = f"{reverse('home')}?page=10"
        response = self.client.get(url)
        self.assertContains(response, 'TITLE1')

    def test_products_are_properly_sorted(self):
        create_test_user_with_endpoint(self.client)
        create_test_products_in_range(self.client, HomeTests.PAGE_SIZE)
        Product.objects.filter(title='title3').update(votes_total=3)
        Product.objects.filter(title='title2').update(votes_total=2)

        response = self.client.get(reverse('home'))
        text_response = response.content.decode('utf8')
        index_1 = text_response.index('TITLE3')
        index_2 = text_response.index('TITLE2')
        index_3 = text_response.index('TITLE4')
        index_4 = text_response.index('TITLE1')
        index_5 = text_response.index('TITLE0')
        self.assertTrue(index_1 < index_2 < index_3 < index_4 < index_5)


class CreateProductTests(TestCase):
    def setUp(self):
        create_test_user_with_endpoint(self.client)

    def empty_param_raises_error(self, data=None):
        response = self.client.post(reverse('create'), data or {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/create.html')
        self.assertEqual(response.context[-1]['error'], 'All fields are required')

    def test_get_method_returns_create_page(self):
        """
        GET method should load 'products/create.html' page.
        """
        response = self.client.get(reverse('create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/create.html')

    def test_empty_title_raises_error(self):
        """
        If `title` parameter is empty, 'products/create.html'
        with `error` parameter should be loaded.
        """
        self.empty_param_raises_error({'title': '', 'body': '', 'url': '', 'icon': test_image, 'image': test_image})

    def test_empty_body_raises_error(self):
        """
        If `body` parameter is empty, 'products/create.html'
        with `error` parameter should be loaded.
        """
        self.empty_param_raises_error({'title': 'title', 'body': '', 'url': '', 'icon': test_image, 'image': test_image})

    def test_empty_url_raises_error(self):
        """
        If `url` parameter is empty, 'products/create.html'
        with `error` parameter should be loaded.
        """
        self.empty_param_raises_error({'title': 'title', 'body': 'body', 'url': '', 'icon': test_image, 'image': test_image})

    def test_valid_url_without_schema_creates_product(self):
        """
        If `url` is valid but does not contain schema.
        No error is provided to 'products/create.html' page.
        """
        url = 'google.com'
        response = self.client.post(reverse('create'),
                                    {'title': 'title', 'body': 'body', 'url': url, 'icon': test_image, 'image': test_image})
        self.assertEqual(response.status_code, 302)

    def test_malformed_url_raises_error(self):
        """
        If `url` is malformed, 'products/create.html'
        with `error` parameter should be loaded.
        """
        url = 'googlecom'
        response = self.client.post(reverse('create'),
                                    {'title': 'title', 'body': 'body', 'url': url, 'icon': test_image, 'image': test_image})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/create.html')
        self.assertEqual(response.context[-1]['error'], 'URL must be valid')

    def test_correct_data_creates_product_in_database(self):
        """
        If provided data is correct, new product is created
        """
        create_test_product_with_endpoint(self.client)
        last_product = Product.objects.latest('id')
        self.assertEqual(last_product.title, 'title')

    def test_correct_data_redirects_to_details(self):
        """
        If provided data is correct, the flow is
        redirected to product details page.
        """
        response = create_test_product_with_endpoint(self.client)
        last_product = Product.objects.latest('id')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], f'/products/{last_product.pk}')


class DetailTests(BsTestCase):
    @staticmethod
    def find_upvote_btn(soup):
        links = soup.find_all('a')
        for link in links:
            if link.get('role') == 'button' and 'Upvote' in link.get_text():
                return link
        return None

    def test_upvote_button_is_visible_for_authenticated(self):
        """
        Upvote button is visible only if user is authenticated
        """
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        product = Product.objects.latest('id')
        response = self.client.get(reverse('detail', args=(product.pk,)))
        self.assertContains(response, 'Upvote')

    def test_upvote_button_is_not_visible_for_unauthenticated(self):
        """
        Upvote button is not visible if user is not authenticated
        """
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        product = Product.objects.latest('id')
        logout_test_user_with_endpoint(self.client)
        response = self.client.get(reverse('detail', args=(product.pk,)))
        self.assertNotContains(response, 'Upvote')

    def test_upvote_button_is_disabled_if_hunter_is_current_user(self):
        """
        Upvote button has `disabled` class if
        the product was created by the current user.
        """
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        product = Product.objects.latest('id')
        response = self.client.get(reverse('detail', args=(product.pk,)))
        upvote_btn = DetailTests.find_upvote_btn(response.soup)
        self.assertTrue('disabled' in upvote_btn['class'])

    def test_info_message_is_shown_if_hunter_is_current_user(self):
        """
        Html contains info message if
        the product was created by the current user.
        """
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        product = Product.objects.latest('id')
        response = self.client.get(reverse('detail', args=(product.pk,)))
        self.assertContains(response, 'You cannot vote on your own projects.')

    def test_upvote_button_is_enabled_if_hunter_is_not_current_user(self):
        """
        Upvote button doesn't have `disabled` class if
        the product was not created by the current user.
        """
        # signup, create product, logout
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        logout_test_user_with_endpoint(self.client)
        # signup another, get product
        create_test_user_with_endpoint(self.client, username='test_another', password='test_another')
        product = Product.objects.latest('id')
        # make request and assert
        response = self.client.get(reverse('detail', args=(product.pk,)))
        upvote_btn = DetailTests.find_upvote_btn(response.soup)
        self.assertTrue('disabled' not in upvote_btn['class'])

    def test_upvote_button_is_disabled_if_user_has_already_voted_on_somebody_s_question(self):
        # signup, create product, logout
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        logout_test_user_with_endpoint(self.client)
        # signup another, get product
        create_test_user_with_endpoint(self.client, username='test_another', password='test_another')
        product = Product.objects.latest('id')
        # vote on that product
        self.client.post(reverse('upvote', args=(product.pk,)))
        # make request and assert
        response = self.client.get(reverse('detail', args=(product.pk,)))
        upvote_btn = DetailTests.find_upvote_btn(response.soup)
        self.assertTrue('disabled' in upvote_btn['class'])

    def test_info_message_is_shown_if_user_has_already_voted_on_somebody_s_question(self):
        # signup, create product, logout
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        logout_test_user_with_endpoint(self.client)
        # signup another, get product
        create_test_user_with_endpoint(self.client, username='test_another', password='test_another')
        product = Product.objects.latest('id')
        # vote on that product
        self.client.post(reverse('upvote', args=(product.pk,)))
        # make request and assert
        response = self.client.get(reverse('detail', args=(product.pk,)))
        self.assertContains(response, 'You can vote on the project only once.')

    def test_upvote_button_is_enabled_if_user_has_not_voted_on_somebody_s_question_yet(self):
        # signup, create product, logout
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        logout_test_user_with_endpoint(self.client)
        # signup another, get product, DO NOT VOTE
        create_test_user_with_endpoint(self.client, username='test_another', password='test_another')
        product = Product.objects.latest('id')
        # make request and assert
        response = self.client.get(reverse('detail', args=(product.pk,)))
        upvote_btn = DetailTests.find_upvote_btn(response.soup)
        self.assertTrue('disabled' not in upvote_btn['class'])


class UpvoteTests(TestCase):
    def setUp(self):
        # signup, create product, logout
        create_test_user_with_endpoint(self.client)
        create_test_product_with_endpoint(self.client)
        logout_test_user_with_endpoint(self.client)
        # signup another, get product
        create_test_user_with_endpoint(self.client, username='test_another', password='test_another')
        self.product = Product.objects.latest('id')

    def test_get_method_raises_404(self):
        """
        Upvote raises Http404 if GET method is performed.
        """
        self.client.get(reverse('upvote', args=(self.product.pk,)))
        self.assertRaises(Http404)

    def test_correct_data_increments_votes_total(self):
        """
        If provided data is correct,
        upvote increments product.votes_total
        """
        prev_votes_total = self.product.votes_total
        self.client.post(reverse('upvote', args=(self.product.pk,)))
        self.product = Product.objects.latest('id')
        self.assertEqual(prev_votes_total + 1, self.product.votes_total)

    def test_correct_data_redirects_to_details(self):
        """
        If provided data is correct, the flow is
        redirected to product details page.
        """
        response = self.client.post(reverse('upvote', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], f'/products/{self.product.pk}')

    def test_raises_404_if_hunter_is_current_user(self):
        """
        If product's hunter is current user Http404 is raised.
        """
        # logout current 'another' user
        logout_test_user_with_endpoint(self.client)
        # login user that created the product
        create_test_user_with_endpoint(self.client)
        # make request and assertions
        self.client.post(reverse('upvote', args=(self.product.pk,)))
        self.assertRaises(Http404)

    def test_raises_404_if_user_has_already_voted_on_somebody_s_product(self):
        """
        If user has already voted on the product
        that they don't own and tries to vote again -
        Http404 error is raised.
        """
        self.client.post(reverse('upvote', args=(self.product.pk,)))
        self.client.post(reverse('upvote', args=(self.product.pk,)))
        self.assertRaises(Http404)
