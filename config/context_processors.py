from django.conf import settings


def stripe_settings(request):
    """Make Stripe settings available in templates."""
    return {
        'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
    }