from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# トップページ
@app.route('/')
def index():
    return render_template('index.html')

# 気分選択ページ
@app.route('/mood')
def mood_select():
    return render_template('mood_select.html')

# 結果ページ（POST対応）
@app.route('/result', methods=['POST'])
def result():
    # フォームから全ての回答を取得
    taste = request.form.get('taste')
    feeling = request.form.get('feeling')
    activity = request.form.get('activity')
    time = request.form.get('time')

    answers = {
        "taste": taste,
        "feeling": feeling,
        "activity": activity,
        "time": time
    }

    # DBからおすすめを取得
    cafe_info = get_cafe_recommendation(answers)

    if cafe_info:
        message = f"おすすめは『{cafe_info['name']}』です！<br>住所：{cafe_info['address']}"
    else:
        message = "おすすめが見つかりませんでした。"

    return render_template('result.html', message=message)

# エラーページ
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# --- DBアクセス関数（担当者が差し替えやすくする） ---
def get_cafe_recommendation(answers):
    """
    answers は {'taste': '甘い', 'feeling': 'リラックスしたい', 'activity': ..., 'time': ...}
    一番多く一致するカフェをDBから探す。
    """
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row  # dict風に取り出す
    cur = conn.cursor()

    # 動的に WHERE 句を作る
    conditions = []
    params = []
    for key, value in answers.items():
        if value:
            conditions.append("(ca.question_id = (SELECT id FROM questions WHERE key = ?) AND ca.answer_text = ?)")
            params.extend([key, value])

    if not conditions:
        return None  # 全部未選択の場合

    sql = f"""
        SELECT c.id, c.name, c.address, COUNT(*) as match_count
        FROM cafes c
        JOIN cafe_answers ca ON c.id = ca.cafe_id
        WHERE {' OR '.join(conditions)}
        GROUP BY c.id
        ORDER BY match_count DESC
        LIMIT 1
    """

    cur.execute(sql, params)
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "name": row["name"],
            "address": row["address"],
            "match_count": row["match_count"]
        }
    else:
        return None



if __name__ == '__main__':
    app.run(debug=True)
