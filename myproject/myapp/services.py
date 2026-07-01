from .models import Order, Cart, CartItem, Watch, ManualPaymentMethod
from django.shortcuts import get_object_or_404

class OrderService:
    @staticmethod
    def create_single_order(user, watch_id, quantity, address, payment_method, online_wallet_id=None, payment_screenshot=None):
        watch = get_object_or_404(Watch, id=watch_id)
        online_wallet = None
        if payment_method == 'Online Payment' and online_wallet_id:
            online_wallet = get_object_or_404(ManualPaymentMethod, id=online_wallet_id)

        order = Order.objects.create(
            user=user,
            watch=watch,
            quantity=quantity,
            address=address,
            payment_method=payment_method,
            online_wallet=online_wallet,
            payment_screenshot=payment_screenshot
        )
        return order

    @staticmethod
    def create_cart_order(user, address, payment_method, online_wallet_id=None, payment_screenshot=None):
        cart = get_object_or_404(Cart, user=user)
        online_wallet = None
        if payment_method == 'Online Payment' and online_wallet_id:
            online_wallet = get_object_or_404(ManualPaymentMethod, id=online_wallet_id)

        for item in cart.items.all():
            Order.objects.create(
                user=user,
                watch=item.watch,
                quantity=item.quantity,
                address=address,
                payment_method=payment_method,
                online_wallet=online_wallet,
                payment_screenshot=payment_screenshot
            )
        cart.items.all().delete()
        return True

class CartService:
    @staticmethod
    def add_item(user, watch_id):
        watch = get_object_or_404(Watch, id=watch_id)
        cart, _ = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, watch=watch)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return cart_item

    @staticmethod
    def remove_item(user, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=user)
        item.delete()

    @staticmethod
    def update_quantity(user, item_id, quantity):
        item = get_object_or_404(CartItem, id=item_id, cart__user=user)
        item.quantity = max(1, int(quantity))
        item.save()
        return item
