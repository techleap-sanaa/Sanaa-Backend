from typing import List, Optional, Union
from pydantic import BaseModel, field_validator
from datetime import datetime


def to_iso(value):
    """
    Convert Clerk's millisecond timestamps or strings to ISO 8601 string.

    Args:
        value (int | str | None): The timestamp to convert.
            - int: milliseconds since epoch
            - str: already a string timestamp
            - None: returns None

    Returns:
        str | None: ISO 8601 formatted string or None if input is None
    """
    if value is None:
        return None
    if isinstance(value, int):
        return datetime.utcfromtimestamp(value / 1000).isoformat()
    return str(value)


class ClerkEmail(BaseModel):
    """
    Represents an email object from Clerk user data.

    Attributes:
        id (str): Unique ID of the email in Clerk.
        email_address (str): The email address string.
    """
    id: str
    email_address: str


class ClerkPhone(BaseModel):
    """
    Represents a phone object from Clerk user data.

    Attributes:
        id (str): Unique ID of the phone number in Clerk.
        phone_number (str): The phone number string.
    """
    id: str
    phone_number: str


class ClerkUser(BaseModel):
    """
    Represents a user object from Clerk webhook data.

    Attributes:
        id (str): Clerk's user ID.
        first_name (str, optional): User's first name. Defaults to "".
        last_name (str, optional): User's last name. Defaults to "".
        image_url (str, optional): URL of the user's profile image. Defaults to "".
        two_factor_enabled (bool, optional): Whether 2FA is enabled. Defaults to False.
        created_at (int | str, optional): Timestamp of user creation (ms or string).
        updated_at (int | str, optional): Timestamp of last update (ms or string).
        last_active_at (int | str, optional): Timestamp of last activity (ms or string).
        email_addresses (List[ClerkEmail]): List of user's email objects.
        primary_email_address_id (str, optional): ID of the primary email.
        phone_numbers (List[ClerkPhone]): List of user's phone objects.
        primary_phone_number_id (str, optional): ID of the primary phone.
    """
    id: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    image_url: Optional[str] = ""
    two_factor_enabled: Optional[bool] = False

    created_at: Optional[Union[int, str]] = None
    updated_at: Optional[Union[int, str]] = None
    last_active_at: Optional[Union[int, str]] = None

    email_addresses: List[ClerkEmail] = []
    primary_email_address_id: Optional[str] = None

    phone_numbers: List[ClerkPhone] = []
    primary_phone_number_id: Optional[str] = None

    @field_validator("created_at", "updated_at", "last_active_at", mode="before")
    def convert_timestamps(cls, value):
        """
        Convert integer timestamps (milliseconds) from Clerk to ISO strings.

        Args:
            value (int | str | None): Timestamp value

        Returns:
            str | None: ISO formatted timestamp
        """
        return to_iso(value)


class ClerkWebhookEvent(BaseModel):
    """
    Represents a Clerk webhook event.

    Attributes:
        type (str): The event type (e.g., "user.created", "user.updated", "user.deleted").
        data (ClerkUser): The user data payload associated with the event.
    """
    type: str
    data: ClerkUser
