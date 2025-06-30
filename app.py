from flask import Flask, render_template, request
import sqlite3  # DB担当が使う想定

app = Flask(__name__)

# トップページ
@app.route('/')
def index():
    return render_template('index.html')

# 気分選択ページ
@app.route('/mood')
def mood_select():
    return render_template('mood_select.html')

# 結果ページ（POST対応＋DB処理に繋げる準備あり）
@app.route('/result', methods=['POST'])
def result():
    # フォームから気分を取得
    mood = request.form.get('mood')

    # --- ここからDB連携処理に渡す想定 ---
    cafe_info = get_cafe_recommendation(mood)
    # --- ここまでで、cafe_info におすすめ内容が入るようにしておく ---

    # 結果をテンプレートに渡す（なければ仮のメッセージ）
    if cafe_info:
        message = f"おすすめは『{cafe_info['name']}』です：{cafe_info['description']}"
    else:
        message = "おすすめが見つかりませんでした。"

    return render_template('result.html', message=message)

# エラーページ
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# --- DBアクセス関数（担当者が差し替えやすくする） ---
def get_cafe_recommendation(mood):
    """
    mood（例: 'relax'）に応じておすすめのカフェ情報を返す。
    将来的にDBと連携する関数。
    """
    # --- 仮のデータ（DBができるまでのダミー） ---
    sample_data = {
        'relax': {'name': 'カフェしずく', 'description': '静かな空間でゆったりと過ごせます。'},
        'focus': {'name': 'カフェ・ステディ', 'description': '集中にぴったりな静音＆Wi-Fi完備。'},
        'chat': {'name': 'カフェトーク', 'description': '会話OKのカジュアルな雰囲気。'},
        'change': {'name': 'ブレンドラボ', 'description': 'ちょっと変わった体験型コーヒー。'}
    }

    return sample_data.get(mood, None)

if __name__ == '__main__':
    app.run(debug=True)
