import stripe
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Deletes all connected Stripe accounts"

    def handle(self, *args, **kwargs):
        # Set your secret key
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Refund all charges and PaymentIntents and delete all customers
            self.refund_charges_and_payment_intents_and_delete_customers()

            # Delete all connected Stripe accounts
            self.delete_connected_accounts()

        except stripe.error.StripeError as e:
            # Display any errors that occur during the process
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def refund_charges_and_payment_intents_and_delete_customers(self):
        # Refund all charges
        charges = stripe.Charge.list(limit=100)
        for charge in charges:
            try:
                if not charge.refunded:
                    refund = stripe.Refund.create(charge=charge.id)
                    self.stdout.write(
                        self.style.SUCCESS(f"Charge {charge.id} refunded successfully")
                    )
            except stripe.error.InvalidRequestError:
                self.stdout.write(
                    self.style.WARNING(f"Charge {charge.id} could not be refunded or has already been refunded")
                )

        # Refund all PaymentIntents
        payment_intents = stripe.PaymentIntent.list(limit=100)
        for payment_intent in payment_intents:
            try:
                if hasattr(payment_intent, 'charges') and payment_intent.charges:
                    charge_id = payment_intent.charges.data[0].id
                    if not payment_intent.charges.data[0].refunded:
                        refund = stripe.Refund.create(charge=charge_id)
                        self.stdout.write(
                            self.style.SUCCESS(f"PaymentIntent {payment_intent.id} refunded successfully")
                        )
            except stripe.error.InvalidRequestError:
                self.stdout.write(
                    self.style.WARNING(f"PaymentIntent {payment_intent.id} could not be refunded or has already been refunded")
                )

        # Delete all customers
        customers = stripe.Customer.list(limit=100)
        for customer in customers:
            stripe.Customer.delete(customer.id)
            self.stdout.write(
                self.style.SUCCESS(f"Customer {customer.id} deleted successfully")
            )

    def delete_connected_accounts(self):
        connected_accounts = stripe.Account.list(limit=100)
        for account in connected_accounts:
            stripe.Account.delete(account.id)
            self.stdout.write(
                self.style.SUCCESS(f"Account {account.id} deleted successfully")
            )

        self.stdout.write(
            self.style.SUCCESS("All connected accounts deleted successfully")
        )
