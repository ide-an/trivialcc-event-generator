from app.models import (
    Event, Circle, Space
)
from app.db import db_session

class CircleImportService:
    def parse_csv(self, import_data):
        pass
    def do_import(self, import_data, event):
        csv = self.parse_csv(import_data)
        # TODO: spaceとcircleを作ってsaveする
        return False
