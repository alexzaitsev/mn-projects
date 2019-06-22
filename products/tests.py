from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from products.models import Product


test_image = SimpleUploadedFile('image.png', b'file_content', content_type='image/png')


def create_test_user(client):
    client.post(reverse('signup'), {'username': 'test', 'password1': 'test', 'password2': 'test'})


def create_test_product(client):
    return client.post(reverse('create'),
                       {'title': 'title', 'body': 'body', 'url': 'google.com', 'icon': test_image,
                       'image': test_image})


def logout_test_user(client):
    client.post(reverse('logout'))


class HomeTests(TestCase):
    # def test_home_shows_message_if_session_param_is_provided(self):
    #     self.client.session['message'] = 'test'
    #     self.client.session.save()
    #     response = self.client.get(reverse('home'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'products/home.html')
    #     self.assertContains(response, 'test')

    def test_home_clears_session_message_if_provided(self):
        self.client.session['message'] = 'test'
        self.client.get(reverse('home'))
        self.assertTrue('message' not in self.client.session)

    def test_home_without_params(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/home.html')


class CreateProductTests(TestCase):
    def setUp(self):
        create_test_user(self.client)

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
        create_test_product(self.client)
        last_product = Product.objects.latest('id')
        self.assertEqual(last_product.title, 'title')

    def test_correct_data_redirects_to_details(self):
        """
        If provided data is correct, the flow is
        redirected to product details page.
        """
        response = create_test_product(self.client)
        last_product = Product.objects.latest('id')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], f'/products/{last_product.pk}')


class DetailTests(TestCase):
    def test_upvote_button_is_visible_for_authenticated(self):
        """
        Upvote button is visible only if user is authenticated
        """
        create_test_user(self.client)
        create_test_product(self.client)
        product = Product.objects.latest('id')
        response = self.client.get(reverse('detail', args=(product.pk,)))
        self.assertContains(response, 'Upvote')

    def test_upvote_button_is_not_visible_for_unauthenticated(self):
        """
        Upvote button is not visible if user is not authenticated
        """
        create_test_user(self.client)
        create_test_product(self.client)
        product = Product.objects.latest('id')
        logout_test_user(self.client)
        response = self.client.get(reverse('detail', args=(product.pk,)))
        self.assertNotContains(response, 'Upvote')


class UpvoteTests(TestCase):
    def setUp(self):
        create_test_user(self.client)
        create_test_product(self.client)
        self.product = Product.objects.latest('id')

    def test_get_method_raises_404(self):
        """
        Upvote raises Http404 if GET method is performed
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
