# MPP Room Panel

Serves a signage page for every Indico room, showing the bookings of the
current day (ongoing booking, upcoming bookings and a 24-hour occupancy bar),
intended for displays next to the room.

For a room with ID `<id>` the plugin provides:

- `/rooms-today/<id>.html` - the page to put on the display
- `/rooms-today/<id>-frame.html` - the auto-reloading content frame

Pages are rendered on request. The list of bookings of each room is cached for
5 minutes.

## Configuration

Enable the plugin in `indico.conf` (`PLUGINS = {'mpppanel'}`) and set the logo
URL in the plugin settings.

## Changelog

### 3.3

- Initial release
