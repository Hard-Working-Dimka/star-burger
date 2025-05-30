from geopy.distance import geodesic
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from geocoordapp.models import Place


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.total_price().filter(status='accepted')
    orders_in_progress = Order.objects.total_price().filter(status='in_progress')
    orders_in_delivery = Order.objects.total_price().filter(status='in_delivery')

    items_of_restaurants = RestaurantMenuItem.objects.filter(availability=True)
    restaurants = Restaurant.objects.all()

    for order in orders:
        order.free_restaurants = []
        free_restaurants = []

        for item in order.items.all():
            item.free_restaurants = []
            for restaurant_item in items_of_restaurants:
                if item.product_id == restaurant_item.product_id:
                    item.free_restaurants.append(restaurant_item.restaurant_id)
            free_restaurants.append(item.free_restaurants)

        if free_restaurants:
            common_restaurants = set(free_restaurants[0])
            for free_restaurant in free_restaurants[1:]:
                common_restaurants &= set(free_restaurant)
            common_restaurants = list(common_restaurants)

            for common_restaurant in common_restaurants:
                for restaurant in restaurants:
                    if common_restaurant == restaurant.id:

                        order_place = Place.objects.filter(address=order.address).first()
                        if order_place is None or order_place.lat is None or order_place.lon is None:
                            distance = 'расстояние не определено, '
                            order.free_restaurants.append({restaurant.name: distance})
                            break
                        else:
                            order_address_lon = order_place.lon
                            order_address_lat = order_place.lat

                        restaurant_place = Place.objects.filter(address=restaurant.address).first()
                        if restaurant_place is None or restaurant_place.lat is None or restaurant_place.lon is None:
                            distance = 'расстояние не определено, '
                            order.free_restaurants.append({restaurant.name: distance})
                            break
                        else:
                            restaurant_address_lon = restaurant_place.lon
                            restaurant_address_lat = restaurant_place.lat

                        distance = round(geodesic((order_address_lat, order_address_lon),
                                                  (restaurant_address_lat, restaurant_address_lon)).km, 2)

                        order.free_restaurants.append({restaurant.name: distance})
                        break

        order.free_restaurants = sorted(order.free_restaurants, key=lambda x: (
            0, list(x.values())[0]) if isinstance(list(x.values())[0], (int, float)) else (
            1, str(list(x.values())[0])))

    return render(request, template_name='order_items.html',
                  context={'order_items': orders, 'order_in_progress': orders_in_progress,
                           'order_in_delivery': orders_in_delivery})
