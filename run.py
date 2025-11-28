#This file for resolve run streamlit through "CLI"

import sys
import os
from streamlit.web import cli as stcli


def main():
    # تحديد مسار ملف التطبيق بدقة
    app_path = os.path.join(os.path.dirname(__file__), "app.py")

    # إعداد أمر التشغيل داخلياً
    sys.argv = ["streamlit", "run", app_path]

    # تشغيل السيرفر
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()