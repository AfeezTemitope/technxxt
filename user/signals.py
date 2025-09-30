# from decouple import config
# from django.contrib.auth import get_user_model
# from django.db.models.signals import post_migrate
# from django.dispatch import receiver
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# @receiver(post_migrate)
# def create_superuser(sender, **kwargs):
#     if sender.name != "django.contrib.auth":
#         return
#     if config("DJANGO_ENV") != "prod":
#         logger.info("Skipping superuser creation (not production).")
#         return
#     User = get_user_model()
#     username = config("DJANGO_SUPERUSER_USERNAME")
#     email = config("DJANGO_SUPERUSER_EMAIL")
#     password = config("DJANGO_SUPERUSER_PASSWORD")
#
#     if username and email and password:
#         if not User.objects.filter(username=username).exists():
#             User.objects.create_superuser(
#                 username=username,
#                 email=email,
#                 password=password
#             )
#             logger.info(f"✅ Superuser '{username}' created successfully.")
#         else:
#             logger.info(f"ℹ️ Superuser '{username}' already exists.")
#     else:
#         logger.warning("⚠️ Superuser env vars not set, skipping creation.")