import streamlit as st #main work frame(Button,Inputs,etc..)
import pandas as pd #this library is to deal with weather and crop data,to convert data into DATAFrame
import time #this lib is to deal with delays such as data fetching time
from src.database import CROP_DB, save_dataset, get_dataset
from src.ai_engine import train_model_logic, predict_risk
from src.weather_service import fetch_weather
from src.ui_helpers import show_map, show_recommendations

#CROP_DB : DB Crops & Properties
#save_dataset, get_dataset : functions is to deal with storage
#train_model_logic, predict_risk : Engine AI
#fetch_weather : Weather data fetch service
#show_map, show_recommendations : UI Aid

# 1. إعدادات الصفحة والنمط (CSS)

st.set_page_config(page_title="Crop FrostShield", layout="wide", page_icon="❄️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }

    /* تنسيق زر الموقع ليشبه تطبيقات الموبايل */
    .location-btn {
        border: 1px solid #3498db; color: #3498db; background-color: transparent;
        padding: 5px; border-radius: 5px; width: 100%; text-align: center; cursor: pointer;
    }

    /* تنسيق صفحة النتائج لتكون مميزة */
    .result-box {
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    .risk-high { background-color: #ffebee; border: 2px solid #ef5350; color: #c62828; }
    .risk-safe { background-color: #e8f5e9; border: 2px solid #66bb6a; color: #2e7d32; }

    div[data-testid="column"] { float: right; }
</style>
""", unsafe_allow_html=True)

# تهيئة حالة الجلسة (للتنقل بين الصفحات)
if 'page' not in st.session_state:
    st.session_state['page'] = 'input'  # الصفحة الافتراضية


# 2. الدوال المساعدة للتنقل

def go_to_result():
    st.session_state['page'] = 'result'
    st.rerun()


def go_to_input():
    st.session_state['page'] = 'input'
    st.session_state['weather_fetched'] = False  # إعادة تعيين الطقس
    st.rerun()



# 3. الهيكلية الرئيسة (Main Layout)
# العنوان الرئيسيً
st.title("❄️ نظام Crop FrostShield")
st.markdown("---")

# نظام التبويبات
tab_home, tab_admin = st.tabs(["🌾 التطبيق الرئيسي", "⚙️ لوحة التحكم (Admin)"])

# تبويب التطبيق الرئيسي
with tab_home:

    # الصفحة 1: واجهة الإدخال (Input Interface)

    if st.session_state['page'] == 'input':

        col_map, col_inputs = st.columns([1, 1])

        with col_inputs:
            st.subheader("1. إدخال البيانات")

            # 1. نوع المحصول (Dropdown)
            crop_name = st.selectbox("نوع المحصول:", list(CROP_DB.keys()))
            crop_info = CROP_DB[crop_name]
            # نحفظ البيانات لاستخدامها في صفحة النتائج
            st.session_state['selected_crop'] = crop_info
            st.session_state['crop_name'] = crop_name

            # 2. الموقع (Latitude / Longitude)
            st.markdown("**الموقع الجغرافي:**")

            # زر Use My Location

            if st.button("📍 Use My Location"):
                with st.spinner("جاري تحديد الموقع عبر GPS..."):
                    time.sleep(1)  # تأثير وهمي للبحث
                    st.session_state['lat'] = 33.5138
                    st.session_state['lon'] = 36.2765
                    st.success("تم تحديد الموقع بدقة.")

            # حقول الإدخال (تتحدث تلقائياً من الزر أو يدوياً)
            lat = st.number_input("خط العرض (Latitude)", value=st.session_state.get('lat', 0.0), format="%.4f")
            lon = st.number_input("خط الطول (Longitude)", value=st.session_state.get('lon', 0.0), format="%.4f")

            # 3. زر Get Weather from API
            if st.button("☁️ Get Weather from API"):
                with st.spinner("الاتصال بـ Open-Meteo..."):
                    w_data = fetch_weather(lat, lon)
                    if w_data:
                        st.session_state['weather'] = w_data
                        st.session_state['weather_fetched'] = True
                        st.success("تم جلب البيانات.")
                    else:
                        st.error("فشل الاتصال.")

            # 4. عرض القيم القادمة من API
            if st.session_state.get('weather_fetched', False):
                st.markdown("---")
                st.markdown("**الطقس المتوقع ليلاً:**")
                w = st.session_state['weather']
                temp = st.number_input("درجة الحرارة (°C)", value=w['temp_night'])
                wind = st.number_input("سرعة الرياح (km/h)", value=w['wind_speed'])
                hum = st.number_input("الرطوبة (%)", value=w['humidity'])

                # حفظ المدخلات النهائية للتحليل
                st.session_state['final_inputs'] = {
                    'temp': temp, 'wind': wind, 'hum': hum
                }

                # 5. زر Analyze Frost Risk
                st.markdown("---")
                if st.button("🚀 Analyze Frost Risk", type="primary", use_container_width=True):
                    # تشغيل التحليل وحفظ النتيجة
                    input_df = pd.DataFrame([{
                        'temp_night': temp, 'wind_speed': wind, 'humidity': hum,
                        'crop_type_code': crop_info['code'], 'cold_tolerance': crop_info['tolerance']
                    }])
                    prob, risk_class = predict_risk(input_df)

                    st.session_state['result'] = {'prob': prob, 'class': risk_class}
                    go_to_result()  # الانتقال لصفحة النتائج

        with col_map:
            st.subheader("تحديد الموقع")
            show_map(lat, lon)  #

    # -------------------------------------------------------
    # الصفحة 2: واجهة النتائج (Result Page)
    # -------------------------------------------------------
    elif st.session_state['page'] == 'result':
        res = st.session_state['result']
        inputs = st.session_state['final_inputs']
        crop = st.session_state['selected_crop']

        # زر العودة
        if st.button("🔙 العودة للبداية"):
            go_to_input()

        st.markdown("## 📊 تقرير تحليل المخاطر")

        col_res_main, col_res_details = st.columns([1, 1])

        with col_res_main:
            # 1. عرض النسبة والتصنيف
            risk_percent = res['prob'] * 100

            if res['class'] == 1:
                st.markdown(f"""
                <div class="result-box risk-high">
                    <h2>🚨 High Frost Risk</h2>
                    <h1>{risk_percent:.1f}%</h1>
                    <p>خطر صقيع مرتفع</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-box risk-safe">
                    <h2>✅ Safe - No Frost Risk</h2>
                    <h1>{risk_percent:.1f}%</h1>
                    <p>الوضع آمن</p>
                </div>
                """, unsafe_allow_html=True)

            # 3. التوصيات الوقائية (فقط عند الخطر)
            if res['class'] == 1 or risk_percent > 40:
                st.warning("🛡️ **توصيات وقائية (Action Plan):**")
                st.markdown("1. **تغطية المحصول** (Plastic Covers) ")
                st.markdown("2. **تفعيل الري بالضباب** (Fog Irrigation) ")
                st.markdown("3. **استخدام مراوح الهواء** (Wind Machines) ")
                st.markdown("4. **تأجيل الري الصباحي** ")

        with col_res_details:
            # 2. توضيح الأسباب
            st.subheader("📝 تحليل الأسباب (Risk Factors):")

            # السبب 1: انخفاض الحرارة
            if inputs['temp'] <= crop['tolerance'] + 2:
                st.error(f"🔴 **انخفاض الحرارة:** الحرارة المتوقعة ({inputs['temp']}°C) قريبة من درجة التجمد.")
            else:
                st.success(f"🟢 **الحرارة:** ({inputs['temp']}°C) ضمن الحدود الآمنة.")

            # السبب 2: الرطوبة
            if inputs['hum'] > 80:
                st.error(f"🔴 **الرطوبة:** عالية جداً ({inputs['hum']}%) مما يعزز تشكل الصقيع.")
            elif inputs['hum'] < 40:
                st.info(f"🟡 **الرطوبة:** منخفضة ({inputs['hum']}%)، قد يحدث صقيع إشعاعي جاف.")
            else:
                st.success(f"🟢 **الرطوبة:** معتدلة.")

            # السبب 3: المحصول حساس للصقيع
            # المنطق المعدل: إذا كانت قدرة التحمل أكبر من -2 (مثل البندورة 0 والبطاطا -2) فهو حساس جداً
            if crop['tolerance'] >= -2:
                st.warning(
                    f"⚠️ **نوع المحصول:** هذا المحصول ({st.session_state['crop_name']}) حساس للصقيع (Sensitive).")
            else:
                st.success(f"🌱 **نوع المحصول:** ({st.session_state['crop_name']}) مقاوم نسبياً للبرودة.")

            # سبب إضافي (الرياح) - من منطق النموذج
            if inputs['wind'] < 5:
                st.warning("⚠️ **الرياح:** ساكنة، مما يزيد من خطر الانعكاس الحراري.")

# :::::::: تبويب لوحة التحكم (Admin Panel) ::::::::
with tab_admin:
    st.header("إعدادات النظام")

    st.subheader("1. إدارة البيانات (Dataset)")
    up_file = st.file_uploader("رفع ملف بيانات جديد (CSV)", type="csv")
    if up_file:
        save_dataset(up_file)
        st.success("تم تحديث قاعدة البيانات بنجاح.")

    st.subheader("2. نموذج الذكاء الاصطناعي (Model)")
    if st.button("بدء إعادة التدريب (Retrain Model)"):
        with st.spinner("جاري تدريب النموذج..."):
            df = get_dataset()
            if df is not None:
                acc, auc = train_model_logic(df)
                c1, c2 = st.columns(2)
                c1.metric("الدقة (Accuracy)", f"{acc * 100:.1f}%")  #
                c2.metric("ROC AUC", f"{auc:.3f}")  #
                st.success("تم التدريب وحفظ النموذج.")
            else:
                st.error("لا يوجد ملف بيانات.")

    st.subheader("3. إعدادات API")
    st.text_input("OpenWeatherMap API Key", type="password")  #