import streamlit as st
import json
import os
import csv
import io
import time
import pandas as pd
from datetime import datetime, timedelta

USERS_FILE = "bc_users.json"       
LOGS_FILE = "bc_logs_final.json"   
CONFIG_FILE = "bc_config.json"     
INSTANCES_FILE = "bc_instances.json" 
NOTIFICATIONS_FILE = "bc_notifications.json"
TASKS_FILE = "bc_adhoc_tasks.json" 
ROUTINES_FILE = "bc_routines.json" 

DEFAULT_ADMIN = {
    "admin": {"name": "Timur Bey", "pass": "admin123", "role": "superadmin", "branch": "Frankfurt", "section": "Management", "email": "", "phone": "", "birthdate": "1990-01-01"}
}

DEFAULT_CONFIG = {
    "Frankfurt": {
        "Müdür": {
            "Sabah Açılış": [
                {"text": "Kasa açılış işlemleri yapılıp rulo, adisyon ve fatura yeterliliği kontrol edildi mi?", "type": "flow"},
                {"text": "Dünkü raporlar ve iletişim defteri okundu mu?", "type": "flow"},
                {"text": "Restoran ısı (21-24 derece), müzik listesi ve aydınlatmaları mevsime göre ayarlandı mı?", "type": "flow"},
                {"text": "Tüm ekibin kılık/kıyafet, isimlik, saç/sakal ve kişisel hijyen kontrolü yapıldı mı?", "type": "flow"}
            ],
            "Gün İçi Operasyon": [
                {"text": "Sipariş alımlarında personelin eksiksiz olarak 'Captain Order' kullandığı teyit edildi mi?", "type": "flow"},
                {"text": "Bekleyen misafirlere doğru süre (Opsiyonlu +5 dk) verilip uygun alanda ikram sağlanıyor mu?", "type": "flow"},
                {"text": "Sipariş iptalleri ve ürün zayiileri Kerzz sistemine nedenleriyle birlikte anında giriliyor mu?", "type": "flow"}
            ],
            "Gece Kapanış": [
                {"text": "Gün sonu Kerzz Z raporu ile Yazarkasa POS Z raporları karşılaştırılıp mutabakat sağlandı mı?", "type": "flow"},
                {"text": "Tüm departmanların 'Kapanış Kontrol Listeleri'ni eksiksiz tamamladığı fiziki olarak denetlendi mi?", "type": "flow"},
                {"text": "Restorandan çıkarken tüm güvenlik kameraları kontrol edilip alarm sistemleri kuruldu mu?", "type": "flow"}
            ]
        },
        "Servis (Salon & Komi)": {
            "Sabah Açılış": [
                {"text": "Masa ayakları kontrol edilip, sallanmadıklarından emin olundu mu?", "type": "flow"},
                {"text": "Menaj takımları (Nar ekşisi, zeytinyağı, tuz, karabiber vb.) doldurulup dış yüzeyleri silindi mi?", "type": "flow"},
                {"text": "Servant içleri temizlenip eksik malzemeler tamamlandı mı? Çekmecelerde kişisel eşya yok değil mi?", "type": "flow"},
                {"text": "Misafir tuvaletlerinin detaylı temizliği kontrol edilip 'Temizlik Kontrol Listesi' imzalandı mı?", "type": "flow"}
            ],
            "Gün İçi Operasyon": [
                {"text": "Siparişten sonra en geç 4 dakika içinde Amuse Bouche ve taze ekmek servisi yapıldı mı?", "type": "flow"},
                {"text": "Yemek servisinden 2 yudum/çatal sonra masaya gidilip misafir memnuniyeti soruldu mu?", "type": "flow"},
                {"text": "Toplanan boşlardan bardaklar bar tepsisine, tabaklar bulaşıkhane tepsisine zamanında taşınıyor mu?", "type": "flow"}
            ],
            "Gece Kapanış": [
                {"text": "Sosiyerlik içerisindeki soslar (ketçap, mayonez vb.) temizlenip soğuk dolaba kaldırıldı mı?", "type": "flow"},
                {"text": "Tüm servantların iç ve dış temizliği yapılıp, gıda maddesi/leke bırakılmadı değil mi?", "type": "flow"},
                {"text": "Masa temizleme bezleri dezenfekte olması için ilaçlı/deterjanlı suya konuldu mu?", "type": "flow"}
            ]
        },
        "Bar": {
            "Sabah Açılış": [
                {"text": "Bar printerları (yazıcılar) kontrol edilip fiş rulo kağıtları takıldı mı?", "type": "flow"},
                {"text": "Eksik ürünler geceden hazırlanan PAAR listesine göre depodan alınıp FIFO kuralına göre dizildi mi?", "type": "flow"},
                {"text": "Çay demlenip, espresso ve Türk kahvesi makineleri servise hazır hale getirildi mi?", "type": "flow"}
            ],
            "Gün İçi Operasyon": [
                {"text": "Tüm içecekler sipariş saatinden itibaren en fazla 4 dakika içinde servise çıktı mı?", "type": "flow"},
                {"text": "Boşalan dolaplar, operasyon yoğunluğuna göre soğukluk dengesi bozulmadan tekrar dolduruluyor mu?", "type": "flow"}
            ],
            "Gece Kapanış": [
                {"text": "Boş içki/meşrubat şişeleri kasalara istiflenip, boşalan kasalar uygun depo alanlarına taşındı mı?", "type": "flow"},
                {"text": "Gün içinde yapılan ürün fireleri 'Bar Zayii Formu'na eksiksiz işlendi mi?", "type": "flow"},
                {"text": "Katı meyve sıkacağı, blender ve kahve makinelerinin parçaları detaylıca yıkanıp fişleri çekildi mi?", "type": "flow"},
                {"text": "Bar tezgahı ve zemini hiçbir yapışkan/şıra lekesi kalmayacak şekilde yıkandı/silindi mi?", "type": "flow"}
            ]
        },
        "Mutfak": {
            "Sabah Açılış": [
                {"text": "Soğuk oda, buzdolapları ve kuru depoların sıcaklık dereceleri kontrol edilip formlara işlendi mi?", "type": "flow"},
                {"text": "Vardiya başlangıcında 'Günlük Hazırlık Listesi'ne göre (mise en place) ürün hazırlıkları tamamlandı mı?", "type": "flow"},
                {"text": "Mutfak personeli eksiksiz olarak temiz/ütülü üniforma, başlık, bone ve terlik ile üretime hazır mı?", "type": "flow"}
            ],
            "Gün İçi Operasyon": [
                {"text": "Tüm yiyecekler BigChefs reçetelerine, porsiyon gramajlarına ve sunum standartlarına uygun hazırlanıyor mu?", "type": "flow"},
                {"text": "Açık mutfak kuralları gereği abiyerde servis personeliyle sessiz iletişim kurulup, telefon kullanılmıyor mu?", "type": "flow"},
                {"text": "Tüm gıda maddeleri uygun şekilde etiketlenip depolarda FIFO (İlk giren ilk çıkar) kuralı uygulanıyor mu?", "type": "flow"}
            ],
            "Gece Kapanış": [
                {"text": "Tezgahlar, raflar, fırınlar, ocaklar ve ızgaralar hijyen standartlarına uygun kimyasallarla temizlendi mi?", "type": "flow"},
                {"text": "Açıkta ve ağzı açık hiçbir gıda maddesi bırakılmadan tamamı streçlenip dolaplara kaldırıldı mı?", "type": "flow"}
            ]
        },
        "Bulaşıkhane & Temizlik": {
            "Sabah Açılış": [
                {"text": "Bulaşık makinesi kontrolleri yapıldı, kimyasal ve deterjan seviyeleri yeterli durumda mı?", "type": "flow"},
                {"text": "Yıkama alanının (zemin, lavabolar, mazgallar) genel temizliği yapıldı mı?", "type": "flow"}
            ],
            "Gün İçi Operasyon": [
                {"text": "Salon ve bardan gelen kirli bardak, tabak, çatal-bıçak biriktirilmeden zamanında makineye sürülüyor mu?", "type": "flow"},
                {"text": "Yıkanan temiz bardak, tabak ve ekipmanlarda leke/su izi kalmadığı kontrol edilerek teslim ediliyor mu?", "type": "flow"}
            ],
            "Gece Kapanış": [
                {"text": "Tüm mutfak, bar ve bulaşıkhane çöpleri ağzı sıkıca bağlanarak ana çöp/konteyner bölgesine taşındı mı?", "type": "flow"},
                {"text": "Bulaşık makinesinin suyu tamamen boşaltılıp, filtreleri ve iç aksamı detaylı olarak yıkandı mı?", "type": "flow"},
                {"text": "Bulaşıkhane zeminleri fırçalanarak yıkandı ve su birikintisi kalmayacak şekilde çek çek ile temizlendi mi?", "type": "flow"}
            ]
        }
    }
}

BRAND_COLORS = {"primary": "#0052CC", "secondary": "#172B4D", "bg_light": "#F4F5F7"}

def apply_branding():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .stApp { background-color: #F4F5F7; font-family: 'Inter', sans-serif; }
        div.stButton > button { background-color: #0052CC; color: white; border-radius: 4px; font-weight: 600; border: none; transition: 0.2s; }
        div.stButton > button:hover { background-color: #0047B3; color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn-danger > button { background-color: #FFEBE6 !important; color: #BF2600 !important; }
        .btn-danger > button:hover { background-color: #FFBDAD !important; }
        .metric-box { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(9,30,66,0.1); text-align: center; border-bottom: 3px solid #0052CC; margin-bottom: 10px; }
        .metric-title { font-size: 14px; color: #5E6C84; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; }
        .metric-value { font-size: 28px; color: #172B4D; font-weight: 700; }
        .badge { padding: 4px 8px; border-radius: 3px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
        .badge-todo { background: #DFE1E6; color: #42526E; }
        .badge-inprogress { background: #DEEBFF; color: #0052CC; }
        .badge-done { background: #E3FCEF; color: #006644; }
        .badge-skipped { background: #FFF0B3; color: #FF8B00; }
        .badge-failed { background: #FFEBE6; color: #BF2600; }
        .right-panel { background: white; padding: 20px; border-radius: 8px; border: 1px solid #DFE1E6; box-shadow: 0 1px 3px rgba(9,30,66,0.1); }
        .panel-header { font-size: 14px; font-weight: 600; color: #5E6C84; text-transform: uppercase; margin-bottom: 15px; border-bottom: 2px solid #F4F5F7; padding-bottom: 8px; }
        .stat-row { display: flex; justify-content: space-between; font-size: 13px; color: #172B4D; margin-bottom: 10px; }
        .stat-val { font-weight: 600; }
        .breadcrumb { color: #6B778C; font-size: 13px; margin-bottom: 10px; }
        h1, h2, h3 { color: #172B4D; font-weight: 600; }
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] { font-family: 'Inter', sans-serif; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)

def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w", encoding='utf-8') as f: json.dump(default, f, indent=4, ensure_ascii=False)
        return default
    with open(file, "r", encoding='utf-8') as f: return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

def send_notification(to_username, subject, message):
    notifs = load_json(NOTIFICATIONS_FILE, [])
    notifs.append({"id": str(len(notifs) + 1), "to": to_username, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "subject": subject, "message": message, "read": False})
    save_json(NOTIFICATIONS_FILE, notifs)

if not os.path.exists("photos"): os.makedirs("photos")
if not os.path.exists("profiles"): os.makedirs("profiles")

st.set_page_config(page_title="BigChefs Operasyon", layout="wide", page_icon="📋")
apply_branding()

users_db = load_json(USERS_FILE, DEFAULT_ADMIN)
stations_db = load_json(CONFIG_FILE, DEFAULT_CONFIG) 
instances_db = load_json(INSTANCES_FILE, {}) 
adhoc_tasks_db = load_json(TASKS_FILE, [])
all_logs = load_json(LOGS_FILE, [])
notifs_db = load_json(NOTIFICATIONS_FILE, [])
routines_db = load_json(ROUTINES_FILE, [])

now = datetime.now()
today_str = now.strftime("%Y-%m-%d")
current_time_str = now.strftime("%H:%M")
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
current_day_str = gunler_tr[now.weekday()]

if today_str not in instances_db or not instances_db[today_str]:
    instances_db[today_str] = {}
    for b, sects in stations_db.items():
        instances_db[today_str][b] = {}
        for s, shfts in sects.items():
            instances_db[today_str][b][s] = {}
            for shf in shfts.keys():
                instances_db[today_str][b][s][shf] = {"status": "OPEN", "tasks": {}}
    save_json(INSTANCES_FILE, instances_db)

routines_updated = False
tasks_updated = False
for r in routines_db:
    if current_day_str in r.get("days", []) and current_time_str >= r.get("time", "23:59"):
        if r.get("last_triggered") != today_str:
            for u_name, u_data in users_db.items():
                if u_data.get("branch") == r.get("branch") or r.get("branch") == "Tümü":
                    if r.get("target") == "Tümü" or u_data.get("role") == r.get("target"):
                        send_notification(u_name, f"⏰ RUTİN: {r['title']}", r['desc'])
                        adhoc_tasks_db.append({
                            "to": u_name, "title": f"⏰ {r['title']}", "desc": r['desc'],
                            "due": today_str, "status": "Pending", "from": "Sistem (Oto-Rutin)"
                        })
                        tasks_updated = True
            r["last_triggered"] = today_str
            routines_updated = True
if routines_updated: save_json(ROUTINES_FILE, routines_db)
if tasks_updated: save_json(TASKS_FILE, adhoc_tasks_db)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if os.path.exists("logo.png"): st.image("logo.png", width=150)
        st.markdown("<h2 style='text-align: center; color:#172B4D;'>Sisteme Giriş Yapın</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u_in = st.text_input("Kullanıcı ID")
            p_in = st.text_input("Şifre", type="password")
            if st.form_submit_button("Devam Et", use_container_width=True):
                if u_in in users_db and users_db[u_in]["pass"] == p_in:
                    users_db[u_in]["last_login"] = datetime.now().strftime("%d.%m.%Y %H:%M")
                    save_json(USERS_FILE, users_db)
                    st.session_state['logged_in'], st.session_state['username'] = True, u_in
                    st.rerun()
                else: st.error("Hatalı giriş!")
else:
    current_username = st.session_state['username']
    current_user = users_db[current_username]
    u_role, u_branch, u_section, u_name = current_user.get('role'), current_user.get('branch'), current_user.get('section'), current_user.get('name')
    
    unread = sum(1 for n in notifs_db if n["to"] == current_username and not n.get("read", False))
    notif_label = f"🔔 Bildirimler ({unread})" if unread > 0 else "📭 Bildirimler"

    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", width=120)
        st.markdown(f"**{u_name}**<br><span style='color:#6B778C; font-size:12px;'>{u_role.upper()}</span>", unsafe_allow_html=True)
        st.divider()
        
        m_opts = ["🏠 Ana Ekran", "📋 Gelişmiş Form (Checklist)", notif_label]
        if u_role in ["shift_leader", "auditor", "admin", "ops_manager", "superadmin"]: m_opts.append("📊 Dashboard & Raporlar")
        if u_role in ["admin", "ops_manager", "superadmin"]: m_opts += ["🛠️ Kurumsal Yönetim", "⚙️ Sistem Senkronizasyon", "👥 Personel Yönetimi"]
        m_opts.append("⚙️ Profil Ayarları")
        
        sel_menu = st.radio("MENÜ", m_opts)
        st.divider()
        if st.button("🚪 Çıkış Yap"): st.session_state['logged_in'] = False; st.rerun()

    sel_branch = u_branch
    if u_role in ["superadmin", "ops_manager", "auditor"] and sel_menu in ["📊 Dashboard & Raporlar", "🛠️ Kurumsal Yönetim", "👥 Personel Yönetimi"]:
        b_opts = list(stations_db.keys())
        sel_branch = st.sidebar.selectbox("🌍 İncelenen Şube", b_opts if b_opts else [u_branch])

    if sel_menu == "🏠 Ana Ekran":
        if os.path.exists("banner_image.png"): st.image("banner_image.png", use_container_width=True)
        st.title(f"Günün Özeti, {u_name.split()[0]}")
        
        my_tasks = [t for t in adhoc_tasks_db if t["to"] == current_username and t["status"] == "Pending"]
        overdue_count = sum(1 for t in my_tasks if datetime.strptime(t['due'], "%Y-%m-%d").date() < now.date() if 'due' in t)
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-box'><div class='metric-title'>📋 Görev & Rutinler</div><div class='metric-value'>{len(my_tasks)}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-box' style='border-bottom-color: #FF8B00;'><div class='metric-title'>🚨 Geciken</div><div class='metric-value' style='color:#FF8B00;'>{overdue_count}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-box' style='border-bottom-color: #006644;'><div class='metric-title'>✅ Aktif Şube</div><div class='metric-value' style='color:#006644;'>{u_branch}</div></div>", unsafe_allow_html=True)

        if my_tasks:
            with st.expander("🎯 BEKLEYEN GÖREVLER & ALARMLAR", expanded=True):
                for idx, t in enumerate(my_tasks):
                    st.warning(f"**{t['title']}** (Termin: {t.get('due','')})\n\n{t.get('desc','')}")
                    if st.button("✅ Görevi Tamamla", key=f"d_{idx}"):
                        t["status"] = "Completed"
                        save_json(TASKS_FILE, adhoc_tasks_db)
                        if t.get("from") != "Sistem (Oto-Rutin)": send_notification(t.get("from", "admin"), "Görev Bitti", f"{u_name} görevi tamamladı.")
                        st.rerun()

    elif sel_menu == "📋 Gelişmiş Form (Checklist)":
        tasks_data = instances_db.get(today_str, {}).get(u_branch, {}).get(u_section, {})
        
        if not tasks_data: st.warning(f"Sistemde {u_section} departmanı için tanımlanmış bir görev listesi yok. Yöneticinizden sizi doğru departmana atamasını isteyiniz.")
        else:
            sel_shf = st.selectbox("Görev Listesi Seçiniz:", list(tasks_data.keys()))
            st.divider()
            
            col_main, col_right = st.columns([2.5, 1], gap="large")
            template_items = stations_db.get(u_branch, {}).get(u_section, {}).get(sel_shf, [])
            
            if "status" not in tasks_data[sel_shf]: tasks_data[sel_shf] = {"status": "OPEN", "tasks": {}}
            current_state = tasks_data[sel_shf].get("tasks", {})
            
            if not current_state and template_items:
                for itm in template_items: current_state[itm['text']] = "YAPILACAK"
                tasks_data[sel_shf]["tasks"] = current_state
                save_json(INSTANCES_FILE, instances_db)

            with col_main:
                st.markdown(f"<div class='breadcrumb'>BigChefs / {u_branch} / {u_section} / {sel_shf}</div>", unsafe_allow_html=True)
                st.markdown(f"<h1>{sel_shf} Görev Akışı</h1>", unsafe_allow_html=True)
                
                total_t = len(template_items)
                done_t = sum(1 for v in current_state.values() if v in ["TAMAMLANDI", "ATLANDI", "DONE", "SKIPPED"])
                prog_val = done_t / total_t if total_t > 0 else 0
                st.progress(prog_val)
                st.markdown("<br>**Kontrol Listesi**", unsafe_allow_html=True)
                
                updated_state = {}
                legacy_map = {"TO DO": "YAPILACAK", "IN PROGRESS": "İŞLEMDE", "DONE": "TAMAMLANDI", "SKIPPED": "ATLANDI", "FAILED": "İHLAL"}
                valid_statuses = ["YAPILACAK", "İŞLEMDE", "TAMAMLANDI", "ATLANDI", "İHLAL"]

                for i, itm in enumerate(template_items):
                    q_text = itm['text']
                    q_status = current_state.get(q_text, "YAPILACAK")
                    
                    if q_status in legacy_map: q_status = legacy_map[q_status]
                    if q_status not in valid_statuses: q_status = "YAPILACAK"
                    
                    b_color = "todo"
                    if q_status == "TAMAMLANDI": b_color = "done"
                    elif q_status == "İŞLEMDE": b_color = "inprogress"
                    elif q_status == "İHLAL": b_color = "failed"
                    elif q_status == "ATLANDI": b_color = "skipped"

                    c_txt, c_stat, c_action = st.columns([6, 2, 1])
                    c_txt.markdown(f"<div style='padding-top:8px;'><span class='badge badge-{b_color}'>{q_status}</span> &nbsp;&nbsp; <span style='font-size:14px; font-weight:500;'>{q_text}</span></div>", unsafe_allow_html=True)
                    new_stat = c_stat.selectbox("Durum", valid_statuses, index=valid_statuses.index(q_status), key=f"stat_{i}", label_visibility="collapsed")
                    updated_state[q_text] = new_stat
                    c_action.markdown(f"<div style='padding-top:8px; color:#6B778C; font-size:12px; text-align:right;'>Bugün</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 0; border-top: 1px solid #DFE1E6;'>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Formu Arşive Gönder", use_container_width=True):
                    instances_db[today_str][u_branch][u_section][sel_shf]["tasks"] = updated_state
                    if not any(s in ["YAPILACAK", "İŞLEMDE"] for s in updated_state.values()):
                        instances_db[today_str][u_branch][u_section][sel_shf]["status"] = "COMPLETED"
                        res = {q: {"cevap": s, "is_issue": s=="İHLAL", "issue_status": "Open" if s=="İHLAL" else "Verified"} for q, s in updated_state.items()}
                        all_logs.append({"tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "sube": u_branch, "bolum": u_section, "vardiya": sel_shf, "personel": u_name, "kontroller": res})
                        save_json(LOGS_FILE, all_logs)
                        st.success("Tüm görevler arşivlendi!")
                    save_json(INSTANCES_FILE, instances_db)
                    st.rerun()

            with col_right:
                fail_t = sum(1 for v in current_state.values() if v in ["İHLAL", "FAILED"])
                inprog_t = sum(1 for v in current_state.values() if v in ["İŞLEMDE", "IN PROGRESS"])
                st.markdown(f"""
                <div class='right-panel'>
                    <div class='panel-header'>İlerleme Durumu 🔄</div>
                    <div class='stat-row'><span>✅ Tamamlanan</span> <span class='stat-val'>{done_t}/{total_t}</span></div>
                    <div class='stat-row'><span>⏳ İşlemde</span> <span class='stat-val' style='color:#0052CC;'>{inprog_t}</span></div>
                    <div class='stat-row'><span>🚨 İhlal / Hata</span> <span class='stat-val' style='color:#BF2600;'>{fail_t}</span></div>
                    <div class='stat-row'><span>👥 Sorumlu</span> <span class='stat-val'>{u_name.split()[0]}</span></div>
                </div>
                """, unsafe_allow_html=True)

    elif sel_menu == "📊 Dashboard & Raporlar":
        st.title("📊 Performans Raporları (Arşiv)")
        with st.expander("🔍 Filtreleme", expanded=True):
            f1, f2, f3, f4 = st.columns(4)
            date_range = f1.date_input("Tarih:", [datetime.now() - timedelta(days=30), datetime.now()])
            sel_f_branch = f2.selectbox("Şube:", ["Tümü"] + list(stations_db.keys()))
            sel_f_dept = f3.selectbox("Departman:", ["Tümü"] + (list(stations_db[sel_f_branch].keys()) if sel_f_branch != "Tümü" and sel_f_branch in stations_db else []))
            sel_f_shift = f4.selectbox("Vardiya:", ["Tümü", "Sabah Açılış", "Gün İçi Operasyon", "Gece Kapanış"])

        filtered_data = []
        for log in all_logs:
            try:
                log_date_str = log.get('tarih', '').split()[0]
                if not log_date_str: continue
                log_date = datetime.strptime(log_date_str, "%Y-%m-%d").date()
                if not (date_range[0] <= log_date <= date_range[1]): continue
                if sel_f_branch != "Tümü" and log.get('sube') != sel_f_branch: continue
                if sel_f_dept != "Tümü" and log.get('bolum') != sel_f_dept: continue
                if sel_f_shift != "Tümü" and sel_f_shift not in log.get('vardiya', ''): continue
                filtered_data.append(log)
            except: continue

        if not filtered_data: st.warning("Seçili kriterlerde veri bulunamadı.")
        else:
            st.dataframe(pd.DataFrame([{
                "Tarih": l.get('tarih', '-'), 
                "Şube": l.get('sube', '-'), 
                "Bölüm": l.get('bolum', '-'), 
                "Personel": l.get('personel', '-')
            } for l in filtered_data]), use_container_width=True)
            
            st.divider()
            st.subheader("📥 Export Center")
            excel_rows = []
            for l in filtered_data:
                for m, d in l.get('kontroller', {}).items():
                    excel_rows.append({
                        "Tarih": l.get('tarih', ''), "Şube": l.get('sube', ''), "Bölüm": l.get('bolum', ''),
                        "Vardiya": l.get('vardiya', ''), "Personel": l.get('personel', ''), "Madde": m, 
                        "Durum": d.get('cevap', '')
                    })
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if excel_rows: pd.DataFrame(excel_rows).to_excel(writer, index=False)
                else: pd.DataFrame([{"Bilgi": "Veri yok."}]).to_excel(writer, index=False)
            st.download_button("📊 Excel Olarak İndir (Tüm Detaylar)", output.getvalue(), f"Rapor_{today_str}.xlsx")

    elif sel_menu == "🛠️ Kurumsal Yönetim":
        st.title("Kurumsal Operasyon Yönetimi")
        t1, t2, t3, t4 = st.tabs(["📋 Görev Şablonu Yarat", "🌍 Şube & Vardiya Ekle", "⏰ Otomatik Rutinler", "🚀 Anlık Görev Ata"])
        
        with t1:
            st.markdown("### 📋 Standart Görev Şablonu Oluştur (Checklist)")
            if sel_branch in stations_db:
                col_m, col_r = st.columns([2.5, 1], gap="large")
                with col_m:
                    depts = list(stations_db[sel_branch].keys())
                    if depts:
                        c_s1, c_s2 = st.columns(2)
                        sel_dept_t = c_s1.selectbox("Departman Seç", depts)
                        shifts = list(stations_db[sel_branch][sel_dept_t].keys())
                        if shifts:
                            sel_shift_t = c_s2.selectbox("Vardiya Seç", shifts)
                            st.divider()
                            with st.form("add_item_form", clear_on_submit=True):
                                c_i1, c_i2 = st.columns([5, 1])
                                new_q = c_i1.text_input("Yeni Görev Maddesi Ekle*", placeholder="Örn: Masaların ayakları sallanıyor mu?")
                                if c_i2.form_submit_button("Ekle", use_container_width=True):
                                    if new_q:
                                        stations_db[sel_branch][sel_dept_t][sel_shift_t].append({"text": new_q, "type": "flow"})
                                        save_json(CONFIG_FILE, stations_db); st.rerun()

                            st.markdown("<br>**Mevcut Görevler Listesi**", unsafe_allow_html=True)
                            current_items = stations_db[sel_branch][sel_dept_t][sel_shift_t]
                            for idx, itm in enumerate(current_items):
                                c_l1, c_l2, c_l3 = st.columns([1, 8, 1])
                                c_l1.markdown("<span class='badge badge-todo'>GÖREV</span>", unsafe_allow_html=True)
                                c_l2.markdown(f"<span style='font-size:14px;'>{itm['text']}</span>", unsafe_allow_html=True)
                                if c_l3.button("🗑️", key=f"del_t_{idx}"):
                                    current_items.pop(idx); save_json(CONFIG_FILE, stations_db); st.rerun()
                                st.markdown("<hr style='margin: 4px 0; border-top: 1px solid #DFE1E6;'>", unsafe_allow_html=True)
                with col_r:
                    st.info("Buraya eklediğiniz her madde, personelin ekranına bir İş Akışı (YAPILACAK) olarak düşer. İşten ayrılan olursa yanındaki çöp kutusuna basarak silebilirsiniz.")
        
        with t2:
            st.markdown("### 🌍 Şube & Departman Yönetimi")
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                st.info("Sisteme yeni bir şube ekleyin.")
                new_branch = st.text_input("Yeni Şube Adı (Örn: Londra):")
                if st.button("🏢 Yeni Şubeyi Oluştur") and new_branch:
                    if new_branch not in stations_db:
                        stations_db[new_branch] = {"Müdür": {"Sabah Açılış": [], "Gün İçi Operasyon": [], "Gece Kapanış": []}, "Servis (Salon & Komi)": {"Sabah Açılış": [], "Gün İçi Operasyon": [], "Gece Kapanış": []}, "Bar": {"Sabah Açılış": [], "Gün İçi Operasyon": [], "Gece Kapanış": []}, "Mutfak": {"Sabah Açılış": [], "Gün İçi Operasyon": [], "Gece Kapanış": []}, "Bulaşıkhane & Temizlik": {"Sabah Açılış": [], "Gün İçi Operasyon": [], "Gece Kapanış": []}}
                        save_json(CONFIG_FILE, stations_db); st.success(f"✅ {new_branch} eklendi!"); time.sleep(1); st.rerun()
            with c_b2:
                st.info("Seçili şubeye yeni departman veya vardiya ekleyin.")
                if stations_db:
                    sel_b_new = st.selectbox("Şube Seç:", list(stations_db.keys()), key="sb_new_b")
                    new_dept_name = st.text_input("1. Adım: Yeni Departman Yarat (Örn: Vale):")
                    if st.button("Departmanı Ekle") and new_dept_name:
                        if new_dept_name not in stations_db[sel_b_new]:
                            stations_db[sel_b_new][new_dept_name] = {"Sabah Açılış": []}
                            save_json(CONFIG_FILE, stations_db); st.success("Eklendi!"); time.sleep(1); st.rerun()
                    st.divider()
                    sel_d_new = st.selectbox("2. Adım: Vardiya Eklenecek Departmanı Seç:", list(stations_db[sel_b_new].keys()), key="sb_new_d")
                    new_shift_name = st.text_input("Yeni Vardiya Adı (Örn: Gece Kapanış):")
                    if st.button("⏰ Vardiyayı Ekle") and new_shift_name:
                        if new_shift_name not in stations_db[sel_b_new][sel_d_new]:
                            stations_db[sel_b_new][sel_d_new][new_shift_name] = []
                            save_json(CONFIG_FILE, stations_db); st.success("Eklendi!"); time.sleep(1); st.rerun()

        with t3:
            st.markdown("### ⏰ Otomatik Rutin / Alarm Oluştur")
            if routines_db:
                for i, r in enumerate(routines_db):
                    if r.get("branch") == sel_branch or r.get("branch") == "Tümü":
                        c_r1, c_r2 = st.columns([4, 1])
                        c_r1.markdown(f"**{r['title']}** - ⏰ {r['time']} | 🎯 Hedef: {r['target']}")
                        if c_r2.button("Sil", key=f"del_rut_{i}"):
                            routines_db.pop(i); save_json(ROUTINES_FILE, routines_db); st.rerun()
                st.divider()
            with st.form("new_routine"):
                r_title = st.text_input("Rutin Başlığı (Örn: Gece Işıklarını Kıs)")
                r_desc = st.text_area("Detay")
                c_rt1, c_rt2 = st.columns(2)
                r_time = c_rt1.time_input("Saat:")
                r_target = c_rt2.selectbox("Hedef Kitle:", ["Tümü", "staff", "shift_leader", "admin"])
                r_days = st.multiselect("Günler:", gunler_tr, default=gunler_tr)
                if st.form_submit_button("Alarmı Kur") and r_title:
                    routines_db.append({"title": r_title, "desc": r_desc, "time": r_time.strftime("%H:%M"), "days": r_days, "target": r_target, "branch": sel_branch, "last_triggered": ""})
                    save_json(ROUTINES_FILE, routines_db); st.success("Kuruldu!"); time.sleep(1); st.rerun()

        with t4:
            with st.form("new_task"):
                t_to = st.selectbox("Personel Seç:", [u for u, d in users_db.items() if d.get('branch') == sel_branch])
                t_title = st.text_input("Görev Başlığı")
                t_desc = st.text_area("Talimat")
                t_due = st.date_input("Termin")
                if st.form_submit_button("Görevi İlet") and t_title:
                    adhoc_tasks_db.append({"to": t_to, "title": t_title, "desc": t_desc, "due": str(t_due), "status": "Pending", "from": current_username})
                    save_json(TASKS_FILE, adhoc_tasks_db)
                    send_notification(t_to, "🚨 YENİ GÖREV", t_title); st.success("İletildi!"); time.sleep(1); st.rerun()

    elif sel_menu == "👥 Personel Yönetimi":
        st.title("Ekip ve Yetki Yönetimi")
        
        with st.expander("➕ Sisteme Yeni Personel Ekle", expanded=False):
            with st.form("new_user_form"):
                c_u1, c_u2 = st.columns(2)
                new_u_id = c_u1.text_input("Kullanıcı Giriş ID (Örn: ali_v)")
                new_u_pass = c_u2.text_input("Şifre", type="password")
                new_u_name = st.text_input("Tam Ad Soyad")
                c_u3, c_u4, c_u5 = st.columns(3)
                new_u_role = c_u3.selectbox("Sistem Rolü:", ["staff", "shift_leader", "admin", "ops_manager", "auditor"])
                new_u_branch = c_u4.selectbox("Kayıtlı Şubesi:", list(stations_db.keys()) if stations_db else ["Frankfurt"])
                new_u_sec = c_u5.selectbox("Departmanı:", ["Müdür", "Servis (Salon & Komi)", "Bar", "Mutfak", "Bulaşıkhane & Temizlik"])
                if st.form_submit_button("Personeli Sisteme Kaydet"):
                    if new_u_id and new_u_pass and new_u_name:
                        users_db[new_u_id] = {"name": new_u_name, "pass": new_u_pass, "role": new_u_role, "branch": new_u_branch, "section": new_u_sec, "email": "", "phone": "", "birthdate": "2000-01-01"}
                        save_json(USERS_FILE, users_db); st.success(f"✅ Eklendi!"); time.sleep(1); st.rerun()

        st.divider()
        st.markdown("### 📋 Mevcut Personel Listesi")
        ch1, ch2, ch3, ch4, ch5 = st.columns([1.5, 3, 2, 2, 1.5])
        ch1.markdown("**ID**")
        ch2.markdown("**Ad Soyad**")
        ch3.markdown("**Rol**")
        ch4.markdown("**Şube/Dep.**")
        ch5.markdown("**Aksiyon**")
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
        
        for u_id, u_data in users_db.items():
            c1, c2, c3, c4, c5 = st.columns([1.5, 3, 2, 2, 1.5])
            c1.markdown(f"<div style='padding-top:8px; font-weight:500;'>{u_id}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='padding-top:8px;'>{u_data.get('name', '-')}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='padding-top:8px;'>{u_data.get('role', '-').upper()}</div>", unsafe_allow_html=True)
            c4.markdown(f"<div style='padding-top:8px;'>{u_data.get('branch', '-')} - {u_data.get('section','')}</div>", unsafe_allow_html=True)
            
            if u_id != current_username and u_id != "admin":
                st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                if c5.button("🗑️ Sil", key=f"del_inline_{u_id}"):
                    del users_db[u_id]
                    save_json(USERS_FILE, users_db)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                c5.markdown("<div style='padding-top:8px; color:#6B778C;'>🔒 Kilitli</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 5px 0; border-top: 1px dashed #DFE1E6;'>", unsafe_allow_html=True)

    elif sel_menu == "⚙️ Sistem Senkronizasyon":
        st.title("Sistem Operasyon Merkezi")
        if st.button("🔄 Bugünkü Görevleri Sıfırla ve Tekrar Dağıt", type="primary"):
            instances_db[today_str] = {}
            for b, sects in stations_db.items():
                instances_db[today_str][b] = {}
                for s, shfts in sects.items():
                    instances_db[today_str][b][s] = {}
                    for shf in shfts.keys(): instances_db[today_str][b][s][shf] = {"status": "OPEN", "tasks": {}}
            save_json(INSTANCES_FILE, instances_db); st.success("✅ Dağıtım tamamlandı!"); time.sleep(1); st.rerun()

    elif sel_menu == notif_label:
        st.title("Gelen Kutusu")
        my_n = [n for n in notifs_db if n["to"] == current_username]
        for n in reversed(my_n):
            border = "#0052CC" if not n.get('read') else "#DFE1E6"
            st.markdown(f"<div style='border: 1px solid {border}; padding: 15px; border-radius: 8px; margin-bottom: 10px; background: white;'><b>{n['subject']}</b><br><small>{n['message']}</small></div>", unsafe_allow_html=True)
            if not n.get('read') and st.button("Okundu İşaretle", key=f"r_{n['id']}"):
                for db_n in notifs_db:
                    if db_n["id"] == n["id"]: db_n["read"] = True
                save_json(NOTIFICATIONS_FILE, notifs_db); st.rerun()

    elif sel_menu == "⚙️ Profil Ayarları":
        st.title("Hesap & Güvenlik")
        st.info(f"Sistem Kayıtlı Adınız: **{u_name}**")
        with st.form("prof"):
            n_email = st.text_input("E-Posta Adresi", value=current_user.get('email', ''))
            n_phone = st.text_input("Telefon", value=current_user.get('phone', ''))
            if st.form_submit_button("Güncelle"):
                users_db[current_username]["email"] = n_email
                users_db[current_username]["phone"] = n_phone
                save_json(USERS_FILE, users_db); st.success("Güncellendi!"); time.sleep(1); st.rerun()
