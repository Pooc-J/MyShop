from decimal import Decimal
from django.conf import settings

from shop.models import Product


class Cart(object):
    def __init__(self, request):
        """
        初始化购物车
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # 空购物车
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        添加产品到购物车或者更新产品数量
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # 更新购物车 session
        self.session[settings.CART_SESSION_ID] = self.cart
        # 标记 session 为"已修改"，以确认已保存
        self.session.modified = True

    def remove(self, product):
        """
        清空购物车
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        迭代购物车里面的产品，并从数据库中获取产品
        """
        product_ids = self.cart.keys()
        # 获取产品对象，并添加到购物车中
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        计算购物车商品数量
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        计算所有商品价格
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # 清空购物车
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True