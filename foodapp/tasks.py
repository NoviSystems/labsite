
from celery import shared_task
from foodapp.models import RiceCooker


@shared_task
def reset_rice_cooker():
    cookers = RiceCooker.objects.all()
    for cooker in cookers:
        cooker.is_on = False
        cooker.save()
