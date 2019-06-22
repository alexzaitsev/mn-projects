from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import DetailView

from products.models import Product


KEY_MESSAGE = 'message'


def home(request):
    params = {}
    if KEY_MESSAGE in request.session and request.session[KEY_MESSAGE]:
        params[KEY_MESSAGE] = request.session[KEY_MESSAGE]
        del request.session[KEY_MESSAGE]
    return render(request, 'products/home.html', params)


@login_required
def create(request):
    if request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']
        url = request.POST['url']
        icon = request.FILES['icon']
        image = request.FILES['image']
        if title and body and url and icon and image:
            url = _decorate_url(url)
            if not _validate_url(url):
                return render(request, 'products/create.html', {'error': 'URL must be valid'})

            product = Product()
            product.title = title
            product.body = body
            product.url = url
            product.icon = icon
            product.image = image
            product.pub_date = timezone.datetime.now()
            product.hunter = request.user
            product.save()
            return redirect('detail', str(product.pk))
        else:
            return render(request, 'products/create.html', {'error': 'All fields are required'})
    else:
        return render(request, 'products/create.html')


def _decorate_url(url):
    return url if url.startswith('http://') or url.startswith('https://')\
        else 'http://' + url


def _validate_url(url):
    try:
        val = URLValidator(schemes=['http', 'https'])
        val(url)
        return True
    except ValidationError:
        return False


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    pk_url_kwarg = 'pk'
