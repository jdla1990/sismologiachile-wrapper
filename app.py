import bottle
import SismoStore
from sys import argv
from json import dumps, loads
from bottle import route, run, response, request, post

bottle.debug(True)

@bottle.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@route('/sismos/ultimos')
def ultimos():
    response.content_type = 'application/json; charset=utf-8'
    try:
        return dumps({'status' : 1, 'data' : SismoStore.get_lasted()})
    except Exception as ex:
        return dumps({'status' : 0})

@post('/sismo/detail')
def detail_sismo():
    response.content_type = 'application/json; charset=utf-8'
    
    path = request.json
    detail = SismoStore.detail_sismo(path['path'])
    if detail:
        return dumps({'status': 1, 'data': detail })
    else:
        return dumps({'status': 0 })

@route('/cache/clear')
def clear_cache():
    response.content_type = 'application/json; charset=utf-8'
    SismoStore.clear_details_cached()
    return dumps({'status':1})

@route('/')
def index():
    response.content_type = 'application/json; charset=utf-8'
    return dumps({'status':'OK'})


bottle.run(host='0.0.0.0', port=argv[1])