from datetime import datetime
from dateutil.tz import gettz
from flask import (
    Blueprint, render_template, request, redirect, current_app, url_for, abort
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField, URLField, DateTimeLocalField
)
from wtforms.validators import (
    DataRequired, URL, Optional
)
from app.models import (
    Event
)
from app.db import db_session

bp = Blueprint('controllers', __name__)

# TODO: configに置く
TIMEZONE=gettz('Asia/Tokyo')

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
        with db_session.begin():
            db_session.add(event)
            db_session.commit()
        current_app.logger.info(event)
        return redirect(url_for('controllers.event_detail', event_id=event.id))
    return render_template('event/new.html', form=form, timezone=TIMEZONE.tzname(datetime.now()))

@bp.route('/event/detail/<int:event_id>')
def event_detail(event_id):
    """
    イベントの詳細
    イベントの編集やイベントに紐付いた各要素の編集につなぐ
    """
    event = Event.query.where(Event.id == event_id).first()
    if event is None:
        abort(404)
    return render_template('event/detail.html', event=event)

class EventForm(FlaskForm):
    name = StringField('イベント名', validators=[DataRequired()])
    location = StringField('場所', validators=[DataRequired()])
    site_url = URLField('サイトURL', validators=[Optional(), URL()])
    start_datetime = DateTimeLocalField('開始日時', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_datetime = DateTimeLocalField('終了日時', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
