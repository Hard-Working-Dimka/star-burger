from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from requests import RequestException
from django.conf import settings

from restaurateur.auxiliary_funcs import fetch_coordinates
from .models import Product, Order, OrderItem, ProductCategory, Restaurant, RestaurantMenuItem
from geocoordapp.models import Place


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'quantity', 'price']
    readonly_fields = ['price']
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)

    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url,
                           src=obj.image.url)

    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, ]

    def save_model(self, request, obj, form, change):
        if not change:
            address = obj.address

            if not Place.objects.filter(address=address).first():
                try:
                    lat, lon = fetch_coordinates(settings.YANDEX_TOKEN, address)
                except (RequestException, TypeError):
                    lat, lon = None, None
                Place.objects.create(address=address, lat=lat, lon=lon)

        if change and obj.restaurant and obj.status == 'accepted':
            obj.status = 'in_progress'

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.price = instance.product.price
            instance.save()
        formset.save_m2m()

    def response_post_save_change(self, request, obj):
        res = super(OrderAdmin, self).response_post_save_change(request, obj)
        if "next" in request.GET and url_has_allowed_host_and_scheme(url=request.GET['next'],
                                                                     allowed_hosts=request.get_host()):
            return HttpResponseRedirect(request.GET['next'])
        else:
            return res


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', ]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['address', 'lon', 'lat', 'request']
