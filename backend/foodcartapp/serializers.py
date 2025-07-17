from rest_framework.serializers import ModelSerializer

from foodcartapp.models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', ]

    def create(self, validated_data):
        OrderItem.objects.create(
            order_id=validated_data['order_id'],
            product_id=validated_data['product'].id,
            quantity=validated_data['quantity'],
            price=validated_data['product'].price,
        )


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'address', 'phonenumber', 'products', ]

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for product in products:
            product['order_id'] = order.id
            OrderItemSerializer.create(OrderItemSerializer(), validated_data=product)
        return order
