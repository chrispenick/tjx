from cart import Cart

def test_cart_starts_empty():
    cart = Cart()
    assert cart.total_items() == 0
    assert cart.total_price() == 0.0

def test_add_item_increases_count_and_price():
    cart = Cart()
    cart.add_item("shirt", price=25.0, quantity=2)
    
    assert cart.total_items() == 2
    assert cart.total_price() == 50.0

