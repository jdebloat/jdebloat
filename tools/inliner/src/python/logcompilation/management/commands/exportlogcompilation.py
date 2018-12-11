from django.core.management.base import BaseCommand, CommandError
from logcompilation.models import Log, CompileThread, Klass, Method, Callsite, InvokeVirtualTerminator, InlineCall, Project

class Command(BaseCommand):
    help = 'Import the log compilation file'

    def add_arguments(self, parser):
        parser.add_argument('project')
        parser.add_argument('out_file')

    def handle(self, *args, **options):
        project, _ = Project.objects.get_or_create(name=options['project'])
        with open(options['out_file'], 'w') as f:
            for inline_call in InlineCall.objects.filter(project=project):
                f.write(str(inline_call))
                f.write('\n')
