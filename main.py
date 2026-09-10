import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

stripe_public_key = os.getenv("STRIPE_PUBLIC_KEY")
stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")