from kerykeion import AstrologicalSubject
import json

def handler(request):
    """
    Vercel Python Serverless Function Handler
    لحساب الخارطة الفلكية الشخصية
    """
    
    # استخراج المعاملات من URL
    query_params = request.args
    
    try:
        # الحصول على البيانات من الطلب
        name = query_params.get('name', 'User')
        year = int(query_params.get('year', 1990))
        month = int(query_params.get('month', 1))
        day = int(query_params.get('day', 1))
        hour = int(query_params.get('hour', 12))
        minute = int(query_params.get('minute', 0))
        city = query_params.get('city', 'London')
        
        # حساب الخارطة الفلكية باستخدام Kerykeion
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
        
        # إرجاع النتيجة كـ JSON
        from flask import Response
        return Response(
            json.dumps(result, ensure_ascii=False, default=str),
            status=200,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json; charset=utf-8'
            }
        )
        
    except Exception as e:
        # معالجة الأخطاء
        from flask import Response
        error_result = {
            'success': False,
            'error': str(e)
        }
        return Response(
            json.dumps(error_result, ensure_ascii=False),
            status=400,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*'
            }
        )
