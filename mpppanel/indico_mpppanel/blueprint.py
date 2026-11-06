# This file is part of the MPP Indico plugins.
# Copyright (C) 2026 MPP
#
# The MPP Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

from flask import make_response
from werkzeug.exceptions import NotFound

from indico.core.plugins import IndicoPluginBlueprint

from indico_mpppanel.render import get_room, render_frame, render_main


blueprint = IndicoPluginBlueprint('mpppanel', __name__, url_prefix='/rooms-today')


def _respond(html):
    resp = make_response(html)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


def _room_or_404(room_id):
    room = get_room(room_id)
    if room is None:
        raise NotFound
    return room


@blueprint.route('/<int:room_id>.html')
def room_today(room_id):
    from indico_mpppanel.plugin import MPPPanelPlugin
    return _respond(render_main(_room_or_404(room_id), MPPPanelPlugin.settings.get('logo_url')))


@blueprint.route('/<int:room_id>-frame.html')
def room_today_frame(room_id):
    return _respond(render_frame(_room_or_404(room_id)))
