# 🔍 Proje Analizi: Binance Pump Detector

## 📁 Proje Yapısı

| Dosya | Açıklama |
|-------|----------|
| `binancePump.py` | **Ana uygulama** - Websocket bağlantısı ve fiyat izleme mantığı |
| `binanceHelper.py` | Binance API yardımcı fonksiyonları (tarih dönüşümleri, kline verisi) |
| `pricechange.py` | `PriceChange` dataclass - Anlık fiyat değişim verisi |
| `pricegroup.py` | `PriceGroup` dataclass - Sembol bazlı grup istatistikleri |
| `api_config.json` | API anahtarları (şu an boş) |
| `requirements.txt` | Bağımlılıklar |

---

## 🧠 Çalışma Mantığı

```
┌─────────────────────────────────────────────────────────────────┐
│                         binancePump.py                          │
├─────────────────────────────────────────────────────────────────┤
│  1. api_config.json'dan API key/secret okunur                   │
│  2. ThreadedWebsocketManager ile Binance'a bağlanır             │
│  3. Tüm ticker'lar 24 saat canlı dinlenir                       │
│  4. Her tick'te process_message() çalışır                       │
│                                                                 │
│  Filtreleme:                                                    │
│  • show_only_pair = "USDT" (sadece USDT çiftleri)              │
│  • min_perc = 0.05 (min %0.05 değişim)                          │
│                                                                 │
│  Raporlama (4 kategori):                                        │
│  • Top Ticks (en çok tick alan)                                │
│  • Top Total Price Change (toplam fiyat değişimi)              │
│  • Top Relative Price Change (göreceli fiyat değişimi)         │
│  • Top Total Volume Change (toplam hacim değişimi)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Veri Modelleri

### PriceChange (pricechange.py)

Anlık her tick için tutulan veri:

- `symbol` - Coin sembolü (örn: BTCUSDT)
- `price`, `prev_price` - Mevcut ve önceki fiyat
- `volume`, `prev_volume` - Mevcut ve önceki hacim
- `price_change_perc` - Fiyat değişim yüzdesi (property)
- `volume_change_perc` - Hacim değişim yüzdesi (property)
- `is_pump()`, `is_dump()` - Pump/dump tespiti

### PriceGroup (pricegroup.py)

Sembol bazlı kümülatif istatistikler:

- `tick_count` - Toplam tick sayısı
- `total_price_change` - Toplam mutlak fiyat değişimi
- `relative_price_change` - Net yönel fiyat değişimi (+ veya -)
- `total_volume_change` - Toplam hacim değişimi
- `console_color` - Terminalde renk (yeşil/kırmızı)

---

## 🛠 Yardımcı Fonksiyonlar (binanceHelper.py)

| Fonksiyon | Açıklama |
|-----------|----------|
| `binanceDataFrame()` | Kline verilerini pandas DataFrame'e çevirir |
| `date_to_milliseconds()` | Tarih stringini milisaniyeye çevirir |
| `interval_to_milliseconds()` | Interval stringini (1m, 1h, 1d) milisaniyeye çevirir |
| `get_historical_klines()` | Geçmiş kline verilerini çeker (**⚠️ `client` tanımlı değil - bug**) |

---

## ⚠️ Tespit Edilen Sorunlar

1. **`binanceHelper.py` satır 112**: `client` değişkeni tanımlı değil - `get_historical_klines()` çalışmaz
2. **`api_config.json`**: API anahtarları boş - gerçek kullanım için doldurulmalı
3. **README.md**: `pyTelegramBotAPI` ve `tqdm` bağımlılıkları yazılı ama `requirements.txt`'te yok

---

## 🚀 Özet

Bu proje, Binance'ın tüm USDT çiftlerini **real-time websocket** ile izleyerek:

- Ani fiyat değişimlerini
- Hacim anomalilerini  
- Potansiyel pump/dump sinyallerini

tespit etmeye çalışan bir **kripto anomaly detector**'dır. 

Terminale renkli çıktı verir (yeşil: artış, kırmızı: düşüş).
