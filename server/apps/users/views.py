import json
import logging
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config
from svix.webhooks import Webhook, WebhookVerificationError
from .schemas import ClerkWebhookEvent
from .models import TenantUser


logger = logging.getLogger(__name__)
SIGNING_SECRET = config("WEBHOOK_SIGNING_SECRET")


def ok(message: str):
    """Return a standard success DRF response."""
    return Response({"message": message}, status=200)


def bad(message: str, code=400):
    """Return a standard error DRF response."""
    return Response({"error": message}, status=code)


@method_decorator(csrf_exempt, name="dispatch")
class ClerkWebhook(APIView):
    """
    Webhook endpoint for handling Clerk user events.

    This view handles user lifecycle events sent by Clerk and synchronizes them
    with the local database. Supported events:

        - user.created: Creates a new user record.
        - user.updated: Updates an existing user record.
        - user.deleted: Deletes a user record.

    Security:
        - Validates webhook signature using Svix.
        - Uses Pydantic for strict payload validation and type safety.
        - All database operations are atomic to ensure consistency.

    Usage:
        POST requests with JSON payload from Clerk containing event type and user data.
    """

    def post(self, request):
        """
        Handle incoming POST requests from Clerk.

        Steps:
            1. Validate Svix webhook signature.
            2. Parse and validate the JSON payload using Pydantic.
            3. Route the event to the appropriate handler (create/update/delete).

        Returns:
            DRF Response with status message.
        """
        # 1. Validate Svix Signature
        svix_headers = {
            "svix-id": request.headers.get("svix-id"),
            "svix-timestamp": request.headers.get("svix-timestamp"),
            "svix-signature": request.headers.get("svix-signature"),
        }

        try:
            wh = Webhook(SIGNING_SECRET)
            wh.verify(request.body, svix_headers)
        except Exception:
            return bad("Invalid webhook signature")

        # 2. Parse + validate payload using Pydantic
        try:
            payload = json.loads(request.body)
            event = ClerkWebhookEvent.model_validate(payload)
        except Exception as e:
            logger.error(f"[Webhook] Invalid Clerk payload: {e}")
            return bad("Invalid payload format")

        user_data = event.data

        # 3. Route event
        if event.type in ("user.created", "user.updated"):
            return self.sync_user(user_data)

        if event.type == "user.deleted":
            return self.delete_user(user_data.id)

        return ok("Event ignored")

    @transaction.atomic
    def sync_user(self, user):
        """
        Create or update a user in the database.

        Args:
            user (ClerkUser): Pydantic model containing user data from Clerk.

        Returns:
            DRF Response indicating whether the user was created or updated.

        Notes:
            - Resolves primary email and phone numbers.
            - Handles missing fields with safe defaults.
            - Uses atomic transaction to prevent partial updates.
        """
        # Resolve primary email
        primary_email = None
        if user.email_addresses:
            primary_email = next(
                (e.email_address for e in user.email_addresses if e.id == user.primary_email_address_id),
                user.email_addresses[0].email_address
            )

        # Resolve primary phone
        primary_phone = None
        if user.phone_numbers:
            primary_phone = next(
                (p.phone_number for p in user.phone_numbers if p.id == user.primary_phone_number_id),
                user.phone_numbers[0].phone_number
            )

        obj, created = TenantUser.objects.update_or_create(
            user_id=user.id,
            defaults={
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "primary_email": primary_email or "",
                "phone_number": primary_phone or "",
                "profile_image": user.image_url or "",
                "two_factor_enabled": user.two_factor_enabled or False,
                "is_signedin": True,
                "created_at": user.created_at or "",
                "updated_at": user.updated_at or "",
                "last_active_at": user.last_active_at or "",
            }
        )

        return ok("User created" if created else "User updated")

    def delete_user(self, user_id):
        """
        Delete a user from the database.

        Args:
            user_id (str): Clerk user ID to delete.

        Returns:
            DRF Response indicating whether the user was deleted or already absent.

        Notes:
            - Operation is idempotent: deleting a non-existent user is safe.
        """
        deleted, _ = TenantUser.objects.filter(user_id=user_id).delete()
        return ok("User deleted")
