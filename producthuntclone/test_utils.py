from django.contrib import auth
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from products.models import Product

test_image = SimpleUploadedFile('image.png', b'file_content', content_type='image/png')


def create_test_user_with_endpoint(client):
    client.post(reverse('signup'), {'username': 'test', 'password1': 'test', 'password2': 'test'})


def create_test_product_with_endpoint(client, title='title', body='body', url='google.com'):
    return client.post(reverse('create'),
                       {'title': title,
                        'body': body,
                        'url': url,
                        'icon': test_image,
                        'image': test_image,
                        })


def create_test_products_in_range(client, number):
    for i in range(number):
        create_test_product(client, title=f'title{i}')


def create_test_product(client, title='title', body='body', url='google.com'):
    return Product.objects.create(title=title,
                                  body=body,
                                  url=url,
                                  icon=test_image,
                                  image=test_image,
                                  pub_date=timezone.datetime.now(),
                                  hunter_id=auth.get_user(client).id)


def logout_test_user_with_endpoint(client):
    client.post(reverse('logout'))
