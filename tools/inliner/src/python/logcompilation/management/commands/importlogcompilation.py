from django.core.management.base import BaseCommand, CommandError
from logcompilation.models import Log, CompileThread, Klass, Method, Callsite, InvokeVirtualTerminator, InlineCall, Project

from xml.etree import ElementTree

class Visitor:
    def __init__(self, log):
        self.log = log
        self.project = log.project
        self.current_compile_thread = None
        self.log_klass_lookup = {}
        self.log_method_lookup = {}

    def add_log_klass_entry(self, klass_id, name):
        klass, _ = Klass.objects.get_or_create(name=name)
        self.log_klass_lookup[klass_id] = klass

    def add_log_method_entry(self, method_id, klass_id, name):
        assert klass_id in self.log_klass_lookup
        method, _ = Method.objects.get_or_create(klass=self.log_klass_lookup[klass_id],
                                                 name=name)
        self.log_method_lookup[method_id] = method

    def get_callsite(self, caller_method_id, bci):
        caller = self.log_method_lookup[caller_method_id]
        callsite, _ = Callsite.objects.get_or_create(caller=caller,
                                                     bci=bci)
        return callsite

    def get_inline_call(self, callsite, callee):
        assert callsite is not None
        assert callee is not None
        inline_call, _ = InlineCall.objects.get_or_create(project=self.project,
                                                          caller=callsite,
                                                          callee=callee)
        return inline_call


    def add_terminator(self, callsite, tag, reason=''):
        InvokeVirtualTerminator.objects.create(compile_thread=self.current_compile_thread,
                                               callsite=callsite,
                                               tag=tag,
                                               reason=reason)

    def reset_log_lookups(self):
        self.log_klass_lookup = {}
        self.log_method_lookup = {}

    def visit_klass(self, node):
        assert node.tag == 'klass'
        assert len(node) == 0
        assert node.text is None
        # Contains 'id', 'name', and 'flags'
        self.add_log_klass_entry(int(node.attrib['id']),
                                 node.attrib['name'])

    def visit_method(self, node):
        assert node.tag == 'method'
        assert len(node) == 0
        assert node.text is None
        # Contains 'id', 'holder', 'name', 'return', 'arguments', 'flags', 'bytes',
        # 'compile_id'?, 'compiler'?, 'level'?, 'iicount'
        self.add_log_method_entry(int(node.attrib['id']),
                                  int(node.attrib['holder']),
                                  node.attrib['name'])

    def visit_parse(self, node):
        assert node.tag == 'parse'
        if node.text:
            assert len(node.text.strip()) == 0
    
        # Parse attributes
        assert 'method' in node.attrib
        if len(node.attrib) == 2:
            assert 'stamp' in node.attrib
        if len(node.attrib) == 3:
            assert 'uses' in node.attrib
        if len(node.attrib) == 4:
            assert 'osr_bci' in node.attrib
    
        current_callsite = None
        current_call = None

        for child in node:
            if child.tag == 'assert_null':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'bc':
                assert len(child) == 0
                assert child.text is None
                # Codes:
                # - 182: invokevirtual
                # - 183: invokespecial
                # - 184: invokestatic
                # - 185: invokeinterface
                # - 186: invokedynamic
                if child.attrib['code'] == '182':
                    assert current_callsite is None
                    current_callsite = self.get_callsite(int(node.attrib['method']),
                                                         int(child.attrib['bci']))
                else:
                    if current_callsite:
                        current_callsite = None
                        current_call = None
            elif child.tag == 'branch':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'call':
                assert len(child) == 0
                assert child.text is None
		# sanity check # of calls 
                # multiple calls ?
                # this is the only call before inline success
                # save current call
                # already have the current callsite
                current_call = self.log_method_lookup[int(child.attrib['method'])]
            elif child.tag == 'cast_up':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'dependency':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'direct_call':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'hot_throw':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'inline_fail':
                assert len(child) == 0
                assert child.text is None
                if current_callsite:
                    self.add_terminator(current_callsite, child.tag, child.attrib['reason'])
                    current_callsite = None
                    current_call = None
            elif child.tag == 'inline_level_discount':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'inline_success':
                assert len(child) == 0
                assert child.text is None
                if current_callsite:
                    # is method always called (not none here)
                    # use callsite and call to InlineCall
                    # clear variables every add_terminator
                    # only var should be call
                    self.add_terminator(current_callsite, child.tag, child.attrib['reason'])
                    self.get_inline_call(current_callsite, current_call)
                    current_callsite = None
                    current_call = None
            elif child.tag == 'intrinsic':
                assert len(child) == 0
                assert child.text is None
                if current_callsite:
                    self.add_terminator(current_callsite, child.tag)
                    # clear variables every add_terminator
                    current_callsite = None
                    current_call = None
            elif child.tag == 'klass':
                self.visit_klass(child)
            elif child.tag == 'method':
                self.visit_method(child)
            elif child.tag == 'missed_CHA_opportunity':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'observe':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'parse':
                assert current_callsite is None
                self.visit_parse(child)
            elif child.tag == 'parse_done':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'predicted_call':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'type':
                assert len(child) == 0
                assert child.text is None
            elif child.tag == 'uncommon_trap':
                assert len(child) == 0
                assert child.text is None
                if child.attrib['reason'] in ['uninitialized', 'unloaded']:
                    if current_callsite:
                        self.add_terminator(current_callsite, child.tag, child.attrib['reason'])
                        current_callsite = None
                        current_call = None
                        current_call = None
            elif child.tag == 'virtual_call':
                if current_callsite:
                    self.add_terminator(current_callsite, child.tag)
                    current_callsite = None
                    current_call = None
                assert len(child) == 0
                assert child.text is None
            else:
                assert False, 'unhandled tag %r' % child.tag

    def visit_phase(self, node):
        assert node.tag == 'phase'

        if node.attrib['name'] == 'escapeAnalysis':
            return

        for child in node:
            if child.tag == 'comment':
                pass
            elif child.tag == 'dependency':
                pass
            elif child.tag == 'dependency_failed':
                pass
            elif child.tag == 'eliminate_allocation':
                pass
            elif child.tag == 'eliminate_lock':
                pass
            elif child.tag == 'failure':
                pass
            elif child.tag == 'klass':
                self.visit_klass(child)
            elif child.tag == 'late_inline':
                pass
            elif child.tag == 'loop_tree':
                pass
            elif child.tag == 'method':
                self.visit_method(child)
            elif child.tag == 'parse':
                self.visit_parse(child)
            elif child.tag == 'phase':
                assert node.attrib['name'] in ['buildIR', 'emit_lir', 'optimizer']
                self.visit_phase(child)
            elif child.tag == 'phase_done':
                pass
            elif child.tag == 'regalloc':
                pass
            elif child.tag == 'replace_string_concat':
                pass
            elif child.tag == 'type':
                pass
            elif child.tag == 'uncommon_trap':
                # Warning: this is also in parse
                pass
            else:
                assert False, 'unhandled tag %r' % child.tag

    def visit_task(self, node):
        self.reset_log_lookups()

        assert node.tag == 'task'
        if node.text:
            assert len(node.text.strip()) == 0
        for child in node:
            if child.tag == 'code_cache':
                pass
            elif child.tag == 'dependency':
                pass
            elif child.tag == 'dependency_failed':
                pass
            elif child.tag == 'failure':
                pass
            elif child.tag == 'observe':
                pass
            elif child.tag == 'phase':
                #self.reset_log_lookups()
                self.visit_phase(child)
                #self.reset_log_lookups()
            elif child.tag == 'task_done':
                pass
            else:
                assert False, 'unhandled tag %r' % child.tag

        self.reset_log_lookups()

    def visit_start_compile_thread(self, node):
        assert node.tag == 'start_compile_thread'
        assert len(node) == 0
        assert node.text is None
        self.current_compile_thread = CompileThread(log=self.log, name=node.attrib['name'])
        self.current_compile_thread.save()

    def visit_compilation_log(self, node):
        assert node.tag == 'compilation_log'
        if node.text:
            assert len(node.text.strip()) == 0
        # Compilation logs contain exactly one 'start_compile_thread' node
        # All other nodes are 'task' nodes
        for child in node:
            if child.tag == 'fragment':
                pass
            elif child.tag == 'start_compile_thread':
                self.visit_start_compile_thread(child)
            elif child.tag == 'task':
                self.visit_task(child)
            else:
                assert False, 'unhandled tag %r' % child.tag

    def visit_hotspot_log(self, node):
        assert node.tag == 'hotspot_log'
        if node.text:
            assert len(node.text.strip()) == 0
        for child in node:
            if child.tag == 'compilation_log':
                self.visit_compilation_log(child)
            elif child.tag == 'hotspot_log_done':
                pass
            elif child.tag == 'tty':
                pass
            elif child.tag == 'vm_arguments':
                pass
            elif child.tag == 'vm_version':
                pass
            else:
                assert False, 'unhandled tag %r' % child.tag

class Command(BaseCommand):
    help = 'Import the log compilation file'

    def add_arguments(self, parser):
        parser.add_argument('project')
        parser.add_argument('path')
        parser.add_argument('name')

    def handle(self, *args, **options):
        tree = ElementTree.parse(options['path'])
        root = tree.getroot()
        project, _ = Project.objects.get_or_create(name=options['project'])
        log = Log.objects.create(project=project, name=options['name'])
        visitor = Visitor(log)
        visitor.visit_hotspot_log(root)
