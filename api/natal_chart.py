from kerykeion import AstrologicalSubject
import json

def handler(request):
    """
    Vercel Python Serverless Function
    """
    # GET request - استخراج المعاملات من URL
    query_params = request.args
    
    try:
        name = query_params.get('name', 'User')
        year = int(query_params.get('year', 1990))
        month = int(query_params.get('month', 1))
        day = int(query_params.get('day', 1))
        hour = int(query_params.get('hour', 12))
        minute = int(query_params.get('minute', 0))
        city = query_params.get('city', 'London')
        
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
            'sun': {
                'sign': subject.sun.sign,
                'degree': round(subject.sun.degree, 2),
                'house': subject.sun.house
            },
            'moon': {
                'sign': subject.moon.sign,
                'degree': round(subject.moon.degree, 2),
                'house': subject.moon.house
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
        
        # إرجاع النتيجة كـ JSON
        from flask import Response
        return Response(
            json.dumps(result, ensure_ascii=False),
            status=200,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        from flask import Response
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
