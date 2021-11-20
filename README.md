# trivialcc-event-generator

## What's This?

trivialcc-event-generator はtrivial-circlecheckに登録するイベントデータを作成するツールです。

## How to Run?

```bash
# venv
python -m venv env
. env/Scripts/activate

# install packages
pip install < requirements.txt

# run flask
flask run

# access http://127.0.0.1:5000/
```

## How to Use?

大まかな流れとしては以下の通り

 1. イベントを新規作成
 2. 作成したイベントにサークルを一括追加
 3. マップの画像分だけマップを追加
 4. 各マップを編集
    1. 認識してない矩形があったら矩形の編集で追加
    2. 矩形とスペースとのマッピングを行う
    3. マッピングが正しいかどうかマップ詳細で確認
 5. 最後にイベントをエクスポートするとtirivial-circlecheckで取り込める形のデータがダウンロードできる
