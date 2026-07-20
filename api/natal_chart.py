from kerykeion import AstrologicalSubject
import json

def handler(event, context):
    # GET request
    if 'queryStringParameters' in event:
        query = event['queryStringParameters']
        
        subject = AstrologicalSubject(
            name=query.get('name', 'User'),
            year=int(query.get('year', 1990)),
            month=int(query.get('month', 1)),
            day=int(query.get('day', 1)),
            hour=int(query.get('hour', 12)),
            minute=int(query.get('minute', 0)),
            city=query.get('city', 'London')
        )
        
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, ensure_ascii=False)
        }
    
    return {
        'statusCode': 400,
        'body': json.dumps({'error': 'Invalid request'})
    }
