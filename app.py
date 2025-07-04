from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = '秘密のキー'  # セッション使うために必要！

# トップページ
@app.route('/')
def index():
    session.clear()  # セッションをクリアして新規スタート
    return render_template('index.html')

@app.route('/question/taste', methods=['GET', 'POST'])
def question_taste():
    if request.method == 'POST':
        session['taste'] = request.form['taste']
        return redirect(url_for('question_feeling'))
    return render_template('questions/taste.html')

@app.route('/question/feeling', methods=['GET', 'POST'])
def question_feeling():
    if request.method == 'POST':
        session['feeling'] = request.form['feeling']
        return redirect(url_for('question_activity'))
    return render_template('questions/feeling.html')

@app.route('/question/activity', methods=['GET', 'POST'])
def question_activity():
    if request.method == 'POST':
        session['activity'] = request.form['activity']
        return redirect(url_for('question_time'))
    return render_template('questions/activity.html')

@app.route('/question/time', methods=['GET', 'POST'])
def question_time():
    if request.method == 'POST':
        session['time'] = request.form['time']
        return redirect(url_for('result'))
    return render_template('questions/time.html')

# 結果ページ
@app.route('/result')
def result():
    answers = {
        'taste': session.get('taste'),
        'feeling': session.get('feeling'),
        'activity': session.get('activity'),
        'time': session.get('time')
    }

    # DBからおすすめを取得
    cafe_info = get_cafe_recommendation(answers)

    if cafe_info:
        message = f"おすすめは『{cafe_info['name']}』です！<br>住所：{cafe_info['address']}"
        cafe_photo_url = url_for('static', filename='img/cafes/' + cafe_info['photo_url']) if cafe_info.get('photo_url') else None
    else:
        message = "おすすめが見つかりませんでした。"
        cafe_photo_url = None

    return render_template('result.html', message=message, cafe_photo_url=cafe_photo_url)

# エラーページ
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# DBアクセス関数
def get_cafe_recommendation(answers):
    """
    answers は {'taste': '甘い', 'feeling': 'リラックスしたい', 'activity': ..., 'time': ...}
    一番多く一致するカフェをDBから探す。
    """
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    conditions = []
    params = []
    for key, value in answers.items():
        if value:
            conditions.append("(ca.question_id = (SELECT id FROM questions WHERE key = ?) AND ca.answer_text = ?)")
            params.extend([key, value])

    if not conditions:
        return None

    sql = f"""
        SELECT c.id, c.name, c.address, c.photo_url, COUNT(*) as match_count
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
            "match_count": row["match_count"],
            "photo_url": row["photo_url"]
        }
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)
