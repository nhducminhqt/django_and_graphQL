from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

ALLOWED_STATUS = ["todo", "in_progress", "done"]

def validate_status(status):
    if status not in ALLOWED_STATUS:
        raise ValidationError(f"Invalid status '{status}'. Must be one of {ALLOWED_STATUS}.")

def validate_title(title, max_length=200):
    if len(title) > max_length:
        raise ValidationError(f"Title too long (maximum {max_length} characters).")

def validate_username(username, max_length=150):
    if len(username) > max_length:
        raise ValidationError(f"Username too long (maximum {max_length} characters).")

def validate_password(password, max_length=30):
    if len(password) > max_length:
        raise ValidationError(f"Password too long (maximum {max_length} characters).")

def validate_user_email(email):
    if len(email) > 100:
        raise ValidationError(f"Password too long (maximum {100} characters).")
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError("Invalid email format.")

def validate_user_exists(user_id):
    from django.contrib.auth.models import User
    if not User.objects.filter(pk=user_id).exists():
        raise ValidationError(f"User with ID '{user_id}' does not exist.")
def validate_description(description, max_length=500):
    if len(description) > max_length:
        raise ValidationError(f"Description too long (maximum {max_length} characters).")