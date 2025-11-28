import folium
import streamlit as st
from streamlit_folium import st_folium

"""
مكتبة folium هي مجرد غلاف (Wrapper) لمكتبة جافاسكريبت الشهيرة Leaflet.js6.
 ما يفعله الكود هو توليد ملف HTML يحتوي على خريطة Leaflet وحقنه (Inject) داخل صفحة Streamlit
  ليظهر للمستخدم وكأنه جزء من التطبيق
"""

def show_map(lat, lon):
    #رسم الخريطة التفاعلية
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], popup="موقع الحقل", icon=folium.Icon(color='blue')).add_to(m)
    st_folium(m, height=400, width=None)

def show_recommendations(risk_class):
    #عرض التوصيات فقط عند الخطر
    if risk_class == 1:
        st.warning("🛡️ **توصيات وقائية:**")
        c1, c2 = st.columns(2)
        c1.markdown("- 1. **تغطية المحصول** (Plastic Covers)")
        c1.markdown("- 2. **تفعيل الري بالضباب** (Fog Irrigation)")
        c2.markdown("-3. **استخدام مراوح الهواء** (Wind Machines) ")
        c2.markdown("- 4. **تأجيل الري الصباحي** ")