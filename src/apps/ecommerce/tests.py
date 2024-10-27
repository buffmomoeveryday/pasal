
import unittest
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Customer, ProductCategory, Products, CartItem, Cart, OrderItem, Order

class CustomerTestCase(TestCase):
    def test_create_customer(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="password",
            mobile_number="1234567890",
            address="123 Main St",
        )
        self.assertEqual(Customer.objects.count(), 1)

    def test_duplicate_email(self):
        Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="password",
            mobile_number="1234567890",
            address="123 Main St",
        )
        with self.assertRaises(ValidationError):
            Customer.objects.create(
                first_name="Jane",
                last_name="Doe",
                email="john@example.com",  # Same email as previous customer
                password="password",
                mobile_number="1234567890",
                address="123 Main St",
            )

class ProductCategoryTestCase(TestCase):
    def test_create_product_category(self):
        category = ProductCategory.objects.create(name="Electronics")
        self.assertEqual(ProductCategory.objects.count(), 1)

class ProductsTestCase(TestCase):
    def test_create_product(self):
        category = ProductCategory.objects.create(name="Electronics")
        product = Products.objects.create(
            name="Laptop",
            price=999.99,
            cost_price=799.99,
            discount=100.00,
            stock_quantity=10,
            description="A high-quality laptop.",
        )
        product.category.add(category)
        self.assertEqual(Products.objects.count(), 1)

class CartItemTestCase(TestCase):
    def test_create_cart_item(self):
        product = Products.objects.create(
            name="Laptop",
            price=999.99,
            cost_price=799.99,
            discount=100.00,
            stock_quantity=10,
            description="A high-quality laptop.",
        )
        cart_item = CartItem.objects.create(product=product, quantity=2)
        self.assertEqual(CartItem.objects.count(), 1)

class CartTestCase(TestCase):
    def test_create_cart(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="password",
            mobile_number="1234567890",
            address="123 Main St",
        )
        cart = Cart.objects.create(cart_customer=customer)
        self.assertEqual(Cart.objects.count(), 1)

class OrderItemTestCase(TestCase):
    def test_create_order_item(self):
        product = Products.objects.create(
            name="Laptop",
            price=999.99,
            cost_price=799.99,
            discount=100.00,
            stock_quantity=10,
            description="A high-quality laptop.",
        )
        order_item = OrderItem.objects.create(product=product, quantity=2, price=999.99)
        self.assertEqual(OrderItem.objects.count(), 1)

class OrderTestCase(TestCase):
    def test_create_order(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="password",
            mobile_number="1234567890",
            address="123 Main St",
        )
        order = Order.objects.create(order_customer=customer, order_number="123")
        self.assertEqual(Order.objects.count(), 1)

if __name__ == '__main__':
    unittest.main()

