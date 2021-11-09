from flask import Blueprint

bp = Blueprint('controllers', __name__)

@bp.route('/')
def index():
    """
    イベントの新規作成への誘導と、作成済みのイベント一覧を返す
    """
    return '<p>top page</p>'

@bp.route('/event/new')
def event_new():
    """
    イベントの新規作成フォーム
    """
    return '<p>event new</p>'

@bp.route('/event/detail/<int:event_id>')
def event_detail(event_id):
    """
    イベントの詳細
    イベントの編集やイベントに紐付いた各要素の編集につなぐ
    """
    return '<p>event detail for {}</p>'.format(event_id)
