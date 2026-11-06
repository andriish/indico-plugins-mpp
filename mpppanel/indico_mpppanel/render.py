# This file is part of the MPP Indico plugins.
# Copyright (C) 2026 MPP
#
# The MPP Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

from collections import namedtuple
from datetime import datetime
from html import escape

from pytz import timezone

from indico.core.cache import make_scoped_cache
from indico.core.config import config
from indico.core.db import db
from indico.modules.rb.models.reservation_occurrences import ReservationOccurrence
from indico.modules.rb.models.reservations import Reservation, ReservationState
from indico.modules.rb.models.rooms import Room


MAIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body {
      font-family: "Helvetica Neue", Arial, sans-serif;
      background-color: #f5f7fa;
      margin: 0;
      padding: 0;
      color: #333;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    header {
      background-color: #0075a3;
      color: white;
      padding: 15px 30px;
      display: flex;
      align-items: center;
    }
    header img {
      height: 80px;
      margin-right: 15px;
    }
    main {
      flex: 1;
      display: flex;
      min-height: 0;
    }
    iframe {
      flex: 1;
      width: 100%;
      border: none;
      display: block;
    }
    footer {
      background-color: #e0e6ed;
      text-align: center;
      padding: 10px;
      font-size: 28px;
      color: #555;
    }
  </style>
</head>

<body>
  <header>
    <img src="{logo}" alt="" width="400" height="160">
    <span style='font-size:56px; font-weight:bold;'>{near}</span>
  </header>

  <main>
    <iframe id="refreshFrame" src="{frame_file}"></iframe>
  </main>

  <footer>
    Powered by Indico – Max-Planck-Institut für Physik
  </footer>

  <script>
    setInterval(() => {
      const f = document.getElementById('refreshFrame');
      f.src = f.src;
    }, 30000);
  </script>

</body>
</html>
"""

FRAME_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body {
      font-family: "Helvetica Neue", Arial, sans-serif;
      background-color: #f5f7fa;
      margin: 0;
      padding: 0;
      color: #333;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    p {
      font-size: 36px;
      margin: 20px 30px;
    }
    h2 {
      margin: 20px 30px 10px;
      color: #0075a3;
    }
    ul {
      margin: 0 30px 20px;
      font-size: 36px;
    }
    .occupancy-bar {
      display: flex;
      width: 90%;
      height: 40px;
      margin: 0 auto 10px;
      border: 2px solid #555;
      border-radius: 5px;
      overflow: hidden;
    }
    .segment {
      height: 100%;
    }
    .free {
      background-color: transparent;
    }
    .booked {
      background-color: #f44336;
    }
    .time-scale {
      display: flex;
      width: 90%;
      margin: 0 auto 20px;
      font-size: 20px;
      color: #333;
      justify-content: space-between;
    }
    .bottom-bar {
      margin-top: auto;
    }
  </style>
</head>
<body>
"""

FRAME_FOOT = """
</body>
</html>
"""

TIME_SCALE = """
    <div class='time-scale'>
      <span>00:00</span>
      <span>06:00</span>
      <span>12:00</span>
      <span>18:00</span>
      <span>24:00</span>
    </div>
"""

Booking = namedtuple('Booking', 'start_dt end_dt reason booker')

CACHE_TTL = 300  # seconds
_cache = make_scoped_cache('mpppanel')


def _pct(dt):
    return (dt.hour * 60 + dt.minute) / (24 * 60) * 100


def _describe(b):
    return f'{escape(b.reason)} ({b.start_dt:%H:%M}–{b.end_dt:%H:%M}) – booked by {escape(b.booker)}'


def _now():
    return datetime.now(timezone(config.DEFAULT_TIMEZONE)).replace(tzinfo=None, microsecond=0)


def _bookings(room_id, today):
    """Today's accepted bookings of a room, cached for CACHE_TTL seconds."""
    key = f'{room_id}:{today}'
    result = _cache.get(key)
    if result is None:
        occs = (ReservationOccurrence.query
                .join(Reservation)
                .filter(Reservation.room_id == room_id,
                        ReservationOccurrence.is_valid,
                        db.cast(ReservationOccurrence.start_dt, db.Date) == today,
                        Reservation.state == ReservationState.accepted)
                .order_by(ReservationOccurrence.start_dt)
                .distinct()
                .all())
        result = []
        for o in occs:
            res = o.reservation
            booker = res.created_by_user.full_name if res.created_by_user else (res.booked_for_name or '')
            result.append(Booking(o.start_dt, o.end_dt, res.booking_reason or '', booker))
        _cache.set(key, result, CACHE_TTL)
    return result


def get_room(room_id):
    return Room.query.filter(Room.id == room_id, ~Room.is_deleted).first()


def render_main(room, logo):
    return (MAIN_HTML.replace('{near}', escape(room.full_name))
                     .replace('{title}', escape(room.full_name))
                     .replace('{logo}', escape(logo))
                     .replace('{frame_file}', f'{room.id}-frame.html'))


def render_frame(room):
    now = _now()
    today = now.date()
    bookings = _bookings(room.id, today)
    out = [FRAME_HEAD]
    if not bookings:
        out.append('<p>No bookings for today</p>')
    else:
        ongoing = None
        future = []
        for b in bookings:
            if b.start_dt <= now <= b.end_dt:
                ongoing = b
            elif b.start_dt > now:
                future.append(b)
        if ongoing:
            out.append("<p style='font-size:48px; font-weight:bold;'>"
                       f"<span style='color:red;'>Ongoing:</span> {_describe(ongoing)}</p>")
        else:
            out.append("<p style='font-size:48px; font-weight:bold;'>No ongoing booking right now</p>")
        if future:
            out.append('<h2>Upcoming bookings:</h2><ul>')
            out.extend(f'<li>{_describe(b)}</li>' for b in future)
            out.append('</ul>')

    midnight = datetime.combine(today, datetime.min.time())
    segments = []
    last_end = midnight
    for b in bookings:
        if b.start_dt > last_end:
            segments.append((_pct(last_end), _pct(b.start_dt), 'free'))
        segments.append((_pct(b.start_dt), _pct(b.end_dt), 'booked'))
        last_end = max(last_end, b.end_dt)
    if last_end < midnight.replace(hour=23, minute=59):
        segments.append((_pct(last_end), 100, 'free'))

    out.append("<div class='bottom-bar'><div class='occupancy-bar'>")
    out.extend(f"<div class='segment {cls}' style='flex:{end - start};'></div>" for start, end, cls in segments)
    out.append('</div>')
    out.append(TIME_SCALE)
    out.append('</div>')
    out.append(FRAME_FOOT)
    return ''.join(out)
