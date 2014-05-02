import time
from celery.task import task, periodic_task
from celery.schedules import crontab
from foodapp.models import RiceCooker

@periodic_task(run_every=crontab(hour=0,minute=1,day_of_week=[0,1,2,3,4,5,6]))
def resetRiceCooker():
	cookers = RiceCooker.objects.all()
	for cooker in cookers: 
		cooker.is_on = False
		cooker.save()
	