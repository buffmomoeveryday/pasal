import stripe

from datetime import datetime
import logging
import uuid

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings


from .models import Customer, Cart, Order, OrderItem, CartItem


@csrf_exempt
def stripe_webhook_payment_success(request):
    if request.method == "POST":
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError as ve:
            logging.error("ValueError: Invalid payload or signature")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as se:
            logging.error("SignatureVerificationError: Invalid signature")
            return HttpResponse(status=400)

        try:
            if event["type"] == "checkout.session.completed":
                process_checkout_session_completed(event)

            elif event["type"] == "payment_intent.succeeded":
                process_payment_intent_succeeded(event)

            elif event["type"] == "payment_intent.payment_failed":
                process_payment_intent_failed(event)

            else:
                logging.info(f"Unhandled Stripe event type: {event['type']}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return HttpResponse(status=500)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)


def process_checkout_session_completed(event):
    """
    Handles successful checkout session completion.

    Args:
        event: The Stripe event object.

    Raises:
        ValueError: If no active cart is found or product stock is insufficient.
    """
    stripe_customer_id = event["data"]["object"]["customer"]
    customer = get_object_or_404(Customer, stripe_id=stripe_customer_id)

    try:
        cart = Cart.objects.filter(cart_customer=customer).first()
        if not cart:
            raise ValueError("No active cart found for this customer")

        order = Order.objects.create(
            tenant=cart.tenant,
            order_customer=customer,
            created_at=datetime.now(),
            order_number=str(uuid.uuid4())[:12],
        )

        move_items_from_cart_to_order(customer, cart, order)

    except ValueError as e:
        logging.error(f"Error processing checkout session: {e}")
        raise


def process_payment_intent_succeeded(event):
    """
    Handles successful payment intent.

    Args:
        event: The Stripe event object.
    """
    intent = event["data"]["object"]
    logging.info(f"Payment intent succeeded: {intent['id']}")


def process_payment_intent_failed(event):
    """
    Handles failed payment intent.

    Args:
        event: The Stripe event object.
    """
    intent = event["data"]["object"]
    error_message = (
        intent["last_payment_error"]["message"]
        if intent.get("last_payment_error")
        else None
    )
    logging.error(f"Payment intent failed: {intent['id']}. Error: {error_message}")


def move_items_from_cart_to_order(customer, cart, order):
    """
    Moves items from the customer's cart to a new order,
    updating product stock and deleting the cart.

    Args:
        customer: The customer object.
        cart: The cart object.
        order: The order object.

    Raises:
        ValueError: If product stock is insufficient.
    """
    for cart_item in cart.items.all():
        product = cart_item.product
        quantity = cart_item.quantity

        if product.stock_quantity < quantity:
            raise ValueError(f"Insufficient stock for product {product.name}")

        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )
        order.items.add(
            order_item
        )  # Add this line to associate the order item with the order

        product.stock_quantity -= quantity
        product.save()
    order.save()  # Save the order after adding items
    cart.delete()  # Corrected from cart.delete to cart.delete()
