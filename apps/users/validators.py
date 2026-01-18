from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .utils import calculate_age


def validate_adult_age(birth_date):
    """Valida que la persona sea mayor de 18 años."""
    if calculate_age(birth_date) < 18:
        raise ValidationError(_("Debes tener al menos 18 años para registrarte."))
