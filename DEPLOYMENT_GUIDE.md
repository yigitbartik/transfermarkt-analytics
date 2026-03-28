# 🚀 Streamlit Cloud Deployment Kılavuzu

Bu kılavuz, projeyi Streamlit Cloud'a dağıtmak için adım adım talimatlar sağlar.

## 📋 Ön Koşullar

1. GitHub hesabı
2. Streamlit Cloud hesabı (https://streamlit.io/cloud)
3. Bu repository'nin bir fork'u GitHub hesabınızda

## 🔧 Hazırlık

### 1. GitHub'a Push Et
```bash
git add .
git commit -m "Prepare for Streamlit deployment"
git push origin main
```

### 2. requirements.txt'i Doğrula
Dosyanız şu içeriği içermeli:
```
requests>=2.31.0,<3.0
beautifulsoup4>=4.12.2,<5.0
selenium>=4.15.2,<5.0
sqlalchemy>=2.0.23,<3.0
streamlit>=1.28.1,<2.0
pandas>=2.2.0,<3.0
plotly>=5.18.0,<6.0
python-dotenv>=1.0.0,<2.0
lxml>=4.9.5,<5.0
```

## 📱 Streamlit Cloud'a Dağıt

### 1. Streamlit Cloud'da Oturum Aç
- https://share.streamlit.io adresine git
- GitHub ile oturum aç

### 2. Yeni App Oluştur
- "New app" butonuna tıkla
- Repository seç: `transfermarkt-analytics`
- Branch: `main`
- Main file path: `app.py`
- Deploy'a tıkla

### 3. Dağıtımı Bekle
Dağıtım işlemi 2-5 dakika sürer.

## ⚙️ Streamlit Cloud Ayarları

### 1. Secrets Ekle (Opsiyonel)
`.streamlit/secrets.toml` dosyasını oluştur:

```toml
[database]
url = "sqlite:///./transfermarkt.db"

[scraper]
request_timeout = 10
retry_attempts = 3
```

Streamlit Cloud dashboard'dan secrets ekle:
1. App Settings → Secrets
2. TOML kodu yapıştır

### 2. Advanced Settings
- **Python version**: 3.11
- **Client error details**: minimal (production için)

## 🔄 Otomatik Güncellemeler

Streamlit Cloud otomatik olarak GitHub repository'sini izler ve güncellemeleri dağıtır:

1. Push → GitHub
2. Streamlit otomatik redeploy yapar (1-2 dakika)

## 🐛 Sorun Giderme

### "ModuleNotFoundError" Hatası
**Çözüm**: `requirements.txt`i güncelle ve tüm paketler listelendiğinden emin ol.

### Veritabanı Bağlantı Hatası
**Çözüm**: Streamlit Cloud ephemeral (geçici) dosya sistemi kullanır. Veriler yeniden başlatmada silinir. Persistent storage için:
- Streamlit Cloud Plans Pro/Business'e upgrade et
- veya
- Harici veritabanı (PostgreSQL) kullan

### Scraper'ın Çalışmaması
**Çözüm**: 
1. Scraper'ı lokal olarak çalıştır ve verileri git'e commit et
2. Veya GitHub Actions yapılandırmasını ayarla

## 💾 Persistent Data Çözümleri

### Seçenek 1: Git LFS (Küçük veritabanı)
```bash
git lfs install
git lfs track "*.db"
git add .gitattributes *.db
git commit -m "Add database with LFS"
git push
```

### Seçenek 2: Dış Veritabanı (Üretim için)

PostgreSQL'e geç:
```python
# config.py
DATABASE_URL = "postgresql://user:password@host/dbname"
```

Ücretsiz PostgreSQL Hosting:
- Railway.app
- Render.com
- Neon.tech

### Seçenek 3: GitHub Actions + Git
`.github/workflows/scrape.yml` workflow'u günde bir kez çalışır:
1. Verileri çeker
2. Veritabanı dosyasını günceller
3. Değişiklikleri GitHub'a gönderir
4. Streamlit otomatik redeploy yapar

## 📊 Performans Ayarları

### Caching Ekle
```python
@st.cache_data
def get_db_data():
    # Veri çekme işlemi
    pass
```

### Session State Kullan
```python
if 'data' not in st.session_state:
    st.session_state.data = get_db_data()
```

## 🔐 Güvenlik

### Environment Variables
Sensitive veriler için:

```python
import os
API_KEY = os.getenv("API_KEY")
```

Streamlit Cloud → Secrets → Ekle:
```
API_KEY = "your-key-here"
```

### Robots.txt Kuralları
`config.py`da request delay ekle:
```python
import time
time.sleep(1)  # Transfermarkt sunucusunun üzerine basma
```

## 📈 Monitoring

### Streamlit Community Cloud
- Logs: App menu → Manage app → View logs
- Metrics: Dashboard'dan performans izle
- Errors: Logs sekmesinde debug

## 🎯 Best Practices

1. **Development**
   ```bash
   streamlit run app.py
   ```

2. **Testing**
   - Lokal olarak tüm özellikleri test et
   - requirements.txt'i koru

3. **Deployment**
   - main branch'i her zaman stabil tut
   - Feature branch'lerde geliştir
   - Pull request ile merge et

4. **Production**
   - Error handling ekle
   - Logging yapılandır
   - Secrets kullan

## 📚 Kaynaklar

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

**Başarılı Dağıtımlar!** 🚀
