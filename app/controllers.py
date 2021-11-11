from flask import (
    Blueprint, render_template, request, redirect, current_app, url_for
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField, URLField, DateTimeLocalField
)
from wtforms.validators import (
    DataRequired, URL, Optional
)
from .models import (
    Event
)


bp = Blueprint('controllers', __name__)

@bp.route('/')
def index():
    """
    イベントの新規作成への誘導と、作成済みのイベント一覧を返す
    """
    events = [
        Event(id=1, name='秋季例大祭'),
        Event(id=2, name='紅楼夢'),
    ]
    return render_template('index.html', events=events)

@bp.route('/event/new', methods=('GET', 'POST'))
def event_new():
    """ イベントの新規作成フォーム """
    form = EventForm()
    if form.validate_on_submit():
        # TODO: implement
        # new Event object
        return redirect(url_for('controllers.event_detail', event_id=1))
    return render_template('event/new.html', form=form)

@bp.route('/event/detail/<int:event_id>')
def event_detail(event_id):
    """
    イベントの詳細
    イベントの編集やイベントに紐付いた各要素の編集につなぐ
    """
    return '<p>event detail for {}</p>'.format(event_id)

class EventForm(FlaskForm):
    name = StringField('イベント名', validators=[DataRequired()])
    location = StringField('場所', validators=[DataRequired()])
    site_url = URLField('サイトURL', validators=[Optional(), URL()])
    start_datetime = DateTimeLocalField('開始日時', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_datetime = DateTimeLocalField('終了日時', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
