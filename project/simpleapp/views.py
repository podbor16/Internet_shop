from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db.models import Exists, OuterRef
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product, Subscription, Category
from .filters import ProductFilter


@login_required
def show_protected_page(request):
    pass


class ProductsList(ListView):
    model = Product
    ordering = 'name'
    template_name = 'products.html'
    context_object_name = 'products'
    paginate_by = 2

    # Переопределяем функцию получения списка товаров
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = ProductFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'product'


# Добавляем новое представление для создания товаров.
class ProductCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('simpleapp.add_product',)
    # Указываем нашу разработанную форму
    form_class = ProductForm
    # модель товаров
    model = Product
    # и новый шаблон, в котором используется форма.
    template_name = 'product_edit.html'
    success_url = reverse_lazy('products_list')


# Добавляем представление для изменения товаров.
class ProductUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('simpleapp.change_product',)
    model = Product
    form_class = ProductForm
    template_name = 'product_edit.html'
    success_url = reverse_lazy('product_detail')


# Добавляем представление для удаления товара.
class ProductDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('simpleapp.delete_product',)
    model = Product
    template_name = 'product_delete.html'
    success_url = reverse_lazy('products_list')


@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user, category=category
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk')
            )
        )
    ).order_by('name')

    return render(
        request,
        'post_subscriptions.html',
        {'category': categories_with_subscriptions})


