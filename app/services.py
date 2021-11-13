from collections import namedtuple
import csv
import io
from app.models import (
    Event, Circle, Space
)
from app.db import db_session
from flask import current_app
import validators

# サークルインポートのフォーマットは下記の通り
# "あ22ab","baba精米所","baba","http://www.pixiv.net/member.php?id=3422465","https://www.pixiv.net/users/3422465","https://twitter.com/baba15207048"
CircleImportRow = namedtuple('CircleImportRow', ['space_name','circle_name','penname','site_url','pixiv','twitter'])
class CircleImportService:
    def parse_csv(self, import_data):
        return list(map(CircleImportRow._make, csv.reader(io.StringIO(import_data))))

    def validate_row(self, row):
        def not_valid_url(v):
            return v is not None and v != ''  and not validators.url(v)
        # とりあえずURLのフォーマットだけ見ておく
        if not_valid_url(row.site_url):
            current_app.logger.info("if not_valid_url(row.site_url):")
            return False
        if not_valid_url(row.pixiv):
            current_app.logger.info("if not_valid_url(row.pixiv):")
            return False
        if not_valid_url(row.twitter):
            current_app.logger.info("if not_valid_url(row.twitter):")
            return False
        return True

    def do_import(self, import_data, event):
        try:
            csv = self.parse_csv(import_data)
        except Exception as e:
            current_app.logger.warning('do_import parse_csv failed:{}'.format(e))
            raise Exception('CSVのパースに失敗しました')
        # spaceとcircleを作ってsaveする
        current_app.logger.info('csv:{}'.format(csv))
        try:
            for row in csv:
                if not self.validate_row(row):
                    raise Exception('不正な行:{}'.format(row))
                space = Space(name=row.space_name, event_id=event.id)
                db_session.add(space)
                db_session.flush() # spaceのidを取得するため
                circle = Circle(
                        name=row.circle_name,
                        penname=row.penname,
                        site_url=row.site_url,
                        pixiv=row.pixiv,
                        twitter=row.twitter,
                        event_id=event.id,
                        space_id=space.id
                        )
                db_session.add(circle)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise Exception('DBへの保存に失敗しました:{}'.format(e))
