__author__ = 'Bohdan Mushkevych'

try:
    from http.client import NO_CONTENT
except ImportError:
    from httplib import NO_CONTENT

import json
from synergy.mx.utils import render_template, expose
from werkzeug.wrappers import Response

from flow.mx.flow_action_handler import FlowActionHandler


@expose('/flow/details/step/')
def details_flow_step(request, **values):
    details = FlowActionHandler(request, **values)
    return Response(response=json.dumps(details.step_details), mimetype='application/json')


@expose('/flow/details/flow/')
def details_flow(request, **values):
    details = FlowActionHandler(request, **values)
    return Response(response=json.dumps(details.flow_details), mimetype='application/json')


@expose('/flow/action/recover/')
def action_flow_recover(request, **values):
    handler = FlowActionHandler(request, **values)
    handler.action_recover()
    return Response(status=NO_CONTENT)


@expose('/flow/action/run_one_step/')
def action_run_one_step(request, **values):
    handler = FlowActionHandler(request, **values)
    handler.action_run_one_step()
    return Response(status=NO_CONTENT)


@expose('/flow/action/get_step_log/')
def action_get_step_log(request, **values):
    handler = FlowActionHandler(request, **values)
    return Response(response=json.dumps(handler.action_get_step_log()), mimetype='application/json')


@expose('/viewer/flow/')
def flow_viewer(request, **values):
    details = FlowActionHandler(request, **values)
    return render_template('flow_viewer.html', details=details.flow_details)