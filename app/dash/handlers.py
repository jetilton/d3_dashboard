from app import db
from flask import render_template, url_for, flash, redirect, request
from app.models import Cbt, Paths
import pandas as pd
import numpy as np
import datetime
from app.dash import bp
from cwms_read.cwms_read import get_cwms
from flask import jsonify

def water_year(row,month=7):
    if row['month']>month:
        return row['year'] +1
    else:return row['year']

def get_date(row, now):
    if row['month'] >= 8:
        year = now.year-1
    else:
        year =  now.year
    return '-'.join([str(year),str(int(row['month'])),str(int(row['day']))])
        

@bp.route('/<cbt>/dash', methods = ['GET'])
def dash_cbt(cbt):
    return render_template('dash/dash.html', cbt=cbt)
    
    
@bp.route('/hydrographdata/<cbt>', methods = ['GET'])
def dash_data(cbt):
    now = datetime.datetime.utcnow()
    cbt = Cbt.query.filter_by(cbt=cbt).first()
    obs_flow_path = Paths.query.filter_by(cbt=cbt.cbt, parameter = 'Flow In').first().path
    print(obs_flow_path)
    obs_flow = get_cwms(paths = obs_flow_path, 
                        col_names = ['obs_flow'], lookback = 30000, timezone = 'GMT')
    
    obs_meta = obs_flow.__dict__['metadata']
    obs_meta['obs_flow'].pop('flags')
    obs_flow_diff = obs_flow.diff()
    
    #de-spike
    obs_flow = obs_flow[(obs_flow_diff["obs_flow"]<obs_flow_diff["obs_flow"].mean()+\
              obs_flow_diff["obs_flow"].std()*6) &\
            (obs_flow_diff["obs_flow"]>obs_flow_diff["obs_flow"].mean()-\
              obs_flow_diff["obs_flow"].std()*6)]
    obs_flow = obs_flow[(obs_flow_diff["obs_flow"]<obs_flow_diff["obs_flow"].mean()+\
              obs_flow_diff["obs_flow"].std()*6) &\
            (obs_flow_diff["obs_flow"]>obs_flow_diff["obs_flow"].mean()-\
              obs_flow_diff["obs_flow"].std()*6)]
    obs_flow = obs_flow.groupby(pd.Grouper(freq = 'd')).mean()          
    
    #get columns to use in transpose/pivot
    obs_flow.reset_index(inplace = True)
    obs_flow['month'] = [x.month for x in obs_flow['date']]
    obs_flow['day'] = [x.day for x in obs_flow['date']]
    obs_flow['year'] = [x.year for x in obs_flow['date']]
    obs_flow['water_year'] = obs_flow.apply(water_year,axis = 1)
    obs_flow.set_index('date', inplace = True)
    
    obs_pivot = pd.pivot_table(obs_flow,index=['month', 'day'],columns=['water_year'],
               values='obs_flow',aggfunc=np.sum)
    
    #don't want to use current year in quantile calcs
    obs_pivot = obs_pivot.loc[:,:now.year-1]
    quants = [i/100.0 for i in range(0, 105, 5)]
    obs_quant = pd.DataFrame(data = obs_pivot.quantile(q = float(quants[0]),axis = 1))
    obs_quant.columns = ['0.00']
    for quant in quants[1:]:
        obs_quant['{0:.2f}'.format(quant)] = obs_pivot.quantile(q = float(quant),axis = 1)
    obs_quant.reset_index(inplace = True)
    #set dates for easier plotting
    wy_start_index =obs_quant[(obs_quant['month']==8) &(obs_quant['day']==1)].index[0]
    this_year = obs_quant.iloc[wy_start_index:]
    next_year = obs_quant.iloc[:wy_start_index]
    obs = pd.concat([this_year,next_year])
    obs['date'] = obs.apply(get_date,now=now,axis = 1)
    obs.set_index('date', inplace = True)
    timeseries = {}
    for column in obs.loc[:,'0.00':].columns:
        print(column)
        ts = [{'date':i, 'value':v} for i,v in obs[column].iteritems()]
        timeseries.update({column:ts})
    current_year = obs_flow[obs_flow['water_year']==now.year]
    current_year_vals = [{'date':str(i).split(' ')[0], 'value':v} for i,v in current_year['obs_flow'].iteritems()]
    obs_meta['obs_flow'].update({'timeseries':{'current_year':current_year_vals,'quantiles':timeseries}})
    
    
    #get forecast data
    fcst = {'quantiles': timeseries}
    
    
    data = {'obs':obs_meta, 'fcst': fcst}
    return jsonify(data)



