from flask import Flask, request, jsonify
from kerykeion import AstrologicalSubject
import json

app = Flask(__name__)

# قاعدة بيانات المدن العربية
ARAB_CITIES = {
    # العراق
    'baghdad': {'lat': 33.3152, 'lng': 44.3661, 'name': 'بغداد'},
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
    'anbar': {'lat': 33.4206, 'lng': 43.3078, 'name': 'الأنبار'},
    
    # السعودية
    'riyadh': {'lat': 24.7136, 'lng': 46.6753, 'name': 'الرياض'},
    'jeddah': {'lat': 21.4858, 'lng': 39.1925, 'name': 'جدة'},
    'mecca': {'lat': 21.3891, 'lng': 39.8579, 'name': 'مكة'},
    'medina': {'lat': 24.5247, 'lng': 39.5692, 'name': 'المدينة'},
    'dammam': {'lat': 26.3927, 'lng': 49.9777, 'name': 'الدمام'},
    'khobar': {'lat': 26.2172, 'lng': 50.1971, 'name': 'الخبر'},
    'tabuk': {'lat': 28.3835, 'lng': 36.5662, 'name': 'تبوك'},
    'abha': {'lat': 18.2164, 'lng': 42.5053, 'name': 'أبها'},
    
    # الإمارات
    'dubai': {'lat': 25.2048, 'lng': 55.2708, 'name': 'دبي'},
    'abu dhabi': {'lat': 24.4539, 'lng': 54.3773, 'name': 'أبوظبي'},
    'sharjah': {'lat': 25.3463, 'lng': 55.4209, 'name': 'الشارقة'},
    'ajman': {'lat': 25.4052, 'lng': 55.5136, 'name': 'عجمان'},
    
    # مصر
    'cairo': {'lat': 30.0444, 'lng': 31.2357, 'name': 'القاهرة'},
    'alexandria': {'lat': 31.2001, 'lng': 29.9187, 'name': 'الإسكندرية'},
    'giza': {'lat': 30.0131, 'lng': 31.2089, 'name': 'الجيزة'},
    'luxor': {'lat': 25.6872, 'lng': 32.6396, 'name': 'الأقصر'},
    'aswan': {'lat': 24.0889, 'lng': 32.8998, 'name': 'أسوان'},
    
    # الأردن
    'amman': {'lat': 31.9454, 'lng': 35.9284, 'name': 'عمّان'},
    'zarqa': {'lat': 32.0728, 'lng': 36.0876, 'name': 'الزرقاء'},
    'aqaba': {'lat': 29.5321, 'lng': 35.0063, 'name': 'العقبة'},
    
    # الكويت
    'kuwait': {'lat': 29.3759, 'lng': 47.9774, 'name': 'الكويت'},
    
    # قطر
    'doha': {'lat': 25.2854, 'lng': 51.5310, 'name': 'الدوحة'},
    
    # البحرين
    'manama': {'lat': 26.0667, 'lng': 50.5577, 'name': 'المنامة'},
    
    # عُمان
    'muscat': {'lat': 23.5880, 'lng': 58.3829, 'name': 'مسقط'},
    'salalah': {'lat': 17.0194, 'lng': 54.0897, 'name': 'صلالة'},
    
    # المغرب
    'rabat': {'lat': 34.0209, 'lng': -6.8416, 'name': 'الرباط'},
    'casablanca': {'lat': 33.5731, 'lng': -7.5898, 'name': 'الدار البيضاء'},
    'marrakech': {'lat': 31.6295, 'lng': -7.9811, 'name': 'مراكش'},
    'fes': {'lat': 34.0181, 'lng': -5.0078, 'name': 'فاس'},
    
    # تونس
    'tunis': {'lat': 36.8065, 'lng': 10.1815, 'name': 'تونس'},
    'sousse': {'lat': 35.8256, 'lng': 10.6369, 'name': 'سوسة'},
    
    # الجزائر
    'algiers': {'lat': 36.7538, 'lng': 3.0588, 'name': 'الجزائر'},
    'oran': {'lat': 35.6911, 'lng': -0.6417, 'name': 'وهران'},
    
    # لبنان
    'beirut': {'lat': 33.8938, 'lng': 35.5018, 'name': 'بيروت'},
    'tripoli': {'lat': 34.4367, 'lng': 35.8497, 'name': 'طرابلس'},
    
    # سوريا
    'damascus': {'lat': 33.5138, 'lng': 36.2765, 'name': 'دمشق'},
    'aleppo': {'lat': 36.2021, 'lng': 37.1343, 'name': 'حلب'},
    
    # فلسطين
    'jerusalem': {'lat': 31.7683, 'lng': 35.2137, 'name': 'القدس'},
    'gaza': {'lat': 31.3547, 'lng': 34.3088, 'name': 'غزة'},
    'ramallah': {'lat': 31.9038, 'lng': 35.2034, 'name': 'رام الله'},
    
    # اليمن
    'sanaa': {'lat': 15.3694, 'lng': 44.1910, 'name': 'صنعاء'},
    'aden': {'lat': 12.7797, 'lng': 45.0367, 'name': 'عدن'},
    
    # ليبيا
    'tripoli libya': {'lat': 32.8872, 'lng': 13.1913, 'name': 'طرابلس'},
    'benghazi': {'lat': 32.1194, 'lng': 20.0869, 'name': 'بنغازي'},
    
    # السودان
    'khartoum': {'lat': 15.5007, 'lng': 32.5599, 'name': 'الخرطوم'},
    
    # مدن عالمية
    'london': {'lat': 51.5074, 'lng': -0.1278, 'name': 'لندن'},
    'paris': {'lat': 48.8566, 'lng': 2.3522, 'name': 'باريس'},
    'new york': {'lat': 40.7128, 'lng': -74.0060, 'name': 'نيويورك'},
    'los angeles': {'lat': 34.0522, 'lng': -118.2437, 'name': 'لوس أنجلوس'},
    'istanbul': {'lat': 41.0082, 'lng': 28.9784, 'name': 'إسطنبول'},
    'berlin': {'lat': 52.5200, 'lng': 13.4050, 'name': 'برلين'},
    'moscow': {'lat': 55.7558, 'lng': 37.6173, 'name': 'موسكو'},
    'tokyo': {'lat': 35.6762, 'lng': 139.6503, 'name': 'طوكيو'},
    'beijing': {'lat': 39.9042, 'lng': 116.4074, 'name': 'بكين'},
    'mumbai': {'lat': 19.0760, 'lng': 72.8777, 'name': 'مومباي'},
}

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/api/natal_chart', methods=['GET', 'OPTIONS'])
def natal_chart():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # استخراج المعاملات
        name = request.args.get('name', 'User')
        year = request.args.get('year', type=int, default=1990)
        month = request.args.get('month', type=int, default=1)
        day = request.args.get('day', type=int, default=1)
        hour = request.args.get('hour', type=int, default=12)
        minute = request.args.get('minute', type=int, default=0)
        city_input = request.args.get('city', 'London').lower().strip()
        
        print(f"🔍 البحث عن مدينة: {city_input}")
        
        # البحث عن المدينة في قاعدة البيانات
        city_data = None
        for city_key, city_info in ARAB_CITIES.items():
            if city_input in city_key or city_key in city_input:
                city_data = city_info
                break
        
        if city_data:
            lat = city_data['lat']
            lng = city_data['lng']
            city_name = city_data['name']
            print(f"✅ تم العثور على المدينة: {city_name} ({lat}, {lng})")
        else:
            # إذا لم توجد المدينة، استخدم لندن كافتراضي
            lat = 51.5074
            lng = -0.1278
            city_name = 'London (default)'
            print(f"⚠️ لم يتم العثور على المدينة، استخدام لندن كافتراضي")
        
        # حساب الخارطة
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
                    'degree': round(subject.sun.degree, 2),
                    'house': subject.sun.house if hasattr(subject.sun, 'house') else None
                },
                'moon': {
                    'sign': subject.moon.sign,
                    'degree': round(subject.moon.degree, 2),
                    'house': subject.moon.house if hasattr(subject.moon, 'house') else None
                },
                'mercury': {
                    'sign': subject.mercury.sign,
                    'degree': round(subject.mercury.degree, 2),
                    'house': subject.mercury.house if hasattr(subject.mercury, 'house') else None
                },
                'venus': {
                    'sign': subject.venus.sign,
                    'degree': round(subject.venus.degree, 2),
                    'house': subject.venus.house if hasattr(subject.venus, 'house') else None
                },
                'mars': {
                    'sign': subject.mars.sign,
                    'degree': round(subject.mars.degree, 2),
                    'house': subject.mars.house if hasattr(subject.mars, 'house') else None
                },
                'jupiter': {
                    'sign': subject.jupiter.sign,
                    'degree': round(subject.jupiter.degree, 2),
                    'house': subject.jupiter.house if hasattr(subject.jupiter, 'house') else None
                },
                'saturn': {
                    'sign': subject.saturn.sign,
                    'degree': round(subject.saturn.degree, 2),
                    'house': subject.saturn.house if hasattr(subject.saturn, 'house') else None
                },
                'uranus': {
                    'sign': subject.uranus.sign,
                    'degree': round(subject.uranus.degree, 2),
                    'house': subject.uranus.house if hasattr(subject.uranus, 'house') else None
                },
                'neptune': {
                    'sign': subject.neptune.sign,
                    'degree': round(subject.neptune.degree, 2),
                    'house': subject.neptune.house if hasattr(subject.neptune, 'house') else None
                },
                'pluto': {
                    'sign': subject.pluto.sign,
                    'degree': round(subject.pluto.degree, 2),
                    'house': subject.pluto.house if hasattr(subject.pluto, 'house') else None
                },
                'ascendant': {
                    'sign': subject.ascendant.sign,
                    'degree': round(subject.ascendant.degree, 2)
                },
                'midheaven': {
                    'sign': subject.midheaven.sign,
                    'degree': round(subject.midheaven.degree, 2)
                }
            },
            'city_used': city_name,
            'coordinates': {'lat': lat, 'lng': lng}
        }
        
        print(f"✅ تم الحساب بنجاح لـ {name}")
        return jsonify(result)
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'message': 'فشل في حساب الخارطة'
        }
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify(error_result), 500

if __name__ == '__main__':
    app.run(debug=True)
