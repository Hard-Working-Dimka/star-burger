import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    serialized_order = request.data
    print(serialized_order)
    products = serialized_order.get('products')
    first_name = serialized_order.get('firstname')
    last_name = serialized_order.get('lastname')
    address = serialized_order.get('address')
    phone_number = serialized_order.get('phonenumber')

    order = Order(
        first_name=first_name,
        last_name=last_name,
        address=address,
        phone_number=phone_number,
    )
    order.save()

    for product in products:
        OrderItem.objects.create(
            order_id=order.id,
            product_id=product.get('product'),
            quantity=product.get('quantity'),
        )
    return JsonResponse({})
