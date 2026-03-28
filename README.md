# ⚽ Transfermarkt Analytics

Transfermarkt'tan futbol verilerini çeken, SQLite veritabanında saklayan ve Streamlit ile görselleştiren modern bir analitik platformudur.

## 🎯 Özellikler

- **📊 Dashboard**: Lig, kulüp, oyuncu ve maç istatistikleri
- **⚽ Kulüp Analizi**: Liglere göre kulüpları görüntüle
- **👤 Oyuncu Verileri**: Kulüplara göre oyuncu listesi
- **🏟️ Maç Bilgileri**: Lig maçlarının detaylı bilgileri
- **📈 İstatistikler**: Grafikler ve analitik görseller

## 📋 Gereksinimler

- Python 3.11+
- SQLite3
- pip (Python paket yöneticisi)

## 🚀 Kurulum

### 1. Repository'yi klonla
```bash
git clone <repository-url>
cd transfermarkt-analytics
```

### 2. Sanal ortam oluştur
```bash
python -m venv venv
```

### 3. Sanal ortamı aktifleştir

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Gerekli paketleri yükle
```bash
pip install -r requirements.txt
```

## 🏃 Kullanım

### Streamlit Uygulamasını Çalıştır
```bash
streamlit run app.py
```

Tarayıcı otomatik olarak açılacak ve `http://localhost:8501` adresinde uygulama görünecektir.

### Scraper'ı Çalıştır
```bash
python run_scraper.py
```

## 📁 Proje Yapısı

```
transfermarkt-analytics/
├── app.py                    # Streamlit ana uygulaması
├── config.py                 # Yapılandırma dosyası
├── requirements.txt          # Python bağımlılıkları
├── run_scraper.py           # Scraper çalıştırıcısı
├── database/
│   ├── __init__.py
│   ├── db.py               # Veritabanı bağlantısı
│   └── models.py           # SQLAlchemy modelleri
├── scraper/
│   ├── __init__.py
│   ├── clubs.py            # Kulüpler scraper
│   ├── players.py          # Oyuncular scraper
│   └── matches.py          # Maçlar scraper
├── .github/
│   └── workflows/
│       └── scrape.yml      # GitHub Actions workflow
└── README.md               # Bu dosya
```

## 🔧 Yapılandırma

`config.py` dosyasında aşağıdaki ayarları yapabilirsiniz:

```python
BASE_URL = "https://www.transfermarkt.com"  # Transfermarkt URL
DATABASE_URL = "sqlite:///./transfermarkt.db"  # Veritabanı yolu
REQUEST_TIMEOUT = 10  # İstek zaman aşımı (saniye)
RETRY_ATTEMPTS = 3  # Yeniden deneme sayısı
```

### Desteklenen Ligler

- 🇹🇷 Türkiye - Süper Lig
- 🇬🇧 İngiltere - Premier League
- 🇪🇸 İspanya - La Liga
- 🇩🇪 Almanya - Bundesliga
- 🇮🇹 İtalya - Serie A
- 🇫🇷 Fransa - Ligue 1
- 🇵🇹 Portekiz - Primeira Liga
- 🇳🇱 Hollanda - Eredivisie
- 🇧🇪 Belçika - Belgian Pro League
- 🇬🇷 Yunanistan - Super League

## 🤖 GitHub Actions (Otomatik Scraping)

`.github/workflows/scrape.yml` dosyası günde bir kez otomatik olarak verileri çeker ve depoya gönderir.

Kron zamanlaması:
```
Saat: 00:00 UTC
Gün: Her gün
```

## 📊 Veritabanı Şeması

### Tablolar

1. **leagues** - Futbol ligleri
2. **clubs** - Kulüpler
3. **players** - Oyuncular
4. **matches** - Maçlar

Her tabloda `created_at` ve `updated_at` zaman damgaları bulunur.

## 🐛 Sorun Giderme

### "ModuleNotFoundError: No module named 'database'"
Sanal ortamın aktif olduğundan emin olun ve bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

### Streamlit veritabanı bulamıyor
Çalışma dizinin doğru olduğundan emin olun. `app.py` ile aynı dizinde çalıştırın:
```bash
cd /path/to/project
streamlit run app.py
```

### Scraper veri çekemiyor
- İnternet bağlantınızı kontrol edin
- User-Agent'in aktif olduğundan emin olun
- Transfermarkt sitesinin erişilebilir olduğunu doğrulayın

## 📦 Bağımlılıklar

| Paket | Sürüm | Amaç |
|-------|-------|------|
| requests | >=2.31.0 | HTTP istekleri |
| beautifulsoup4 | >=4.12.2 | HTML parsing |
| selenium | >=4.15.2 | Web tarama (dinamik içerik) |
| sqlalchemy | >=2.0.23 | ORM |
| streamlit | >=1.28.1 | Web arayüzü |
| pandas | >=2.2.0 | Veri analizi |
| plotly | >=5.18.0 | İnteraktif grafikler |
| lxml | >=4.9.5 | XML/HTML işleme |

## 📝 Not

- Transfermarkt'ın Robots.txt ve Kullanım Şartlarına uyun
- Aşırı scraping yapımı engelleyebilir - request delay'ini ayarlayın
- Veritabanında saklanan veriler telif altında olabilir

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle kabul edilir. Büyük değişiklikler için lütfen önce konu açın.

## 📄 Lisans

Bu proje MIT Lisansı altında yayınlanmıştır.

## 📞 İletişim

Sorularınız veya önerileriniz varsa, lütfen Issue açın.

---

**Son Güncelleme**: Mart 2026
**Versiyon**: 1.0.0
