from django.shortcuts import get_object_or_404, render
from django.db.models import Count

from .models import Log

def index(request):
    context = {'title': 'Log Compilation', 'logs': Log.objects.order_by('-date')}
    return render(request, 'logcompilation/index.html', context)

def detail(request, log_id):
    log = get_object_or_404(Log, pk=log_id)
    tag_entries = log.all_terminators().values('tag').distinct().annotate(count=Count('tag')).order_by('-count')
    reason_entries = log.all_terminators().values('tag', 'reason').distinct().annotate(count=Count('reason')).order_by('-count')
    context = {'title': log.name,
               'log': log,
               'tag_entries': tag_entries,
               'reason_entries': reason_entries}
    return render(request, 'logcompilation/detail.html', context)
