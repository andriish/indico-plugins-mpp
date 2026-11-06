# This file is part of the MPP Indico plugins.
# Copyright (C) 2026 MPP
#
# The MPP Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

from wtforms.fields import StringField
from wtforms.validators import DataRequired

from indico.core.plugins import IndicoPlugin
from indico.web.forms.base import IndicoForm

from indico_mpppanel import _
from indico_mpppanel.blueprint import blueprint


class SettingsForm(IndicoForm):
    logo_url = StringField(_('Logo URL'), [DataRequired()],
                           description=_('URL of the logo shown in the page header.'))


class MPPPanelPlugin(IndicoPlugin):
    """MPP room panel

    Publishes, for every room, a signage page showing today's bookings (ongoing, upcoming, occupancy bar),
    available at /rooms-today/<room id>.html rendered on request (bookings are cached for 5 minutes).
    """

    configurable = True
    settings_form = SettingsForm
    default_settings = {
        'logo_url': '/images/logo_indico_mpp.svg',
    }

    def get_blueprints(self):
        return blueprint
