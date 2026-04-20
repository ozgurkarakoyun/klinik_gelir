# Klinik Takip Sistemi

Flask + SQLite tabanlı klinik giriş takip uygulaması.

## Railway Deploy Adımları

### 1. GitHub'a Yükle
```bash
git init
git add .
git commit -m "ilk kurulum"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/klinik-takip.git
git push -u origin main
```

### 2. Railway'de Proje Oluştur
1. https://railway.app adresine git, GitHub ile giriş yap
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Repoyu seç → deploy başlar

### 3. Volume Ekle (veri kaybolmasın!)
Railway'de SQLite dosyasının kaybolmaması için:
1. Projeye tıkla → **"Add a service"** → **"Volume"**
2. Mount path: `/data`
3. Service'e git → **Variables** sekmesi → ekle:
   ```
   DB_PATH = /data/klinik.db
   ```
4. Redeploy yap

### 4. Domain Al
- Settings → Networking → **"Generate Domain"**
- URL kopyala → istediğin cihazdan aç

## Lokal Çalıştırma
```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

## Özellikler
- ✅ Ortopedi / Fizik Tedavi doktor seçimi
- ✅ 14 işlem tipi (Muayene, FZT, SIS, HIL, ESWT, Kortizon, Tetik Nokta, Mezoterapi, Ozon, PRP, Alçı, Tırnak Çekimi, Lipoödem, **Ameliyat**)
- ✅ Nakit / Kredi Kartı
- ✅ Günlük / Haftalık / Aylık / Özel tarih aralığı raporları
- ✅ Aylık karşılaştırma grafiği (son 12 ay)
- ✅ Doktor bazlı gelir karşılaştırması
- ✅ İşlem bazlı istatistikler
- ✅ SQLite — Volume ile kalıcı depolama
