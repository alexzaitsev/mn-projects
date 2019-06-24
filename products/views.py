from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import URLValidator
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, ListView

from products.models import Product


class HomeView(ListView):
    PAGE_SIZE = 5

    template_name = 'products/home.html'
    context_object_name = 'products'

    def get_queryset(self):
        page = self.request.GET.get('page')
        queryset = Product.objects.all().order_by('-votes_total', '-pub_date')
        paginator = Paginator(queryset, HomeView.PAGE_SIZE)
        return paginator.get_page(page)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = context['product']
        context['is_author'] = product.hunter.id == self.request.user.id
        return context


@login_required
def upvote(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        if product.hunter.id == request.user.id:
            raise Http404()

        product.votes_total += 1
        product.save()
        return redirect('detail', str(pk))
    else:
        raise Http404()
