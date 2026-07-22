from flask import Flask, request, jsonify
from kerykeion import AstrologicalSubjectFactory  # ✅ استخدم Kerykeion
from kerykeion.chart_data_factory import ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer
import os

app = Flask(__name__)

SIGNS_AR = [
    'الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'العذراء',
    'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت'
]

CITIES = {
    'najaf': (32.0, 44.3333, 'النجف', 'Asia/Baghdad'),
    'baghdad': (33.3152, 44.3661, 'بغداد', 'Asia/Baghdad'),
    'basra': (30.5081, 47.7835, 'البصرة', 'Asia/Baghdad'),
    'cairo': (30.0444, 31.2357, 'القاهرة', 'Africa/Cairo'),
    'riyadh': (24.7136, 46.6753, 'الرياض', 'Asia/Riyadh'),
    'dubai': (25.2048, 55.2708, 'دبي', 'Asia/Dubai'),
    'amman': (31.9454, 35.9284, 'عمّان', 'Asia/Amman'),
    'beirut': (33.8938, 35.5018, 'بيروت', 'Asia/Beirut'),
    'damascus': (33.5138, 36.2765, 'دمشق', 'Asia/Damascus'),
    'london': (51.5074, -0.1278, 'لندن', 'Europe/London'),
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
        name = request.args.get('name', 'User')
        year = int(request.args.get('year', 1990))
        month = int(request.args.get('month', 1))
        day = int(request.args.get('day', 1))
        hour = int(request.args.get('hour', 12))
        minute = int(request.args.get('minute', 0))
        city_key = request.args.get('city', 'baghdad').lower().strip()
        
        city_data = CITIES.get(city_key)
        if not city_data:
            city_data = CITIES['najaf']
        
        lat, lng, city_name, tz_str = city_data
        
        # ✅ استخدام Kerykeion (وليس flatlib)
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            lng=lng,
            lat=lat,
            tz_str=tz_str,
            online=False,
        )
        
        # استخراج بيانات الكواكب
        result = {
            'success': True,
            'data': {},
            'city_used': city_name
        }
        
        planets = {
            'sun': subject.sun,
            'moon': subject.moon,
            'mercury': subject.mercury,
            'venus': subject.venus,
            'mars': subject.mars,
            'jupiter': subject.jupiter,
            'saturn': subject.saturn,
        }
        
        for key, planet in planets.items():
            sign_idx = planet.sign_num
            result['data'][key] = {
                'sign': planet.sign,
                'sign_ar': SIGNS_AR[sign_idx] if 0 <= sign_idx < 12 else 'غير معروف',
                'degree': round(planet.position, 2),
                'longitude': round(planet.abs_pos, 2),
                'retrograde': planet.retrograde,
            }
        
        # الطالع (Ascendant)
        result['data']['ascendant'] = {
            'sign': subject.first_house.sign,
            'sign_ar': SIGNS_AR[subject.first_house.sign_num] if 0 <= subject.first_house.sign_num < 12 else 'غير معروف',
            'degree': round(subject.first_house.position, 2),
            'longitude': round(subject.first_house.abs_pos, 2),
        }
        
        # MC (Midheaven)
        result['data']['midheaven'] = {
            'sign': subject.tenth_house.sign,
            'sign_ar': SIGNS_AR[subject.tenth_house.sign_num] if 0 <= subject.tenth_house.sign_num < 12 else 'غير معروف',
            'degree': round(subject.tenth_house.position, 2),
            'longitude': round(subject.tenth_house.abs_pos, 2),
        }
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
