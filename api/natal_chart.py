from flask import Flask, request, jsonify, Response
from kerykeion import AstrologicalSubject
import json

app = Flask(__name__)

@app.route('/api/natal_chart', methods=['GET', 'OPTIONS'])
def natal_chart():
    """
    API endpoint لحساب الخارطة الفلكية
    """
    # معالجة CORS preflight
    if request.method == 'OPTIONS':
        response = Response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    try:
        # استخراج المعاملات من URL
        name = request.args.get('name', 'User')
        year = int(request.args.get('year', 1990))
        month = int(request.args.get('month', 1))
        day = int(request.args.get('day', 1))
        hour = int(request.args.get('hour', 12))
        minute = int(request.args.get('minute', 0))
        city = request.args.get('city', 'London')
        
        # حساب الخارطة الفلكية
        subject = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city
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
                'ascendant': {
                    'sign': subject.ascendant.sign,
                    'degree': round(subject.ascendant.degree, 2)
                },
                'midheaven': {
                    'sign': subject.midheaven.sign,
                    'degree': round(subject.midheaven.degree, 2)
                }
            }
        }
        
        # إرجاع النتيجة
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Content-Type', 'application/json; charset=utf-8')
        return response
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        response = jsonify(error_result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.status_code = 400
        return response

# هذا السطر مهم جداً لـ Vercel!
if __name__ == '__main__':
    app.run()
