import razorpay
import hmac
import hashlib
from django.conf import settings


def get_razorpay_client():
    """
    Returns an authenticated Razorpay client.
    """
    return razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )


def create_razorpay_order(amount, currency='INR', notes={}):
    """
    Create a Razorpay order.
    Amount must be in paise (₹1 = 100 paise).
    Returns the order details.
    """
    client = get_razorpay_client()

    order_data = {
        'amount'   : int(amount * 100),  # convert to paise
        'currency' : currency,
        'notes'    : notes,
        'payment_capture': 1             # auto capture payment
    }

    order = client.order.create(data=order_data)
    return order


def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verify payment signature from Razorpay.
    This ensures payment is authentic and not tampered.
    Returns True if valid, False otherwise.
    """
    try:
        # Generate expected signature
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, razorpay_signature)

    except Exception:
        return False