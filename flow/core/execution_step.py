__author__ = 'Bohdan Mushkevych'

from flow.core.abstract_action import AbstractAction
from flow.core.execution_context import ContextDriven


def validate_action_param(param, klass):
    assert isinstance(param, (tuple, list)), \
        'Expected list of {0} or an empty list. Instead got {1}'.format(klass.__name__, param.__class__.__name__)
    assert all(isinstance(p, klass) for p in param), \
        'Expected list of {0}. Not all elements of the list were of this type'.format(klass.__name__)


class ExecutionStep(ContextDriven):
    """ helper class for the GraphNode, keeping the track of completed actions
        and providing means to run the step """
    def __init__(self, name, main_action, pre_actions=None, post_actions=None, **kwargs):
        super(ExecutionStep, self).__init__()

        if pre_actions is None: pre_actions = []
        if post_actions is None: post_actions = []
        if kwargs is None: kwargs = {}

        self.name = name
        self.main_action = main_action

        self.is_pre_completed = False
        self.is_main_completed = False
        self.is_post_completed = False

        self.pre_actions = pre_actions
        validate_action_param(self.pre_actions, AbstractAction)

        self.post_actions = post_actions
        validate_action_param(self.post_actions, AbstractAction)

        self.kwargs = kwargs

    @property
    def is_complete(self):
        return self.is_pre_completed and self.is_main_completed and self.is_post_completed

    def _do(self, actions, execution_cluster):
        assert self.is_context_set is True
        is_success = True
        for action in actions:
            try:
                action.do(self.context, execution_cluster)
            except Exception as e:
                is_success = False
                self.logger.error('Execution Error: {0}'.format(e), exc_info=True)
                break
            finally:
                action.cleanup()
        return is_success

    def do_pre(self, execution_cluster):
        self.is_pre_completed = self._do(self.pre_actions, execution_cluster)
        return self.is_pre_completed

    def do_main(self, execution_cluster):
        self.is_main_completed = self._do([self.main_action], execution_cluster)
        return self.is_main_completed

    def do_post(self, execution_cluster):
        self.is_post_completed = self._do(self.post_actions, execution_cluster)
        return self.is_post_completed
