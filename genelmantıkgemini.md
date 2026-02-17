# Binance Pump/Dump Sinyal Algoritması - Genel Mantık

Bu belge, **binancePump** projesinin çalışma prensibini, sinyal yakalama algoritmasını ve satış (çıkış) stratejisi mantığını özetler.

## 1. Projenin Amacı
Bu proje bir "Trading Bot" (Otomatik Al-Sat yapan robot) değil, bir **Sinyal Takip ve Analiz Aracıdır**.
Amacı: Binance üzerindeki yüzlerce kripto varlığı **milisaniyeler mertebesinde** (Websocket ile) izleyerek, normal dışı para giriş/çıkışlarını ve ani fiyat hareketlerini (Pump & Dump) kullanıcıya anlık olarak raporlamaktır.

---

## 2. Algoritma Mantığı

Sistem 4 ana aşamadan oluşur:

### A. Veri Akışı (Data Ingestion)
- **Teknoloji**: REST API yerine **Websocket** kullanılır.
- **Farkı**: Sunucuya "Fiyat ne oldu?" diye sormak yerine, borsada işlem gerçekleştiği anda veri sunucudan bize akar (`push`). Bu sayede gecikme (latency) minimize edilir.
- **İşlem**: Gelen her fiyat/hacim paketi anlık olarak işlenir ve bir önceki durumla kıyaslanır.

### B. Anomali Tespiti (Sinyal Üretme)
Algoritma, "her fiyat artışını" değil, sadece "hacimli ve sıra dışı" hareketleri yakalar. Bir coinin sinyal üretmesi için **aynı anda** şu iki şartı sağlaması gerekir:

1.  **Fiyat Patlaması**: Fiyat, son güncellemeye göre **>%0.05** değişmeli.
2.  **Hacim Patlaması**: 24 Saatlik toplam hacim, son güncellemeye göre aniden **>%0.05** artmalı.

> **Mantık**: Devasa 24 saatlik hacmin içinde, 1 saniyede %0.05'lik ani bir hacim artışı olması, o an tahtadan "Balina" büyüklüğünde bir emir geçtiğini kanıtlar.

### C. Gruplama ve Puanlama (Momentum)
Tek bir anlık hareket yanıltıcı olabilir. Algoritma bu sinyalleri `PriceGroup` nesneleri altında toplar ve bir **Momentum Puanı** oluşturur:
- **Tick Count**: Art arda kaç kez sinyal yaktı? (Hareketin kararlılığı)
- **Total Volume Change**: Toplamda ne kadar hacim girdi?
- **Relative Price Change (RPCh)**:
    - **Pozitif (+)**: Alım baskısı (Pump)
    - **Negatif (-)**: Satış baskısı (Dump)

### D. Sıralama (Ranking)
Sitem sürekli olarak şu listeleri günceller:
1.  **Top Ticks**: En sık sinyal üretenler (En hareketli tahtalar).
2.  **Top Price Change**: Fiyatı en çok savrulanlar.
3.  **Top Relative Change**: Yönü en belirgin olanlar (En sert Pump veya Dump).

---

## 3. Satış Zamanı Nasıl Anlaşılır? (Exit Strategy)

**Önemli**: Kodun içinde `sell()` fonksiyonu yoktur. Otomatik satış yapmaz. Karar kullanıcıya aittir. Ancak algoritma size **"Kaç!"** sinyalleri verir:

### A. Renk Kodları (Görsel Uyarı)
Konsol çıktısı renklenerek size piyasa yönünü anlatır:
- **YEŞİL (Green)**: Alım baskısı hakim (Pump devam ediyor).
- **KIRMIZI (Red)**: Satış baskısı hakim (Dump başladı).

### B. İndikatörler
Takip edilmesi gereken kritik veriler:
1.  **RPCh (Relative Price Change) Negatife Dönmesi**: Eğer bu değer pozitiften düşmeye başlarsa veya eksiye geçerse, alıcılar tükenmiş ve satıcılar baskın gelmiş demektir.
2.  **Hacimsiz Fiyat Hareketi**: Fiyat artmaya çalışıyor ama `Volume Change` durduysa, bu bir "Fake Pump" veya "Boğa Tuzağı" olabilir.

### Özet
Algoritma size **"Şu an tahtayı süpürüyorlar (AL)"** veya **"Şu an tahtaya mal boşaltıyorlar (SAT)"** bilgisini verir. Tetiği çekecek olan kullanıcıdır.
