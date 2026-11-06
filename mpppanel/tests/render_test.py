# This file is part of the MPP Indico plugins.
# Copyright (C) 2026 MPP
#
# The MPP Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

from datetime import datetime

from indico_mpppanel.render import Booking, _describe, _pct


def test_pct():
    assert _pct(datetime(2026, 1, 1, 0, 0)) == 0
    assert _pct(datetime(2026, 1, 1, 12, 0)) == 50


def test_describe_escapes_html():
    b = Booking(datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 10, 30), '<b>Talk</b>', 'A & B')
    assert _describe(b) == '&lt;b&gt;Talk&lt;/b&gt; (09:00–10:30) – booked by A &amp; B'
