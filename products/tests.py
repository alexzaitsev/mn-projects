from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from products.models import Product


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
        # create user
        self.client.post(reverse('signup'), {'username': 'test', 'password1': 'test', 'password2': 'test'})
        # upload image
        self.image = SimpleUploadedFile('image.png', b'file_content', content_type='image/png')

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
        self.empty_param_raises_error({'title': '', 'body': '', 'url': '', 'icon': self.image, 'image': self.image})

    def test_empty_body_raises_error(self):
        """
        If `body` parameter is empty, 'products/create.html'
        with `error` parameter should be loaded.
        """
        self.empty_param_raises_error({'title': 'title', 'body': '', 'url': '', 'icon': self.image, 'image': self.image})

    def test_empty_url_raises_error(self):
        """
        If `url` parameter is empty, 'products/create.html'
        with `error` parameter should be loaded.
        """
        self.empty_param_raises_error({'title': 'title', 'body': 'body', 'url': '', 'icon': self.image, 'image': self.image})

    def test_valid_url_without_schema_creates_product(self):
        """
        If `url` is valid but does not contain schema.
        No error is provided to 'products/create.html' page.
        """
        url = 'google.com'
        response = self.client.post(reverse('create'),
                                    {'title': 'title', 'body': 'body', 'url': url, 'icon': self.image, 'image': self.image})
        self.assertEqual(response.status_code, 302)

    def test_malformed_url_raises_error(self):
        """
        If `url` is malformed, 'products/create.html'
        with `error` parameter should be loaded.
        """
        url = 'googlecom'
        response = self.client.post(reverse('create'),
                                    {'title': 'title', 'body': 'body', 'url': url, 'icon': self.image, 'image': self.image})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/create.html')
        self.assertEqual(response.context[-1]['error'], 'URL must be valid')

    def test_correct_data_creates_product_in_database(self):
        """
        If provided data is correct, new product is created
        """
        self.client.post(reverse('create'),
                         {'title': 'title', 'body': 'body', 'url': 'google.com', 'icon': self.image,
                          'image': self.image})
        last_product = Product.objects.latest('id')
        self.assertEqual(last_product.title, 'title')

    def test_correct_data_redirects_to_details(self):
        """
        If provided data is correct, the flow is
        redirected to product details page.
        """
        response = self.client.post(reverse('create'),
                                    {'title': 'title', 'body': 'body', 'url': 'google.com', 'icon': self.image,
                                    'image': self.image})
        last_product = Product.objects.latest('id')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], f'/products/{last_product.pk}')


class DetailTests(TestCase):
    pass
