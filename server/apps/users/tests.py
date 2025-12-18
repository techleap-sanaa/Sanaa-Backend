import json
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import TenantUser as User 
from .views import ClerkWebhook

class ClerkWebhookTests(APITestCase):
    def setUp(self):
        self.url = "/api/users"  # As defined in urls.py
        self.signing_secret = "test_secret"
        
        # Valid signature headers for mocking
        self.valid_headers = {
            "HTTP_SVIX_ID": "msg_123",
            "HTTP_SVIX_TIMESTAMP": "1234567890",
            "HTTP_SVIX_SIGNATURE": "v1,signature",
        }

        self.user_payload = {
            "type": "user.created",
            "data": {
                "id": "user_123",
                "first_name": "Test",
                "last_name": "User",
                "image_url": "http://example.com/image.jpg",
                "two_factor_enabled": False,
                "created_at": 1672531200000,
                "updated_at": 1672531200000,
                "last_active_at": 1672531200000,
                "email_addresses": [
                    {"id": "email_1", "email_address": "test@example.com"}
                ],
                "primary_email_address_id": "email_1",
                "phone_numbers": [
                    {"id": "phone_1", "phone_number": "+1234567890"}
                ],
                "primary_phone_number_id": "phone_1"
            }
        }

    @patch("apps.users.views.Webhook")
    def test_missing_signature_headers(self, mock_webhook):
        """Test that missing Svix headers results in a bad request (implicitly handled or signature fail)."""
        # If headers are missing, Webhook.verify might fail or code might error. 
        # The view code explicitly gets headers. If they are None, verify likely fails.
        # Let's mock verify to raise exception if headers are bad
        mock_wh_instance = mock_webhook.return_value
        mock_wh_instance.verify.side_effect = Exception("Invalid signature")

        response = self.client.post(self.url, self.user_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid webhook signature")

    @patch("apps.users.views.Webhook")
    def test_invalid_signature(self, mock_webhook):
        """Test that an invalid signature returns a 400 error."""
        mock_wh_instance = mock_webhook.return_value
        mock_wh_instance.verify.side_effect = Exception("Invalid signature")

        response = self.client.post(
            self.url, 
            self.user_payload, 
            format='json', 
            **self.valid_headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.users.views.Webhook")
    def test_invalid_payload_format(self, mock_webhook):
        """Test that a malformed payload returns a 400 error."""
        # Signature verification passes
        mock_wh_instance = mock_webhook.return_value
        mock_wh_instance.verify.return_value = True

        # Malformed format (not matching Schema)
        payload = {"type": "user.created", "data": {"invalid": "structure"}}
        
        response = self.client.post(
            self.url, 
            payload, 
            format='json', 
            **self.valid_headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid payload format")

    @patch("apps.users.views.Webhook")
    def test_user_created_success(self, mock_webhook):
        """Test that a valid user.created event creates a user."""
        mock_wh_instance = mock_webhook.return_value
        mock_wh_instance.verify.return_value = True

        response = self.client.post(
            self.url, 
            self.user_payload, 
            format='json', 
            **self.valid_headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User created")
        
        # Verify DB
        user = User.objects.get(user_id="user_123")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.primary_email, "test@example.com")
        self.assertEqual(user.phone_number, "+1234567890")

    @patch("apps.users.views.Webhook")
    def test_user_updated_success(self, mock_webhook):
        """Test that a valid user.updated event updates an existing user."""
        # Create initial user
        User.objects.create(
            user_id="user_123",
            first_name="Old",
            primary_email="old@example.com"
        )

        mock_wh_instance = mock_webhook.return_value
        mock_wh_instance.verify.return_value = True

        # Change payload to update
        self.user_payload["type"] = "user.updated"
        self.user_payload["data"]["first_name"] = "NewName"

        response = self.client.post(
            self.url, 
            self.user_payload, 
            format='json', 
            **self.valid_headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User updated")
        
        user = User.objects.get(user_id="user_123")
        self.assertEqual(user.first_name, "NewName")

    @patch("apps.users.views.Webhook")
    def test_user_deleted_success(self, mock_webhook):
        """Test that a valid user.deleted event removes the user."""
        User.objects.create(
            user_id="user_123",
            first_name="Test",
            primary_email="test@example.com"
        )
        
        mock_wh_instance = mock_webhook.return_value
        mock_wh_instance.verify.return_value = True

        payload = {
            "type": "user.deleted",
            "data": {
                "id": "user_123",
                "deleted": True
            }
        }

        response = self.client.post(
            self.url, 
            payload, 
            format='json', 
            **self.valid_headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User deleted")
        self.assertFalse(User.objects.filter(user_id="user_123").exists())

    @patch("apps.users.views.Webhook")
    def test_user_deleted_idempotent(self, mock_webhook):
        """Test deleting a non-existent user is successful (idempotent)."""
        mock_wh_instance = mock_webhook.return_value
        mock_wh_instance.verify.return_value = True

        payload = {
            "type": "user.deleted",
            "data": {
                "id": "non_existent_user",
                "deleted": True
            }
        }

        response = self.client.post(
            self.url, 
            payload, 
            format='json', 
            **self.valid_headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User deleted")
