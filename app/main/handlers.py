# -*- coding: utf-8 -*-


import json
import requests
from app.main import bp
from flask_restful import reqparse
from datetime import datetime
from flask import jsonify





def time_window_url(paths, public=True, lookback = 7, start_date = False, end_date = False, timezone = 'PST'):
    """
    helper function for cwms_read
    
    Arguments:  
        
        path -- cwms data path, 
        public -- boolean, 
        start_date -- date integer tuple format (YYYY, m, d)
        end_date -- date integer tuple format (YYYY, m, d)
        timezone -- optional keyword argument if time zone is specified.  
                    Defaults to 'PST' if nothing set
    Returns:
        
        url -- url string of CWMS data webservice for the specified 
               data path and time window
               
    """

    if isinstance(paths, list): 
        path = '%22%2C%22'.join(paths)
    else: path = paths
        
    if public:
        url = r'http://pweb.crohms.org/dd/common/web_service/webexec/getjson?timezone=TIMEZONE_&query=%5B%22PATH%22%5D&'
    else:
        url = r'http://nwp-wmlocal2.nwp.usace.army.mil/common/web_service/webexec/getjson?timezone=TIMEZONE_&query=%5B%22PATH%22%5D&'
    
    url = url.replace('PATH', path).replace('TIMEZONE_', timezone)
    if lookback:
        time = 'backward=' + str(lookback) + 'd'
        url = url + time
    else:
        url = url + 'startdate=START_MONTH%2FSTART_DAY%2FSTART_YEAR+00%3A00&enddate=END_MONTH%2FEND_DAY%2FEND_YEAR+23%3A00'
        url = url.replace('START_MONTH', str(start_date.month)).replace('START_DAY', str(start_date.day)).replace('START_YEAR', str(start_date.year))
        url = url.replace('END_MONTH', str(end_date.month)).replace('END_DAY', str(end_date.day)).replace('END_YEAR', str(end_date.year))
    
    return url



@bp.route('/cwms', methods = ['GET', 'POST'])
def cwms():
    parser = reqparse.RequestParser()
    parser.add_argument('paths', action='append')
    parser.add_argument('lookback', type=int)
    parser.add_argument('startdate', type=lambda x: datetime.strptime(x,'%Y-%m-%d') )
    parser.add_argument('enddate', type=lambda x: datetime.strptime(x,'%Y-%m-%d') )
    args = parser.parse_args()
    paths = args['paths']
    lookback = args['lookback']
    if lookback:
        start_date = False
        end_date = False
    else:
        start_date = args['startdate']
        end_date = args['enddate']
        lookback = False
    url = time_window_url(paths, public=True, lookback = lookback, start_date = start_date, end_date = end_date, timezone = 'GMT')
    requests.packages.urllib3.disable_warnings() 
    data = json.loads(requests.get(url, verify = False).text)
    print(url)
    data_list = []
    for key,value in data.items():
        print(value.keys())
        lat = value['coordinates']['latitude']
        long = value['coordinates']['longitude']
        name = value['name']
        for k,v in value['timeseries'].items():
            v['pathname'] = k
            v['latitude'] = lat
            v['longitude'] = long
            v['name'] = name
            vals = []
            for val in v['values']:
                vals.append({'date':val[0],'value':val[1],'flag':val[2]})
            v['values'] = vals
            data_list.append(v)
    return jsonify(data_list)
