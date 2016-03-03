__author__ = 'Bohdan Mushkevych'

from flow.execution_context import ExecutionContext, get_logger


class ClusterError(Exception):
    pass


class AbstractCluster(object):
    def __init__(self, name, context, **kwargs):
        assert isinstance(context, ExecutionContext)

        self.name = name
        self.context = context
        self.logger = get_logger(name, context)

        self.kwargs = {} if not kwargs else kwargs

    def run_pig_step(self, uri_script, **kwargs):
        pass

    def run_spark_step(self, uri_script, **kwargs):
        pass

    def run_hadoop_step(self, uri_script, **kwargs):
        pass

    def run_shell_command(self, uri_script, **kwargs):
        pass

    def launch(self):
        pass

    def terminate(self):
        pass