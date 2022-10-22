from odoo.addons.bus.controllers.main import BusController
from odoo.http import request


class BusSaleManagement(BusController):
    def _poll(self, dbname, channels, last, options):
        channels = list(channels)
        channels.append((request.session.db, 'new_so'))
        channels.append((request.session.db, 'new_user'))
        return super()._poll(dbname, channels, last, options)
