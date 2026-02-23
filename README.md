# 🍳 BigChefs Kurumsal Operasyon ve Denetim Sistemi (MVP)

Bu proje, BigChefs şubelerinin günlük operasyonlarını, mutfak/bar standartlarını, personel görevlerini ve rutin alarmlarını tek bir merkezden yönetmek için tasarlanmış kurumsal bir "Advanced Checklist" ve Denetim (Audit) yazılımıdır.

## 🚀 Özellikler
- **Jira-Style Görev Akışı:** "Evet/Hayır" yerine YAPILACAK -> İŞLEMDE -> TAMAMLANDI mantığı.
- **Dinamik Şube Yönetimi:** Sınırsız şube, departman ve vardiya ekleme.
- **Otomatik Rutin Motoru:** Belirlenen saatte tüm personele otomatik görev/alarm düşmesi.
- **Personel Yönetimi (Onboarding/Offboarding):** Rol bazlı (Müdür, Komi, Barmen vb.) yetkilendirme.
- **Export Center:** Günlük z-raporları ve audit denetimlerinin Excel/CSV olarak dışa aktarılması.

## 🛠️ Kurulum (Yerel / Local)
1. Python 3.9+ yüklü olduğundan emin olun.
2. Gereksinimleri yükleyin: `pip install -r requirements.txt`
3. Uygulamayı başlatın: `streamlit run app.py`

## 🐳 Docker ile Canlıya Alma (Production)
Sunucunuzda (VDS/Cloud) Docker kurulu ise tek satırla sistemi ayağa kaldırabilirsiniz:
```bash
docker-compose up -d --build
