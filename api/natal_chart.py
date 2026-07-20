from flask import Flask, request, jsonify
import traceback
from datetime import datetime

app = Flask(__name__)

# قاعدة بيانات المدن العربية مع الإحداثيات ومنطقة الزمن
CITIES_DB = {
    'baghdad': {'lat': 33.3152, 'lng': 44.3661, 'name': 'بغداد', 'tz': 'Asia/Baghdad'},
    'basra': {'lat': 30.5081, 'lng': 47.7835, 'name': 'البصرة', 'tz': 'Asia/Baghdad'},
    'mosul': {'lat': 36.3450, 'lng': 43.1309, 'name': 'الموصل', 'tz': 'Asia/Baghdad'},
    'erbil': {'lat': 36.1911, 'lng': 44.0093, 'name': 'أربيل', 'tz': 'Asia/Baghdad'},
    'najaf': {'lat': 32.0000, 'lng': 44.3333, 'name': 'النجف', 'tz': 'Asia/Baghdad'},
    'karbala': {'lat': 32.6160, 'lng': 44.0241, 'name': 'كربلاء', 'tz': 'Asia/Baghdad'},
    'kut': {'lat': 32.5109, 'lng': 45.8181, 'name': 'الكوت', 'tz': 'Asia/Baghdad'},
    'nasiriyah': {'lat': 31.0571, 'lng': 46.2637, 'name': 'الناصرية', 'tz': 'Asia/Baghdad'},
    'amara': {'lat': 31.8344, 'lng': 47.1447, 'name': 'العمارة', 'tz': 'Asia/Baghdad'},
    'diwaniyah': {'lat': 31.9929, 'lng': 44.9253, 'name': 'الديوانية', 'tz': 'Asia/Baghdad'},
    'hillah': {'lat': 32.4640, 'lng': 44.4217, 'name': 'الحلة', 'tz': 'Asia/Baghdad'},
    'ramadi': {'lat': 33.4206, 'lng': 43.3078, 'name': 'الرمادي', 'tz': 'Asia/Baghdad'},
    'fallujah': {'lat': 33.3500, 'lng': 43.7833, 'name': 'الفلوجة', 'tz': 'Asia/Baghdad'},
    'samarra': {'lat': 34.1956, 'lng': 43.8742, 'name': 'سامراء', 'tz': 'Asia/Baghdad'},
    'tikrit': {'lat': 34.6111, 'lng': 43.6833, 'name': 'تكريت', 'tz': 'Asia/Baghdad'},
    'duhok': {'lat': 36.8667, 'lng': 43.0000, 'name': 'دهوك', 'tz': 'Asia/Baghdad'},
    'sulaymaniyah': {'lat': 35.5556, 'lng': 45.4333, 'name': 'السليمانية', 'tz': 'Asia/Baghdad'},
    'kirkuk': {'lat': 35.4681, 'lng': 44.3922, 'name': 'كركوك', 'tz': 'Asia/Baghdad'},
    'riyadh': {'lat': 24.7136, 'lng': 46.6753, 'name': 'الرياض', 'tz': 'Asia/Riyadh'},
    'jeddah': {'lat': 21.4858, 'lng': 39.1925, 'name': 'جدة', 'tz': 'Asia/Riyadh'},
    'mecca': {'lat': 21.3891, 'lng': 39.8579, 'name': 'مكة', 'tz': 'Asia/Riyadh'},
    'medina': {'lat': 24.5247, 'lng': 39.5692, 'name': 'المدينة', 'tz': 'Asia/Riyadh'},
    'dammam': {'lat': 26.3927, 'lng': 49.9777, 'name': 'الدمام', 'tz': 'Asia/Riyadh'},
    'dubai': {'lat': 25.2048, 'lng': 55.2708, 'name': 'دبي', 'tz': 'Asia/Dubai'},
    'abu dhabi': {'lat': 24.4539, 'lng': 54.3773, 'name': 'أبوظبي', 'tz': 'Asia/Dubai'},
    'cairo': {'lat': 30.0444, 'lng': 31.2357, 'name': 'القاهرة', 'tz': 'Africa/Cairo'},
    'alexandria': {'lat': 31.2001, 'lng': 29.9187, 'name': 'الإسكندرية', 'tz': 'Africa/Cairo'},
    'amman': {'lat': 31.9454, 'lng': 35.9284, 'name': 'عمّان', 'tz': 'Asia/Amman'},
    'kuwait': {'lat': 29.3759, 'lng': 47.9774, 'name': 'الكويت', 'tz': 'Asia/Kuwait'},
    'doha': {'lat': 25.2854, 'lng': 51.5310, 'name': 'الدوحة', 'tz': 'Asia/Qatar'},
    'manama': {'lat': 26.0667, 'lng': 50.5577, 'name': 'المنامة', 'tz': 'Asia/Bahrain'},
    'muscat': {'lat': 23.5880, 'lng': 58.3829, 'name': 'مسقط', 'tz': 'Asia/Muscat'},
    'beirut': {'lat': 33.8938, 'lng': 35.5018, 'name': 'بيروت', 'tz': 'Asia/Beirut'},
    'damascus': {'lat': 33.5138, 'lng': 36.2765, 'name': 'دمشق', 'tz': 'Asia/Damascus'},
    'london': {'lat': 51.5074, 'lng': -0.1278, 'name': 'لندن', 'tz': 'Europe/London'},
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
        # استخراج المعاملات مع التحقق
        name = request.args.get('name', 'User')
        
        # تحويل التاريخ بشكل آمن
        try:
            year = int(request.args.get('year', 1990))
            month = int(request.args.get('month', 1))
            day = int(request.args.get('day', 1))
            hour = int(request.args.get('hour', 12))
            minute = int(request.args.get('minute', 0))
        except (ValueError, TypeError) as e:
            return jsonify({
                'success': False,
                'error': 'تاريخ أو وقت غير صحيح'
            }), 400
        
        city_key = request.args.get('city', 'baghdad').lower().strip()
        
        # البحث عن المدينة
        city_data = CITIES_DB.get(city_key)
        if not city_data:
            city_data = CITIES_DB['baghdad']
        
        print(f"📊 Calculating for: {name}, {year}-{month}-{day} {hour}:{minute}, {city_data['name']}")
        
        # استيراد Kerykeion
        try:
            from kerykeion import AstrologicalSubject
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': f'Failed to import Kerykeion: {str(e)}'
            }), 500
        
        # حساب الخارطة مع online=False
        subject = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city_data['name'],
            lat=city_data['lat'],
            lng=city_data['lng'],
            tz_str=city_data['tz'],
            online=False
        )
        
        # تجهيز النتائج
        result = {
            'success': True,
            'data': {
                'sun': {
                    'sign': subject.sun.sign,
                    'degree': round(float(subject.sun.degree), 2),
                    'house': int(subject.sun.house) if hasattr(subject.sun, 'house') and subject.sun.house else None
                },
                'moon': {
                    'sign': subject.moon.sign,
                    'degree': round(float(subject.moon.degree), 2),
                    'house': int(subject.moon.house) if hasattr(subject.moon, 'house') and subject.moon.house else None
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
            'city_used': city_data['name'],
            'coordinates': {'lat': city_data['lat'], 'lng': city_data['lng']}
        }
        
        print(f"✅ Success! Sun in {result['data']['sun']['sign']}")
        return jsonify(result)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ ERROR: {str(e)}")
        print(error_trace)
        
        return jsonify({
            'success': False,
            'error': str(e),
            'debug': 'Check Vercel logs for details'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
