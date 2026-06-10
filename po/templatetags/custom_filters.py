from django import template
from num2words import num2words

register = template.Library()

@register.filter
def indian_number_to_words(value):
    try:
        # Convert to integer or float
        number = float(value)
        # Use num2words with Indian numbering system
        words = num2words(number, lang='en_IN')
        # Capitalize first letter
        return words.capitalize()
    except Exception:
        return value







