from flask import Flask, request, jsonify
from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

app = Flask(__name__)

# أسماء الأبراج بالترتيب
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# قاعدة بيانات المدن العربية
CITIES = {
    'baghdad': (33.3152, 44.3661, 'بغداد'),
    'basra': (30.5081, 47.7835, 'البصرة'),
    'mosul': (36.3450, 43.1309, 'الموصل'),
    'erbil': (36.1911, 44.0093, 'أربيل'),
    'najaf': (32.0000, 44.3333, 'النجف'),
    'karbala': (32.6160, 44.0241, 'كربلاء'),
    'kut': (32.5109, 45.8181, 'الكوت'),
    'nasiriyah': (31.0571, 46.2637, 'الناصرية'),
    'amara': (31.8344, 47.1447, 'العمارة'),
    'diwaniyah': (31.9929, 44.9253, 'الديوانية'),
    'hillah': (32.4640, 44.4217, 'الحلة'),
    'ramadi': (33.4206, 43.3078, 'الرمادي'),
    'fallujah': (33.3500, 43.7833, 'الفلوجة'),
    'samarra': (34.1956, 43.8742, 'سامراء'),
    'tikrit': (34.6111, 43.6833, 'تكريت'),
    'duhok': (36.8667, 43.0000, 'دهوك'),
    'sulaymaniyah': (35.5556, 45.4333, 'السليمانية'),
    'kirkuk': (35.4681, 44.3922, 'كركوك'),
    'riyadh': (24.7136, 46.6753, 'الرياض'),
    'jeddah': (21.4858, 39.1925, 'جدة'),
    'mecca': (21.3891, 39.8579, 'مكة'),
    'medina': (24.5247, 39.5692, 'المدينة'),
    'dammam': (26.3927, 49.9777, 'الدمام'),
    'dubai': (25.2048, 55.2708, 'دبي'),
    'abu dhabi': (24.4539, 54.3773, 'أبوظبي'),
    'cairo': (30.0444, 31.2357, 'القاهرة'),
    'alexandria': (31.2001, 29.9187, 'الإسكندرية'),
    'amman': (31.9454, 35.9284, 'عمّان'),
    'kuwait': (29.3759, 47.9774, 'الكويت'),
    'doha': (25.2854, 51.5310, 'الدوحة'),
    'manama': (26.0667, 50.5577, 'المنامة'),
    'muscat': (23.5880, 58.3829, 'مسقط'),
    'beirut': (33.8938, 35.5018, 'بيروت'),
    'damascus': (33.5138, 36.2765, 'دمشق'),
    'london': (51.5074, -0.1278, 'لندن'),
}

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/api/natal_chart', methods=['GET', 'OPTIONS'])
def natal_chart():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # استخراج البيانات
        name = request.args.get('name', 'User')
        year = int(request.args.get('year', 1990))
        month = int(request.args.get('month', 1))
        day = int(request.args.get('day', 1))
        hour = int(request.args.get('hour', 12))
        minute = int(request.args.get('minute', 0))
        city_key = request.args.get('city', 'baghdad').lower().strip()

        # الحصول على بيانات المدينة
        city_data = CITIES.get(city_key)
        if not city_data:
            # إذا لم تكن المدينة موجودة، استخدم النجف كافتراضية
            city_data = CITIES['najaf']

        lat, lng, city_name = city_data

        # ✅ الحل: تنسيق التاريخ الصحيح لـ Flatlib
        # Flatlib تتطلب: 'YYYY/MM/DD' و 'HH:MM:SS'
        date_str = f'{year}/{month}/{day}'
        time_str = f'{hour:02d}:{minute:02d}:00'

        # ✅ الحل: timezone offset (+03:00 للعراق، +03:00 للسعودية، +02:00 لمصر)
        tz_offset = '+03:00'  # افتراضي للعراق
        if city_key in ['cairo', 'alexandria']:
            tz_offset = '+02:00'
        elif city_key in ['dubai', 'abu dhabi']:
            tz_offset = '+04:00'
        elif city_key in ['london']:
            tz_offset = '+00:00'

        date = Datetime(date_str, time_str, tz_offset)
        pos = GeoPos(lat, lng)

        # ✅ الحل: معالجة الأخطاء عند حساب الخارطة
        try:
            chart = Chart(date, pos)
        except Exception as chart_err:
            print(f"Chart error: {chart_err}")
            # إذا فشل حساب الخارطة، أرجع خطأ واضح
            return jsonify({
                'success': False,
                'error': f'فشل في حساب الخارطة: {str(chart_err)}'
            }), 500

        # دالة مساعدة لاستخراج بيانات الكوكب
        def get_planet_data(obj):
            if obj is None:
                return {'sign': 'Unknown', 'degree': 0.0}
            sign_idx = obj.sign  # رقم البرج (0-11)
            if sign_idx < 0 or sign_idx >= 12:
                sign_idx = 0
            degree_in_sign = obj.lon - (sign_idx * 30)  # الدرجة داخل البرج
            return {
                'sign': SIGNS[sign_idx],
                'degree': round(degree_in_sign, 2)
            }

        # استخراج جميع الكواكب مع معالجة الأخطاء
        result = {
            'success': True,
            'data': {},
            'city_used': city_name
        }

        # قائمة الكواكب
        planets = {
            'sun': const.SUN,
            'moon': const.MOON,
            'mercury': const.MERCURY,
            'venus': const.VENUS,
            'mars': const.MARS,
            'jupiter': const.JUPITER,
            'saturn': const.SATURN
        }

        for planet_name, planet_const in planets.items():
            try:
                obj = chart.get(planet_const)
                result['data'][planet_name] = get_planet_data(obj)
            except Exception as e:
                print(f"Error getting {planet_name}: {e}")
                result['data'][planet_name] = {'sign': 'Unknown', 'degree': 0.0}

        # النقاط المهمة (Ascendant, MC)
        try:
            result['data']['ascendant'] = get_planet_data(chart.get(const.ASC))
        except Exception as e:
            print(f"Error getting ASC: {e}")
            result['data']['ascendant'] = {'sign': 'Unknown', 'degree': 0.0}

        try:
            result['data']['midheaven'] = get_planet_data(chart.get(const.MC))
        except Exception as e:
            print(f"Error getting MC: {e}")
            result['data']['midheaven'] = {'sign': 'Unknown', 'degree': 0.0}

        return jsonify(result)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
