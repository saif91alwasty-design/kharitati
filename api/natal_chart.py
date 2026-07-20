from flask import Flask, request, jsonify
import json
import traceback

app = Flask(__name__)

# قاعدة بيانات المدن العربية مع الإحداثيات
CITIES_DB = {
    'baghdad': {'lat': 33.3152, 'lng': 44.3661, 'name': 'بغداد'},
    'basra': {'lat': 30.5081, 'lng': 47.7835, 'name': 'البصرة'},
    'mosul': {'lat': 36.3450, 'lng': 43.1309, 'name': 'الموصل'},
    'erbil': {'lat': 36.1911, 'lng': 44.0093, 'name': 'أربيل'},
    'najaf': {'lat': 31.9996, 'lng': 44.3201, 'name': 'النجف'},
    'karbala': {'lat': 32.6160, 'lng': 44.0241, 'name': 'كربلاء'},
    'kut': {'lat': 32.5109, 'lng': 45.8181, 'name': 'الكوت'},
    'nasiriyah': {'lat': 31.0571, 'lng': 46.2637, 'name': 'الناصرية'},
    'amara': {'lat': 31.8344, 'lng': 47.1447, 'name': 'العمارة'},
    'diwaniyah': {'lat': 31.9929, 'lng': 44.9253, 'name': 'الديوانية'},
    'hillah': {'lat': 32.4640, 'lng': 44.4217, 'name': 'الحلة'},
    'ramadi': {'lat': 33.4206, 'lng': 43.3078, 'name': 'الرمادي'},
    'fallujah': {'lat': 33.3500, 'lng': 43.7833, 'name': 'الفلوجة'},
    'samarra': {'lat': 34.1956, 'lng': 43.8742, 'name': 'سامراء'},
    'tikrit': {'lat': 34.6111, 'lng': 43.6833, 'name': 'تكريت'},
    'duhok': {'lat': 36.8667, 'lng': 43.0000, 'name': 'دهوك'},
    'sulaymaniyah': {'lat': 35.5556, 'lng': 45.4333, 'name': 'السليمانية'},
    'kirkuk': {'lat': 35.4681, 'lng': 44.3922, 'name': 'كركوك'},
    'riyadh': {'lat': 24.7136, 'lng': 46.6753, 'name': 'الرياض'},
    'jeddah': {'lat': 21.4858, 'lng': 39.1925, 'name': 'جدة'},
    'mecca': {'lat': 21.3891, 'lng': 39.8579, 'name': 'مكة'},
    'medina': {'lat': 24.5247, 'lng': 39.5692, 'name': 'المدينة'},
    'dammam': {'lat': 26.3927, 'lng': 49.9777, 'name': 'الدمام'},
    'dubai': {'lat': 25.2048, 'lng': 55.2708, 'name': 'دبي'},
    'abu dhabi': {'lat': 24.4539, 'lng': 54.3773, 'name': 'أبوظبي'},
    'cairo': {'lat': 30.0444, 'lng': 31.2357, 'name': 'القاهرة'},
    'alexandria': {'lat': 31.2001, 'lng': 29.9187, 'name': 'الإسكندرية'},
    'amman': {'lat': 31.9454, 'lng': 35.9284, 'name': 'عمّان'},
    'kuwait': {'lat': 29.3759, 'lng': 47.9774, 'name': 'الكويت'},
    'doha': {'lat': 25.2854, 'lng': 51.5310, 'name': 'الدوحة'},
    'manama': {'lat': 26.0667, 'lng': 50.5577, 'name': 'المنامة'},
    'muscat': {'lat': 23.5880, 'lng': 58.3829, 'name': 'مسقط'},
    'beirut': {'lat': 33.8938, 'lng': 35.5018, 'name': 'بيروت'},
    'damascus': {'lat': 33.5138, 'lng': 36.2765, 'name': 'دمشق'},
    'london': {'lat': 51.5074, 'lng': -0.1278, 'name': 'لندن'},
}

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/api/natal_chart', methods=['GET', 'OPTIONS'])
def natal_chart():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # استخراج المعاملات
        name = request.args.get('name', 'User')
        year = int(request.args.get('year', 1990))
        month = int(request.args.get('month', 1))
        day = int(request.args.get('day', 1))
        hour = int(request.args.get('hour', 12))
        minute = int(request.args.get('minute', 0))
        city_key = request.args.get('city', 'baghdad').lower().strip()
        
        # البحث عن المدينة في قاعدة البيانات
        city_data = CITIES_DB.get(city_key)
        
        if not city_data:
            # إذا لم توجد، استخدم بغداد كافتراضي
            city_data = CITIES_DB['baghdad']
        
        lat = city_data['lat']
        lng = city_data['lng']
        city_name = city_data['name']
        
        # استيراد Kerykeion
        from kerykeion import AstrologicalSubject
        
        # حساب الخارطة - استخدام lat/lng فقط (بدون city لتجنب التعارض)
        subject = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city_name,
            lat=lat,
            lng=lng
        )
        
        # تجهيز النتائج
        result = {
            'success': True,
            'data': {
                'sun': {
                    'sign': subject.sun.sign,
                    'degree': round(float(subject.sun.degree), 2),
                    'house': subject.sun.house if hasattr(subject.sun, 'house') else None
                },
                'moon': {
                    'sign': subject.moon.sign,
                    'degree': round(float(subject.moon.degree), 2),
                    'house': subject.moon.house if hasattr(subject.moon, 'house') else None
                },
                'mercury': {
                    'sign': subject.mercury.sign,
                    'degree': round(float(subject.mercury.degree), 2)
                },
                'venus': {
                    'sign': subject.venus.sign,
                    'degree': round(float(subject.venus.degree), 2)
                },
                'mars': {
                    'sign': subject.mars.sign,
                    'degree': round(float(subject.mars.degree), 2)
                },
                'jupiter': {
                    'sign': subject.jupiter.sign,
                    'degree': round(float(subject.jupiter.degree), 2)
                },
                'saturn': {
                    'sign': subject.saturn.sign,
                    'degree': round(float(subject.saturn.degree), 2)
                },
                'ascendant': {
                    'sign': subject.ascendant.sign,
                    'degree': round(float(subject.ascendant.degree), 2)
                },
                'midheaven': {
                    'sign': subject.midheaven.sign,
                    'degree': round(float(subject.midheaven.degree), 2)
                }
            },
            'city_used': city_name
        }
        
        return jsonify(result)
        
    except Exception as e:
        # تسجيل الخطأ للتشخيص
        error_trace = traceback.format_exc()
        print(f"ERROR: {str(e)}")
        print(error_trace)
        
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': error_trace
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
