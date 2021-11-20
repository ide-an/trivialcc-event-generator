from collections import namedtuple
import csv
import io
from app.models import (
    Event, Circle, Space, Map, MapRegion
)
from app.db import db_session
from sqlalchemy import select
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

class EventExportService:
    def yaml_event(self, event):
        # タイムゾーンは+09決め打ち
        return f"""
- &event{event.id} !!models.Event
  name: "{event.name}"
  location: "{event.location}"
  startAt: "{event.start_datetime.strftime('%Y-%m-%d %H:%M:%S+09')}"
  endAt: "{event.end_datetime.strftime('%Y-%m-%d %H:%M:%S+09')}"
  url: "{event.site_url}"
"""

    def yaml_circle(self, circle, event):
        return f"""
- &circle{circle.id} !!models.Circle
  name: "{circle.name}"
  penName: "{circle.penname}"
  url: "{circle.site_url}"
  pixivUrl: "{circle.pixiv}"
  twitterUrl: "{circle.twitter}"
  event: *event{event.id}
"""

    def yaml_space(self, space, circle, event):
        return f"""
- &space{space.id} !!models.Space
  name: "{space.name}"
  event: *event{event.id}
  circle: *circle{circle.id}
"""

    def yaml_map(self, map_, event):
        return f"""
- &map{map_.id} !!models.Map
  name: "{map_.name}"
  imageFile: "{map_.image_url}"
  event: *event{event.id}
"""

    def yaml_map_region(self, map_region, space, map_):
        return f"""
- &mapEntry{map_region.id} !!models.MapEntry
  x: {map_region.x}
  y: {map_region.y}
  width: {map_region.w}
  height: {map_region.h}
  space: *space{space.id}
  map: *map{map_.id}
"""

    def do_export(self, event):
        """
        イベント情報をyamlに変換する
        """
        yaml = ''
        yaml += self.yaml_event(event)
        yaml_circles = ''
        yaml_spaces = ''
        circles_spaces = Circle.find_by_event(event)
        for circle, space in circles_spaces:
            yaml_circles += self.yaml_circle(circle, event)
            yaml_spaces += self.yaml_space(space, circle, event)
        yaml += yaml_circles
        yaml += yaml_spaces
        maps = Map.query.where(Map.event_id == event.id).order_by(Map.id).all()
        for map_ in maps:
            yaml += self.yaml_map(map_, event)
        for map_ in maps:
            regions_spaces = db_session.execute(
                    select(MapRegion, Space)
                    .where(MapRegion.space_id == Space.id)
                    .where(MapRegion.map_id == map_.id)
                    .order_by(MapRegion.id)).all()
            current_app.logger.info(len(regions_spaces))
            for region, space in regions_spaces:
                yaml += self.yaml_map_region(region, space, map_)
        return yaml
