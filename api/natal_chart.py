from flask import Flask, request, jsonify
import sys
import traceback

app = Flask(__name__)

@app.route('/api/natal_chart', methods=['GET', 'OPTIONS'])
def natal_chart():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # 1. اختبار استيراد المكتبة (هنا يكمن اللغز)
        try:
            from kerykeion import AstrologicalSubject
            import_status = "SUCCESS"
        except Exception as import_err:
            import_status = f"FAILED: {str(import_err)}"
            return jsonify({
                'success': False,
                'error': 'فشل استيراد Kerykeion',
                'import_error': import_status,
                'hint': 'المشكلة في تثبيت pyswisseph على Vercel'
            }), 500

        # 2. استخراج البيانات
        name = request.args.get('name', 'User')
        year = int(request.args.get('year', 1990))
        month = int(request.args.get('month', 1))
        day = int(request.args.get('day', 1))
        hour = int(request.args.get('hour', 12))
        minute = int(request.args.get('minute', 0))
        city = request.args.get('city', 'baghdad').lower()
        
        # بيانات النجف كبداية
        if city == 'najaf':
            lat, lng, tz_str, city_name, nation = 32.0000, 44.3333, 'Asia/Baghdad', 'النجف', 'Iraq'
        else:
            lat, lng, tz_str, city_name, nation = 33.3152, 44.3661, 'Asia/Baghdad', 'بغداد', 'Iraq'

        # 3. الحساب
        subject = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city_name,
            nation=nation,
            lng=lng,
            lat=lat,
            tz_str=tz_str,
            online=False
        )

        return jsonify({
            'success': True,
            'import_status': import_status,
            'data': {
                'sun': {'sign': subject.sun.sign, 'degree': float(subject.sun.degree)},
                'moon': {'sign': subject.moon.sign, 'degree': float(subject.moon.degree)},
                'ascendant': {'sign': subject.ascendant.sign, 'degree': float(subject.ascendant.degree)}
            }
        })

    except Exception as e:
        # التقاط أي خطأ آخر وإرجاعه كنص واضح
        error_details = traceback.format_exc()
        print("CRASH DETAILS:", error_details, file=sys.stderr)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_details
        }), 500

if __name__ == '__main__':
    app.run()
