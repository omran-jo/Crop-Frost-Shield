import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score

#مسار حفظ النموذج المدرب
"""
دالة os.path.join
نحن لا نكتب المسار يدوياً مثل data/file.csv لأن طريقة كتابة المسارات تختلف بين Windows ( \ ) و Linux/Mac ( / ). 
دالة os.path.join تكتشف نظام التشغيل وتضع الفواصل الصحيحة تلقائياً، مما يجعل المشروع Portable (قابل للنقل والعمل على أي جهاز فوراً).
"""
MODEL_PATH = os.path.join('data', 'frost_model.pkl')

#تدريب النموذج وحساب الدقة
def train_model_logic(df):

    #تجديد المدخلات و المخرجات
    X = df[['temp_night', 'wind_speed', 'humidity', 'crop_type_code', 'cold_tolerance']]
    y = df['frost_risk']

    #تقسيم البيانات للتدريب و الاختبار
    """
    دالة train_test_split و random_state=42
    في علم البيانات، تقسيم البيانات إلى تدريب واختبار يتم عشوائياً. وضع قيمة ثابتة لـ random_state (والرقم 42 هو عرف برمجي شهير) يضمن "قابلية التكرار".
أي أنه في كل مرة نعيد فيها تدريب النموذج، سيتم تقسيم البيانات بنفس الطريقة تماماً، مما يضمن أن النتائج والمقاييس (Accuracy) لن تتغير عشوائياً بين كل عرض وآخر.

    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #بناء النموذج
    model = LogisticRegression()
    model.fit(X_train, y_train)

    #حساب مقاييس الاداء للعرض بلوحة التحكم
    #model.predict : تعطي النتيجة النهائية اذا كانت فوق ال50% تعطي 1 والا تعطي 0
    acc = accuracy_score(y_test, model.predict(X_test))
    #model.predict_proba : تعطي نسبة الاحتمال
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]) # [cite: 67]
    """
    الـ predict يقرر هل هناك خطر أم لا، 
    بينما predict_proba تخبر المزارع بمدى جدية هذا الخطر (هل هو خطر بنسبة 51% أم 99%؟). 
    """

    #حفظ النموذج
    if not os.path.exists('data'): os.makedirs('data')
    joblib.dump(model, MODEL_PATH)
    return acc, auc

def predict_risk(inputs):
    #التنبؤ للمستخدم الجديد
    if not os.path.exists(MODEL_PATH): return None, None
    model = joblib.load(MODEL_PATH)
    #إرجاع الاحتمالية (0.0-1.0) والتصنيف (0/1)
    return model.predict_proba(inputs)[0][1], model.predict(inputs)[0]