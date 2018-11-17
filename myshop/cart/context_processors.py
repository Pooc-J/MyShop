from .cart import Cart


def cart(request):
    return {'mycart': Cart(request)}
