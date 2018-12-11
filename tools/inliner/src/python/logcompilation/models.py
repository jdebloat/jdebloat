from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Log(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def all_terminators(self):
        return InvokeVirtualTerminator.objects.filter(compile_thread__in=self.compilethread_set.all())

class CompileThread(models.Model):
    log = models.ForeignKey(Log, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Klass(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Method(models.Model):
    klass = models.ForeignKey(Klass, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    signature = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.signature

class Callsite(models.Model):
    caller = models.ForeignKey(Method, on_delete=models.CASCADE)
    bci = models.IntegerField()

    def __str__(self):
        return '{}@{}'.format(self.caller, self.bci)

    class Meta:
        unique_together = ('caller', 'bci')

class InlineCall(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    callsite = models.ForeignKey(Callsite, on_delete=models.CASCADE)
    callee = models.ForeignKey(Method, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(str(self.callsite), str(self.callee))

    class Meta:
        unique_together = ('project', 'callsite')
   
class InvokeVirtualTerminator(models.Model):
    compile_thread = models.ForeignKey(CompileThread, on_delete=models.CASCADE)
    callsite = models.ForeignKey(Callsite, on_delete=models.CASCADE)
    tag = models.CharField(max_length=200)
    reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return '{} {} {}{}'.format(self.compile_thread,
                                   self.callsite,
                                   self.tag,
                                   ' [{}]'.format(self.reason) if self.reason != '' else '')
