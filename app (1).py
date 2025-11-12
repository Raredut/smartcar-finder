from google.colab import drive
drive.mount('/content/drive')

import os
paths = [
 "/content/drive/MyDrive/car_images/Toyota.png",
 "/content/drive/MyDrive/car_images/hyundai.jpg",
 "/content/drive/MyDrive/car_images/tesla.jpg",
 "/content/drive/MyDrive/car_images/jeep.jpg",
 "/content/drive/MyDrive/car_images/logo.png",
]
for p in paths:
    print(p, "=>", os.path.exists(p))

  # ========== إنشاء ملف app.py مُصلح وآمن للتعامل مع الصور ==========
app_code = r'''
import os
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image, UnidentifiedImageError

# دالة مساعدة لفتح الصورة بأمان
def safe_load_image(path):
    """
    إذا path يبدأ بـ "http" نعيد السلسلة (Streamlit يقبل روابط).
    إذا كان مسارًا محليًا: نتحقق من وجود الملف ونحاول فتحه كـ PIL.Image.
    في حال الفشل نعيد None.
    """
    if not path:
        return None
    try:
        if str(path).lower().startswith("http"):
            return path  # Streamlit يدعم URL مباشرة
        if os.path.exists(path):
            try:
                img = Image.open(path)
                return img
            except UnidentifiedImageError:
                return None
        else:
            return None
    except Exception:
        return None

# ------------- بيانات السيارات (مسارات الصور محلية في Drive) -------------
cars_data = [
    {
        "name": "تويوتا كورولا",
        "brand": "Toyota",
        "price": 85000,
        "engine": "بنزين",
        "type": "عائلية",
        "color": "أبيض",
        "desc": "سيارة عملية واقتصادية مثالية للعائلات الصغيرة.",
        "img": "/content/drive/MyDrive/car_images/Toyota.png",
        "location": [24.7136, 46.6753],
    },
    {
        "name": "هيونداي النترا",
        "brand": "Hyundai",
        "price": 78000,
        "engine": "بنزين",
        "type": "صغيرة",
        "color": "فضي",
        "desc": "سيارة مريحة واقتصادية للاستخدام اليومي.",
        "img": "/content/drive/MyDrive/car_images/hyundai.jpg",
        "location": [21.3891, 39.8579],
    },
    {
        "name": "تسلا موديل 3",
        "brand": "Tesla",
        "price": 190000,
        "engine": "كهرباء",
        "type": "رياضية",
        "color": "أسود",
        "desc": "سيارة كهربائية ذكية بأداء عالٍ وتقنيات متقدمة.",
        "img": "/content/drive/MyDrive/car_images/tesla.jpg",
        "location": [25.276987, 55.296249],
    },
    {
        "name": "جيب رانجلر",
        "brand": "Jeep",
        "price": 210000,
        "engine": "ديزل",
        "type": "دفع رباعي",
        "color": "أحمر",
        "desc": "سيارة قوية للطرق الوعرة والمغامرات البرية.",
        "img": "/content/drive/MyDrive/car_images/jeep.jpg",
        "location": [26.4207, 50.0888],
    },
]

df = pd.DataFrame(cars_data)

# ---------- واجهة Streamlit ----------
st.set_page_config(page_title="مساعد السيارة الذكي", layout="wide")

# شعار (جرب وضع "/content/drive/MyDrive/car_images/logo.png")
logo_path = "/content/drive/MyDrive/car_images/logo.png"
logo_img = safe_load_image(logo_path)
if logo_img:
    st.sidebar.image(logo_img, width=120)
else:
    st.sidebar.write("لوغو غير متوفر")

st.sidebar.title("🚗 مساعد السيارة الذكي")
st.sidebar.markdown("مرحبًا بك! اختر سيارتك المثالية بسهولة 🧭")

st.title("🚗 مساعد السيارة الذكي")
st.write("اعثر على سيارتك المثالية بسهولة دون الحاجة لأي خبرة فنية بالسيارات!")

# ---------------- التصفية والبحث ----------------
search = st.text_input("🔍 ابحث عن سيارة بالاسم أو الماركة")
col1, col2, col3, col4 = st.columns(4)
car_type = col1.selectbox("النوع", ["الكل"] + sorted(df["type"].unique().tolist()))
color = col2.selectbox("اللون", ["الكل"] + sorted(df["color"].unique().tolist()))
engine = col3.selectbox("نوع المحرك", ["الكل"] + sorted(df["engine"].unique().tolist()))
price_limit = col4.slider("السعر الأقصى (ريال)", 50000, 250000, 250000, step=5000)

filtered = df[
    (df["price"] <= price_limit)
    & ((df["name"].str.contains(search, case=False)) | (df["brand"].str.contains(search, case=False)))
]
if car_type != "الكل":
    filtered = filtered[filtered["type"] == car_type]
if color != "الكل":
    filtered = filtered[filtered["color"] == color]
if engine != "الكل":
    filtered = filtered[filtered["engine"] == engine]

# ---------------- عرض السيارات مع تحميل الصورة الآمن ----------------
st.subheader("🚘 السيارات المتاحة")
if filtered.empty:
    st.info("❌ لا توجد سيارات تطابق المعايير.")
else:
    for _, car in filtered.iterrows():
        st.markdown("---")
        colA, colB = st.columns([1, 2])
        with colA:
            img = safe_load_image(car.get("img"))
            if img:
                st.image(img, use_column_width=True, caption=f"{car['brand']} {car['name']}")
            else:
                st.warning("صورة غير متوفرة")
        with colB:
            st.markdown(f"### {car['name']} ({car['brand']})")
            st.markdown(f"**السعر:** {car['price']:,} ريال")
            st.markdown(f"**المحرك:** {car['engine']} | **النوع:** {car['type']} | **اللون:** {car['color']}")
            st.markdown(car['desc'])
            st.button(f"⭐ أضف إلى المفضلة", key=f"fav{car['name']}")
            st.button(f"📞 طلب دعم حول {car['name']}", key=f"sup{car['name']}")

# ---------------- سؤال ذكي بسيط ----------------
st.subheader("🧠 اسأل مساعد السيارة الذكي")
q = st.text_input("اكتب سؤالك هنا:")
if q:
    q_lower = q.lower()
    if "عائلية" in q_lower:
        st.success("🚗 أنصحك بـ تويوتا كورولا أو هيونداي النترا — سيارات مثالية للعائلة.")
    elif "كهرباء" in q_lower:
        st.success("⚡ أنصحك بـ تسلا موديل 3 — سيارة كهربائية ذكية وصديقة للبيئة.")
    elif "دفع" in q_lower or "بر" in q_lower:
        st.success("🚙 جيب رانجلر هي الأنسب للمغامرات.")
    else:
        st.info("جرب أن تكتب مثل: 'أريد سيارة اقتصادية' أو 'سيارة رياضية'.")

# ---------------- خريطة المعارض ----------------
st.subheader("📍 خريطة المعارض القريبة")
m = folium.Map(location=[24.7136, 46.6753], zoom_start=5)
for _, car in df.iterrows():
    folium.Marker(location=car["location"], popup=f"{car['brand']} - {car['name']}").add_to(m)
st_folium(m, width=700, height=400)
'''
# نحفظ الملف
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("✅ تم إنشاء app.py بنجاح. راجع /content/app.py")

!wget -q -O - ipv4.icanhazip.com
!streamlit run app.py & npx --yes localtunnel --port 8501


your url is: https://xxxxx.loca.lt
