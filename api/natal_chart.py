from flask import Flask, request, jsonify
from kerykeion import AstrologicalSubject
import json

app = Flask(__name__)

# إعداد CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/natal_chart', methods=['GET', 'OPTIONS'])
def natal_chart():
    # معالجة OPTIONS request
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
        city = request.args.get('city', 'London')
        
        print(f"Calculating chart for: {name}, {year}-{month}-{day} {hour}:{minute}, {city}")
        
        # حساب الخارطة
        subject = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city,
            lng=0,  # سيتم حسابه تلقائياً من اسم المدينة
            lat=0
        )
        
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
            },
            'message': 'Chart calculated successfully'
        }
        
        print(f"Result: {json.dumps(result, ensure_ascii=False)}")
        return jsonify(result)
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'message': 'Failed to calculate chart'
        }
        print(f"Error: {str(e)}")
        return jsonify(error_result), 400

if __name__ == '__main__':
    app.run(debug=True)
