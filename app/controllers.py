from datetime import datetime
from dateutil.tz import gettz
from flask import (
    Blueprint, render_template, request, redirect, current_app, url_for, abort, flash
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField, URLField, DateTimeLocalField, HiddenField, TextAreaField, FloatField
)
from wtforms.validators import (
    DataRequired, URL, Optional
)
from app.models import (
    Event, Circle, Map, MapRegion, Space
)
from app.db import db_session
from app.services import (
    CircleImportService
)
from app.extract_region_service import ExtractRegionService

bp = Blueprint('controllers', __name__)

# TODO: configに置く
TIMEZONE=gettz('Asia/Tokyo')

FLASH_OK = 'ok'
FLASH_NG = 'ng'

@bp.route('/')
def index():
    """
    イベントの新規作成への誘導と、作成済みのイベント一覧を返す
    """
    events = Event.query.order_by(Event.id.asc())
    return render_template('index.html', events=events)

@bp.route('/event/new', methods=('GET', 'POST'))
def event_new():
    """ イベントの新規作成フォーム """
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
                name = form.name.data,
                location = form.location.data,
                site_url = form.site_url.data,
                start_datetime = form.start_datetime.data.replace(tzinfo=TIMEZONE),
                end_datetime = form.end_datetime.data.replace(tzinfo=TIMEZONE),
                )
        try:
            db_session.add(event)
            db_session.commit()
        except:
            db_session.rollback()
        current_app.logger.info(event)
        return redirect(url_for('controllers.event_detail', event_id=event.id))
    return render_template('event/new.html', form=form, timezone=TIMEZONE.tzname(datetime.now()))

@bp.route('/event/detail/<int:event_id>')
def event_detail(event_id):
    """
    イベントの詳細
    イベントの編集やイベントに紐付いた各要素の編集につなぐ
    """
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    maps = Map.query.where(Map.event_id == event_id).order_by(Map.id).all()
    return render_template('event/detail.html', event=event, maps=maps)

@bp.route('/event/<int:event_id>/circle/import', methods=('GET', 'POST'))
def circle_import(event_id):
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    form = CircleImportForm()
    if form.validate_on_submit():
        importer = CircleImportService()
        try:
            importer.do_import(form.import_data.data, event)
            flash('インポートに成功しました', FLASH_OK)
            return redirect(url_for('controllers.circle_list', event_id=event.id))
        except Exception as e: # import失敗の旨を通知する
            flash('インポートが失敗しました:{}'.format(e), FLASH_NG)
            pass
    return render_template('circle/import.html', form=form, event=event)

@bp.route('/event/<int:event_id>/circle/list')
def circle_list(event_id):
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    circles_spaces = Circle.find_by_event(event)
    return render_template('circle/list.html', circles_spaces = circles_spaces, event=event)

@bp.route('/event/<int:event_id>/map/new', methods=('GET', 'POST'))
def map_new(event_id):
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    form = MapForm()
    if form.validate_on_submit():
        # 画像からMapRegion抽出
        try:
            region_extractor = ExtractRegionService()
            regions = region_extractor.extract(form.image_url.data)
            try:
                new_map = Map(
                        name = form.name.data,
                        image_url = form.image_url.data,
                        event_id = event.id,
                        )
                db_session.add(new_map)
                db_session.flush() # mapのid取得のため
                for region in regions:
                    map_region = MapRegion(
                            x = region.x,
                            y = region.y,
                            w = region.w,
                            h = region.h,
                            map_id = new_map.id,
                            )
                    db_session.add(map_region)
                db_session.commit()
                flash('マップ追加が成功しました', FLASH_OK)
                # TODO: 本当はmap_detailに飛ばしたい
                return redirect(url_for('controllers.event_detail', event_id=event.id))
            except Exception as e:
                db_session.rollback()
                flash('マップ追加が失敗しました:{}'.format(e), FLASH_NG)
        except Exception as e:
            flash('マップ追加が失敗しました:{}'.format(e), FLASH_NG)
    return render_template('map/new.html', form=form, event=event)

@bp.route('/event/<int:event_id>/map/<int:map_id>/detail')
def map_detail(event_id, map_id):
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    map_ = Map.query.get(map_id)
    if map_ is None:
        abort(404)
    map_regions = MapRegion.query.where(MapRegion.map_id == map_.id).order_by(MapRegion.id).all()
    circles_spaces = Circle.find_by_event(event)
    return render_template('map/detail.html', map=map_, map_regions=map_regions, event=event, circles_spaces=circles_spaces)

@bp.route('/event/<int:event_id>/map/<int:map_id>/edit_mapping')
def map_edit_mapping(event_id, map_id):
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    map_ = Map.query.get(map_id)
    if map_ is None:
        abort(404)
    map_regions = MapRegion.query.where(MapRegion.map_id == map_.id).order_by(MapRegion.id).all()
    spaces = Space.query.where(Space.event_id == event.id).order_by(Space.id).all()
    return render_template('map/edit_mapping.html', map=map_, map_regions=map_regions, event=event, spaces=spaces)

@bp.route('/event/<int:event_id>/map/<int:map_id>/edit_region')
def map_edit_region(event_id, map_id):
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    map_ = Map.query.get(map_id)
    if map_ is None:
        abort(404)
    map_regions = MapRegion.query.where(MapRegion.map_id == map_.id).order_by(MapRegion.id).all()
    form_new = RegionNewForm(map_id=map_.id)
    form_edit = RegionEditForm(map_id=map_.id)
    return render_template('map/edit_region.html', map=map_, map_regions=map_regions, event=event, form_new=form_new, form_edit=form_edit)

# ajax
@bp.route('/map/<int:map_id>/region/new', methods=['POST'])
def map_region_new(map_id):
    form = RegionNewForm()
    if not form.validate_on_submit():
        return { 'error': form.errors }, 400
    map_region = MapRegion(
            x = form.x.data,
            y = form.y.data,
            w = form.w.data,
            h = form.h.data,
            map_id = form.map_id.data,
            )
    try:
        db_session.add(map_region)
        db_session.commit()
        return map_region.to_json()
    except Exception as e:
        db_session.rollback()
        current_app.logger.error('add map_region failed:{}'.format(e))
        return { 'error': 'add map_region failed:{}'.format(e) }, 500

@bp.route('/map/<int:map_id>/region/<int:region_id>/edit', methods=['POST'])
def map_region_edit(map_id, region_id):
    form = RegionEditForm()
    if not form.validate_on_submit():
        return { 'error': form.errors }, 400

    map_region = MapRegion.query.get(region_id)
    if map_region is None:
        return { 'error': '対象の矩形が見つかりません'}, 404
    try:
        map_region.x = form.x.data
        map_region.y = form.y.data
        map_region.w = form.w.data
        map_region.h = form.h.data
        db_session.commit()
        return map_region.to_json()
    except Exception as e:
        db_session.rollback()
        current_app.logger.error('update map_region failed:{}'.format(e))
        return { 'error': 'update map_region failed:{}'.format(e) }, 500

@bp.route('/region/<int:region_id>/space', methods=['POST'])
def region_to_space_save(region_id):
    form = RegionToSpaceForm()
    if not form.validate_on_submit():
        return { 'error': form.errors }, 400

    map_region = MapRegion.query.get(region_id)
    if map_region is None:
        return { 'error': '対象の矩形が見つかりません'}, 404

    space = Space.query.get(form.space_id.data)
    if space is None:
        return { 'error': '対象のスペースが見つかりません'}, 404

    try:
        map_region.space_id = space.id
        db_session.commit()
        return map_region.to_json()
    except Exception as e:
        db_session.rollback()
        current_app.logger.error('update map_region failed:{}'.format(e))
        return { 'error': 'update map_region failed:{}'.format(e) }, 500

@bp.route('/map/<int:map_id>/region/reset', methods=['DELETE'])
def region_to_space_reset(map_id):
    map_ = Map.query.get(map_id)
    if map_ is None:
        abort(404)
    try:
        regions = MapRegion.query.where(MapRegion.map_id == map_.id).all()
        for r in regions:
            r.space_id = None
        db_session.commit()
        return {}
    except Exception as e:
        db_session.rollback()
        current_app.logger.error('update map_region failed:{}'.format(e))
        return { 'error': 'update map_region failed:{}'.format(e) }, 500

class EventForm(FlaskForm):
    name = StringField('イベント名', validators=[DataRequired()])
    location = StringField('場所', validators=[DataRequired()])
    site_url = URLField('サイトURL', validators=[Optional(), URL()])
    start_datetime = DateTimeLocalField('開始日時', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_datetime = DateTimeLocalField('終了日時', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

class CircleImportForm(FlaskForm):
    import_data = TextAreaField('インポートデータ', validators=[DataRequired()])

class MapForm(FlaskForm):
    name = StringField('マップ名', validators=[DataRequired()])
    image_url = URLField('画像URL', validators=[DataRequired(), URL()])

class RegionNewForm(FlaskForm):
    map_id = HiddenField(validators=[DataRequired()])
    x = FloatField('x', validators=[DataRequired()])
    y = FloatField('y', validators=[DataRequired()])
    w = FloatField('w', validators=[DataRequired()])
    h = FloatField('h', validators=[DataRequired()])

class RegionEditForm(FlaskForm):
    map_id = HiddenField(validators=[DataRequired()])
    region_id = HiddenField(validators=[DataRequired()])
    x = FloatField('x', validators=[DataRequired()])
    y = FloatField('y', validators=[DataRequired()])
    w = FloatField('w', validators=[DataRequired()])
    h = FloatField('h', validators=[DataRequired()])

class RegionToSpaceForm(FlaskForm):
    space_id = HiddenField(validators=[DataRequired()])
