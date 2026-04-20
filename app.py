from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

DB_PATH = os.environ.get('DB_PATH', 'klinik.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS kayitlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hasta TEXT NOT NULL,
            tarih TEXT NOT NULL,
            doktor TEXT NOT NULL,
            islemler TEXT NOT NULL,
            ucret REAL NOT NULL DEFAULT 0,
            odeme TEXT NOT NULL DEFAULT 'nakit',
            notlar TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ── Kayıtlar ──────────────────────────────────────────────
@app.route('/api/kayitlar', methods=['GET'])
def get_kayitlar():
    conn = get_db()
    rows = conn.execute('SELECT * FROM kayitlar ORDER BY tarih DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/kayitlar', methods=['POST'])
def add_kayit():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Veri gerekli'}), 400
    required = ['hasta', 'tarih', 'doktor', 'islemler', 'odeme']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} gerekli'}), 400
    islemler = ','.join(data['islemler']) if isinstance(data['islemler'], list) else data['islemler']
    conn = get_db()
    cur = conn.execute(
        'INSERT INTO kayitlar (hasta, tarih, doktor, islemler, ucret, odeme, notlar) VALUES (?,?,?,?,?,?,?)',
        (data['hasta'], data['tarih'], data['doktor'], islemler,
         float(data.get('ucret', 0)), data['odeme'], data.get('notlar', ''))
    )
    new_id = cur.lastrowid
    conn.commit()
    row = conn.execute('SELECT * FROM kayitlar WHERE id=?', (new_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201

@app.route('/api/kayitlar/<int:kid>', methods=['DELETE'])
def del_kayit(kid):
    conn = get_db()
    conn.execute('DELETE FROM kayitlar WHERE id=?', (kid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── Rapor: aylık karşılaştırma ────────────────────────────
@app.route('/api/rapor/aylik', methods=['GET'])
def rapor_aylik():
    conn = get_db()
    rows = conn.execute('''
        SELECT
            strftime('%Y-%m', tarih) AS ay,
            doktor,
            odeme,
            COUNT(*) AS hasta_sayisi,
            SUM(ucret) AS toplam_gelir,
            islemler
        FROM kayitlar
        GROUP BY ay, doktor, odeme
        ORDER BY ay DESC
    ''').fetchall()
    # İşlem istatistikleri ayrıca
    proc_rows = conn.execute('''
        SELECT strftime('%Y-%m', tarih) AS ay, islemler, COUNT(*) AS adet, SUM(ucret) as gelir
        FROM kayitlar
        GROUP BY ay, islemler
        ORDER BY ay DESC
    ''').fetchall()
    conn.close()
    return jsonify({
        'ozet': [dict(r) for r in rows],
        'islemler': [dict(r) for r in proc_rows]
    })

# ── Rapor: filtrelenmiş özet ──────────────────────────────
@app.route('/api/rapor/ozet', methods=['GET'])
def rapor_ozet():
    baslangic = request.args.get('baslangic', '2000-01-01')
    bitis = request.args.get('bitis', '2099-12-31')
    doktor = request.args.get('doktor', '')
    conn = get_db()
    q = 'SELECT * FROM kayitlar WHERE tarih >= ? AND tarih <= ?'
    params = [baslangic + 'T00:00:00', bitis + 'T23:59:59']
    if doktor:
        q += ' AND doktor = ?'
        params.append(doktor)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    toplam = sum(r['ucret'] for r in data)
    nakit = sum(r['ucret'] for r in data if r['odeme'] == 'nakit')
    kk = sum(r['ucret'] for r in data if r['odeme'] == 'kk')
    havale = sum(r['ucret'] for r in data if r['odeme'] == 'havale')
    return jsonify({
        'hasta_sayisi': len(data),
        'toplam_gelir': toplam,
        'nakit': nakit,
        'kredi_karti': kk,
        'havale': havale,
        'kayitlar': data
    })

# ── SPA fallback ──────────────────────────────────────────
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
