from django import template
from django.db.models import Q
from ..models import Message

register = template.Library()

@register.filter
def get_last_message(user, current_user):
    last_message = Message.objects.filter(
        Q(sender=user, receiver=current_user) | Q(sender=current_user, receiver=user)
    ).order_by('-timestamp').first()
    return last_message
