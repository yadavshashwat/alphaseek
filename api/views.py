from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponse
from django.core.paginator import Paginator
from django.core import serializers
from datascrape.models import *
from strategytest.models import *
from django.db.models import Q, Max, Min
from overall.views import get_param,cleanstring,booleanvar_check, listvar_check, intvar_check, floatvar_check
import json
import operator
import math
from django.views.decorators.csrf import csrf_exempt
import pandas as pd


# operations_allowed_default = ['create','read','update','delete']
operations_allowed_default = ['read']

# Create your views here.

# CRUD for exchange

def create_update_exchange(request):
    error = False
    success = False
    error_message_list = []
    output = Exchange.objects.none()
    message = "Request Recieved"
    operation               = get_param(request, 'operation', None)
    exchange_name           = get_param(request, 'exchange_name', None)      
    exchange_code           = get_param(request, 'exchange_code', None)      
    exchange_country        = get_param(request, 'exchange_country', None)  
    exchange_timezone        = get_param(request, 'exchange_timezone', None)  
    exchange_timezone_short = get_param(request, 'exchange_timezone_short', None) 
    timezone_gmt_off_milliseconds = get_param(request, 'timezone_gmt_off_milliseconds', None)  
    data_id                 = get_param(request, 'data_id', None)      
    # user fields check and correction
    if exchange_name:
        exchange_name = cleanstring(exchange_name)
    else:
        error = True
        error_message_list.append("Missing exchange_name")                               

    if exchange_code:
        exchange_code = cleanstring(exchange_code)
    else:
        if operation=="update":
            pass
        else:
            error = True
            error_message_list.append("Missing exchange_code")                               

    if exchange_timezone:
        exchange_timezone = cleanstring(exchange_timezone)
    else:
        error = True
        error_message_list.append("Missing exchange_timezone")                               


    if exchange_country:
        exchange_country = cleanstring(exchange_country)
    else:
        error = True
        error_message_list.append("Missing exchange_country")                               

    if exchange_timezone_short:
        pass
    else:
        error = True
        error_message_list.append("Missing exchange_timezone_short")                               

    check_time = intvar_check(variable_name="timezone_gmt_off_milliseconds",value=timezone_gmt_off_milliseconds)
    if not check_time['error']:
        timezone_gmt_off_milliseconds = check_time['output']
    else:
        error = check_time['error']
        error_message_list.append(check_time['errormessage'])    

    if operation == "update":
        if data_id:
            try:
                exchange = Exchange.objects.get(id=data_id)
            except:
                error = True
                error_message_list = ['invalid data_id']
        else:
            error = True
            error_message_list = ['missing data_id']
        
    if not error: 
        if operation == "create":
            exchange = Exchange.objects.filter(
                exchange_code=exchange_code
                )
            if exchange.count() > 0 :
                message = "Exchange Already Exists!"        
                output = exchange
                success = False
            else:
                exchange_new = Exchange.objects.create(
                exchange_name = exchange_name
                ,exchange_code = exchange_code
                ,exchange_country = exchange_country
                ,exchange_timezone = exchange_timezone
                ,exchange_timezone_short = exchange_timezone_short
                ,timezone_gmt_off_milliseconds = timezone_gmt_off_milliseconds
                )
                output = [exchange_new]
                success = True
                message = "Exchange Created!"
        else:
            print(exchange_code)
            print(exchange.exchange_code)
            if exchange_code == exchange.exchange_code:
                exchange.exchange_name = exchange_name   
                exchange.exchange_country = exchange_country   
                exchange.exchange_timezone = exchange_timezone   
                exchange.exchange_timezone_short = exchange_timezone_short   
                exchange.timezone_gmt_off_milliseconds = timezone_gmt_off_milliseconds   
                exchange.save()
                success = True
                message = "Exchange Updated!"
                output = [exchange]
            else:
                error = True
                success = False
                error_message_list.append('exchnage code cant be changed exists')
                message = "Exchange code cant be changed"
                output = [exchange]
    else:
        message = "Errors | Refer Error List!"

    return {'output':output,'message':message,'error':error,'error_message_list':error_message_list,'success':success}

def delete_exchange(request):
    error = False
    success = False
    error_message_list = []
    data_id      = get_param(request, 'data_id', None)
    output = Exchange.objects.none()
    message = "Request Recieved"
    if data_id:
        try:
            exchange = Exchange.objects.get(id=data_id)
        except:
            error=True
            error_message_list.append('Incorrect data_id')
    else:
        error = True
        error_message_list.append('Missing data_id')
    if not error: 
        if exchange:
            exchange.delete()
            message = "Exchange Deleted"
            success = True
        else:
            message = "Exchange not found"
            success = False
    else:
        message = "Errors | Refer Error List!"

    return {'output':output,'message':message,'error':error,'error_message_list':error_message_list,'success':success}

def read_exchange(request):
    error = False
    success = False
    error_message_list = []
    message = "Request Recieved!"
    filters = {}
    num_pages = 1
    total_records = 0 
    tranObjs = Exchange.objects.none()
    page_num = get_param(request, 'page_num', "1")
    page_size = get_param(request, 'page_size', "10")
    search = get_param(request,'search',None) 
    sort_by = get_param(request,'sort_by',None) 
    order = get_param(request,'order_by',None)    
    exchange_country = get_param(request,'exchange_country',None) 
    data_id = get_param(request,'data_id',None)    
    
    if data_id != None and data_id != "":
        tranObjs = Exchange.objects.filter(id=data_id)
    else:
        tranObjs = Exchange.objects.all()

        if exchange_country !=None and exchange_country !="" and exchange_country != "none":
            exchange_country_list = exchange_country.split(",")
            tranObjs = tranObjs.filter(exchange_country__in=exchange_country_list)

        # Filters/Sorting Start
        if search !=None and search !="":
            tranObjs = tranObjs.filter(Q(exchange_code__icontains=search) | Q(exchange_name__icontains=search))

        if sort_by !=None and sort_by !="" and sort_by != "none":
            if order == "asc":
                tranObjs = tranObjs.order_by(sort_by)
            else:
                tranObjs = tranObjs.order_by("-" + sort_by)
        # Filters/Sorting End
    # pagination variable

    total_records = tranObjs.count()    
    if page_num != None and page_num != "":
        page_num = int(page_num)
        tranObjs = Paginator(tranObjs, int(page_size))
        try:
            tranObjs = tranObjs.page(page_num)
        except:
            tranObjs = tranObjs
        num_pages = int(math.ceil(total_records / float(int(page_size))))
    # data = list(tranObjs)
    message  = "Success!"
    success = True
    
    exchange_country_list = Exchange.objects.all()
    filters['exchange_country'] = []
    for item in exchange_country_list:
        filters['exchange_country'].append({
            'value':item.exchange_country,
            'label':(item.exchange_country).title()
            })
    filters['exchange_country'] = {v['value']:v for v in filters['exchange_country']}.values()
    filters['exchange_country'] = sorted(filters['exchange_country'], key=operator.itemgetter('value'))

    filters['sort_by'] = [
                        {'value':'exchange_country','label':'Exchange Country'},
                        {'value':'exchange_name','label':'Exchange Name'},
                        {'value':'exchange_code','label':'Exchange Code'}
                       ]
                

    filters['order_by'] = [{'value':'asc','label':'Ascending'},
                           {'value':'desc','label':'Descending'}]

    return({
        'output':tranObjs,
        'num_pages':num_pages,
        'total_records':total_records,
        'error':error,
        'error_message_list':error_message_list,
        'filter':filters,
        'message':message,
        'success':success
    })

def crud_exchange(request):
    obj = {}
    status = False
    result = []
    message = "Request Recieved"
    filters = {}
    tranObjs = Exchange.objects.none()
    operation = get_param(request, 'operation', None)
    error = False
    error_message_list = []
    num_pages = 1
    total_records = 0 
    
    check_operation = listvar_check(variable_name='operation',value=operation,allowedlist=operations_allowed_default)
    if not check_operation['error']:
        if operation == "read":
            out_read_exchange = read_exchange(request) 
            message = out_read_exchange['message']               
            tranObjs = out_read_exchange['output']
            error_message_list.extend(out_read_exchange['error_message_list'])               
            error = out_read_exchange['error']     
            status = out_read_exchange['success']     
            num_pages     = out_read_exchange['num_pages']          
            filters       = out_read_exchange['filter']     
            total_records = out_read_exchange['total_records']          

        if operation in ["create","update"]:
            out_create_update_exchange = create_update_exchange(request) 
            message = out_create_update_exchange['message']               
            tranObjs = out_create_update_exchange['output']
            error_message_list.extend(out_create_update_exchange['error_message_list'])               
            error = out_create_update_exchange['error']   
            status = out_create_update_exchange['success']          

        if operation == "delete":
            out_delete_exchange = delete_exchange(request) 
            message = out_delete_exchange['message']               
            tranObjs = out_delete_exchange['output']               
            error_message_list.extend(out_delete_exchange['error_message_list'])               
            error = out_delete_exchange['error']     
            status = out_delete_exchange['success']           

        if not error:
            for trans in tranObjs:
                result.append({
                    'id':trans.id
                    ,'exchange_name':trans.exchange_name
                    ,'exchange_code':trans.exchange_code
                    ,'exchange_country':trans.exchange_country
                    ,'exchange_timezone':trans.exchange_timezone
                    ,'exchange_timezone_short':trans.exchange_timezone_short
                    ,'exchange_currency':trans.exchange_currency
                    ,'timezone_gmt_off_milliseconds':trans.timezone_gmt_off_milliseconds
                    ,'created_at':str(trans.created_at)[:19]
                    ,'modified_at':str(trans.modified_at)[:19]
                })
    
    else:
        error = check_operation['error']
        message = "Operation Not Specified"
        error_message_list.append(check_operation['errormessage'])

    obj['result'] = result
    obj['filter'] = filters
    obj['num_pages'] = num_pages
    obj['total_records'] = total_records
    obj['message'] = message
    obj['status'] = status
    obj['error'] = error
    obj['error_list'] = error_message_list
    return HttpResponse(json.dumps(obj), content_type='application/json')

# CRUD for companies

def read_company(request):
    error = False
    success = False
    error_message_list = []
    message = "Request Recieved!"
    filters = {}
    num_pages = 1
    total_records = 0 
    tranObjs = Company.objects.none()
    page_num = get_param(request, 'page_num', "1")
    page_size = get_param(request, 'page_size', "10")
    search = get_param(request,'search',None) 
    sort_by = get_param(request,'sort_by',None) 
    order = get_param(request,'order_by',None)    
    data_id = get_param(request,'data_id',None)
    
    if data_id != None and data_id != "":
        tranObjs = Company.objects.filter(id=data_id)
    else:
        tranObjs = Company.objects.all()

        # Filters/Sorting Start
        if search !=None and search !="":
            tranObjs = tranObjs.filter(Q(name__icontains=search) | Q(nse_ticker__icontains=search))

        if sort_by !=None and sort_by !="" and sort_by != "none":
            if order == "asc":
                tranObjs = tranObjs.order_by(sort_by)
            else:
                tranObjs = tranObjs.order_by("-" + sort_by)
        # Filters/Sorting End
    # pagination variable

    total_records = tranObjs.count()    
    if page_num != None and page_num != "":
        page_num = int(page_num)
        tranObjs = Paginator(tranObjs, int(page_size))
        try:
            tranObjs = tranObjs.page(page_num)
        except:
            tranObjs = tranObjs
        num_pages = int(math.ceil(total_records / float(int(page_size))))
    # data = list(tranObjs)
    message  = "Success!"
    success = True
    
    filters['sort_by'] = [
                        {'value':'name','label':'Name'},
                        {'value':'isin_no','label':'ISIN Number'},
                        {'value':'nse_ticker','label':'Company NSE Code'},
                        {'value':'nse_return_1d','label':'1 Day NSE Return'},
                        {'value':'nse_return_1m','label':'1 Month NSE Return'},
                        {'value':'nse_return_1y','label':'1 Year NSE Return'},
                        {'value':'nse_annualized_return','label':'Average NSE Return'},
                        {'value':'nse_annualized_vol','label':'Volatility NSE Return'},
                        {'value':'nse_volume','label':'Volume Traded NSE'}
                        ]   

    filters['order_by'] = [{'value':'asc','label':'Ascending'},
                           {'value':'desc','label':'Descending'}]

    return({
        'output':tranObjs,
        'num_pages':num_pages,
        'total_records':total_records,
        'error':error,
        'error_message_list':error_message_list,
        'filter':filters,
        'message':message,
        'success':success
    })

def crud_company(request):
    obj = {}
    status = False
    result = []
    message = "Request Recieved"
    filters = {}
    tranObjs = Exchange.objects.none()
    operation = get_param(request, 'operation', None)
    error = False
    error_message_list = []
    num_pages = 1
    total_records = 0 
    
    check_operation = listvar_check(variable_name='operation',value=operation,allowedlist=operations_allowed_default)
    if not check_operation['error']:
        if operation == "read":
            # pass
            out_read_company = read_company(request) 
            message = out_read_company['message']               
            tranObjs = out_read_company['output']
            error_message_list.extend(out_read_company['error_message_list'])               
            error = out_read_company['error']     
            status = out_read_company['success']     
            num_pages     = out_read_company['num_pages']          
            filters       = out_read_company['filter']     
            total_records = out_read_company['total_records']          

        if operation in ["create","update"]:
            pass
            # out_create_update_exchange = create_update_exchange(request) 
            # message = out_create_update_exchange['message']               
            # tranObjs = out_create_update_exchange['output']
            # error_message_list.extend(out_create_update_exchange['error_message_list'])               
            # error = out_create_update_exchange['error']   
            # status = out_create_update_exchange['success']          

        if operation == "delete":
            pass
            # out_delete_exchange = delete_exchange(request) 
            # message = out_delete_exchange['message']               
            # tranObjs = out_delete_exchange['output']               
            # error_message_list.extend(out_delete_exchange['error_message_list'])               
            # error = out_delete_exchange['error']     
            # status = out_delete_exchange['success']           

        if not error:
            for trans in tranObjs:
                TickerData = TickerHistoricDay.objects.filter(company=trans)
                first_nse_ticker_date = TickerData.aggregate(Min('date'))
                last_nse_ticker_date = TickerData.aggregate(Max('date'))
                result.append({
                    'id':trans.id
                    ,'name':trans.name
                    ,'isin_no':trans.isin_no
                    ,'is_listed_nse':trans.is_listed_nse
                    ,'nse_ticker':trans.nse_ticker
                    ,'industry_sector':trans.industry_sector
                    ,'nse_tracker':trans.nse_tracker
                    ,'nse_price_update_db_date':str(trans.nse_price_update_db_date)[:19]
                    ,'nse_return_update_date':str(trans.nse_return_update_date)[:19]
                    ,'created_at':str(trans.created_at)[:19]
                    ,'modified_at':str(trans.modified_at)[:19]
                    ,'min_nse_ticker_date':str(first_nse_ticker_date['date__min'])
                    ,'last_nse_ticker_date':str(last_nse_ticker_date['date__max'])
                    ,'total_nse_prices':TickerData.count()
                    ,'nse_return_date':str(trans.nse_return_date)[:19]
                    ,'nse_return_1d':trans.nse_return_1d
                    ,'nse_return_1m':trans.nse_return_1m
                    ,'nse_return_1y':trans.nse_return_1y
                    ,'nse_annualized_return':trans.nse_annualized_return
                    ,'nse_annualized_vol':trans.nse_annualized_vol
                    ,'nse_trade_date':str(trans.nse_trade_date)[:19]
                    ,'nse_price_high':trans.nse_price_high
                    ,'nse_price_low':trans.nse_price_low
                    ,'nse_price_close':trans.nse_price_close
                    ,'nse_price_open':trans.nse_price_open
                    ,'nse_price_close_adjusted':trans.nse_price_close_adjusted
                    ,'nse_volume':trans.nse_volume
                })
    
    else:
        error = check_operation['error']
        message = "Operation Not Specified"
        error_message_list.append(check_operation['errormessage'])

    obj['result'] = result
    obj['filter'] = filters
    obj['num_pages'] = num_pages
    obj['total_records'] = total_records
    obj['message'] = message
    obj['status'] = status
    obj['error'] = error
    obj['error_list'] = error_message_list
    return HttpResponse(json.dumps(obj), content_type='application/json')

def read_company_prices(request):
    error = False
    success = False
    error_message_list = []
    message = "Request Recieved!"
    filters = {}
    num_pages = 1
    total_records = 0 
    tranObjs = TickerHistoricDay.objects.none()

    sort_by = get_param(request,'sort_by',None) 
    order = get_param(request,'order_by',None)    
    data_id = get_param(request,'data_id',None)
    ticker = get_param(request,'ticker',None)
    isin = get_param(request,'isin',None)
    no_parameter = 0
    if data_id != None and data_id != "":
        tranObjs = TickerHistoricDay.objects.filter(company__id=data_id)
    elif ticker != None and ticker != "":
        tranObjs = TickerHistoricDay.objects.filter(company__nse_ticker=ticker)
    elif isin != None and isin != "":
        tranObjs = TickerHistoricDay.objects.filter(company__isin_no=isin)
    else:
        no_parameter = 1
        tranObjs = TickerHistoricDay.objects.none()

    total_records = tranObjs.count()    

    if no_parameter == 1:
        message = "No parameter shared"
    else:
        message  = "Success!"
    success = True
    
    filters['sort_by'] = [
                        {'value':'date','label':'Date'},
                       ]
                

    filters['order_by'] = [{'value':'asc','label':'Ascending'},
                           {'value':'desc','label':'Descending'}]

    return({
        'output':tranObjs,
        'num_pages':num_pages,
        'total_records':total_records,
        'error':error,
        'error_message_list':error_message_list,
        'filter':filters,
        'message':message,
        'success':success
    })

def crud_company_prices(request):
    obj = {}
    status = False
    result = {}
    message = "Request Recieved"
    filters = {}
    tranObjs = TickerHistoricDay.objects.none()
    operation = get_param(request, 'operation', None)
    error = False
    error_message_list = []
    num_pages = 1
    total_records = 0 
    
    check_operation = listvar_check(variable_name='operation',value=operation,allowedlist=operations_allowed_default)
    if not check_operation['error']:
        if operation == "read":
            pass
            out_read = read_company_prices(request) 
            message = out_read['message']               
            tranObjs = out_read['output']
            error_message_list.extend(out_read['error_message_list'])               
            error = out_read['error']     
            status = out_read['success']     
            num_pages     = out_read['num_pages']          
            filters       = out_read['filter']     
            total_records = out_read['total_records']          

        if operation in ["create","update"]:
            pass
            # out_create_update_exchange = create_update_exchange(request) 
            # message = out_create_update_exchange['message']               
            # tranObjs = out_create_update_exchange['output']
            # error_message_list.extend(out_create_update_exchange['error_message_list'])               
            # error = out_create_update_exchange['error']   
            # status = out_create_update_exchange['success']          

        if operation == "delete":
            pass
            # out_delete_exchange = delete_exchange(request) 
            # message = out_delete_exchange['message']               
            # tranObjs = out_delete_exchange['output']               
            # error_message_list.extend(out_delete_exchange['error_message_list'])               
            # error = out_delete_exchange['error']     
            # status = out_delete_exchange['success']           

        if not error:
            company = tranObjs[0].company
            
            result['company'] = {
                    'id':company.id
                    ,'name':company.name
                    ,'isin_no':company.isin_no
                    ,'is_listed_nse':company.is_listed_nse
                    ,'nse_ticker':company.nse_ticker
                    ,'industry_sector':company.industry_sector
                    ,'nse_tracker':company.nse_tracker
                    ,'nse_price_update_db_date':str(company.nse_price_update_db_date)[:19]
                    ,'nse_return_update_date':str(company.nse_return_update_date)[:19]
                    ,'created_at':str(company.created_at)[:19]
                    ,'modified_at':str(company.modified_at)[:19]
                    ,'nse_return_date':str(company.nse_return_date)[:19]
                    ,'nse_return_1d':company.nse_return_1d
                    ,'nse_return_1m':company.nse_return_1m
                    ,'nse_return_1y':company.nse_return_1y
                    ,'nse_annualized_return':company.nse_annualized_return
                    ,'nse_annualized_vol':company.nse_annualized_vol
                    ,'nse_trade_date':str(company.nse_trade_date)[:19]
                    ,'nse_price_high':company.nse_price_high
                    ,'nse_price_low':company.nse_price_low
                    ,'nse_price_close':company.nse_price_close
                    ,'nse_price_open':company.nse_price_open
                    ,'nse_price_close_adjusted':company.nse_price_close_adjusted
                    ,'nse_volume':company.nse_volume
                    }
            result['prices']={}
            result['prices'] = []
            # outdata = serializers.serialize('python', tranObjs)
            # outdata_sorted = json.dumps([d['fields'] for d in outdata])
            # result['prices']['nse'] = json.loads(outdata_sorted)
            tranObjs = tranObjs.order_by('date')
            date_list = list(map(lambda x : str(x.date)[:19],tranObjs))
            date_list = list(dict.fromkeys(date_list))
            total_dates = len(date_list)
            df_final  = pd.DataFrame({'Date':date_list}, columns = ['Date'])
            sub_nse_data = tranObjs.filter(exchange__exchange_code = "NSE")
            dates_nse = list(map(lambda x : str(x.date)[:19],sub_nse_data))
            prices_nse = list(map(lambda x : round(x.price_close,2),sub_nse_data))
            db_nse = pd.DataFrame({'Date':dates_nse,'Price NSE':prices_nse}, columns = ['Date','Price NSE'])
            df_final = pd.merge(df_final,
                                        db_nse[['Date', 'Price NSE']],
                                        on='Date', 
                                        how='left')

            for i in range(total_dates):       
                # if trans.exchange.exchange_code == "NSE":     
                result['prices'].append({
                    'date':df_final['Date'][i],
                    'Price NSE':df_final['Price NSE'][i]
                })

    
    else:
        error = check_operation['error']
        message = "Operation Not Specified"
        error_message_list.append(check_operation['errormessage'])

    obj['result'] = result
    # obj['filter'] = filters
    # obj['num_pages'] = num_pages
    # obj['total_records'] = total_records
    obj['message'] = message
    obj['status'] = status
    obj['error'] = error
    obj['error_list'] = error_message_list
    return HttpResponse(json.dumps(obj), content_type='application/json')

def read_index(request):
    error = False
    success = False
    error_message_list = []
    message = "Request Recieved!"
    filters = {}
    num_pages = 1
    total_records = 0 
    tranObjs = Company.objects.none()
    page_num = get_param(request, 'page_num', "1")
    page_size = get_param(request, 'page_size', "10")
    search = get_param(request,'search',None) 
    sort_by = get_param(request,'sort_by',None) 
    order = get_param(request,'order_by',None)    
    data_id = get_param(request,'data_id',None)
    
    if data_id != None and data_id != "":
        tranObjs = Index.objects.filter(id=data_id)
    else:
        tranObjs = Index.objects.all()

        # Filters/Sorting Start
        if search !=None and search !="":
            tranObjs = tranObjs.filter(Q(name__icontains=search) | Q(ticker__icontains=search))

        if sort_by !=None and sort_by !="" and sort_by != "none":
            if order == "asc":
                tranObjs = tranObjs.order_by(sort_by)
            else:
                tranObjs = tranObjs.order_by("-" + sort_by)
        # Filters/Sorting End
    # pagination variable

    total_records = tranObjs.count()    
    if page_num != None and page_num != "":
        page_num = int(page_num)
        tranObjs = Paginator(tranObjs, int(page_size))
        try:
            tranObjs = tranObjs.page(page_num)
        except:
            tranObjs = tranObjs
        num_pages = int(math.ceil(total_records / float(int(page_size))))
    # data = list(tranObjs)
    message  = "Success!"
    success = True
    
    filters['sort_by'] = [
                        {'value':'name','label':'Name'},
                        {'value':'ticker','label':'Ticker'},
                        {'value':'return_1d','label':'1 Day Return'},
                        {'value':'return_1m','label':'1 Month Return'},
                        {'value':'return_1y','label':'1 Year Return'},
                        {'value':'annualized_return','label':'Average Return'},
                        {'value':'annualized_vol','label':'Volatility Return'},
                        {'value':'volume','label':'Volume Traded'}
                       ]
                

    filters['order_by'] = [{'value':'asc','label':'Ascending'},
                           {'value':'desc','label':'Descending'}]

    return({
        'output':tranObjs,
        'num_pages':num_pages,
        'total_records':total_records,
        'error':error,
        'error_message_list':error_message_list,
        'filter':filters,
        'message':message,
        'success':success
    })

def crud_index(request):
    obj = {}
    status = False
    result = []
    message = "Request Recieved"
    filters = {}
    tranObjs = Exchange.objects.none()
    operation = get_param(request, 'operation', None)
    error = False
    error_message_list = []
    num_pages = 1
    total_records = 0 
    
    check_operation = listvar_check(variable_name='operation',value=operation,allowedlist=operations_allowed_default)
    if not check_operation['error']:
        if operation == "read":
            # pass
            out_read = read_index(request) 
            message = out_read['message']               
            tranObjs = out_read['output']
            error_message_list.extend(out_read['error_message_list'])               
            error = out_read['error']     
            status = out_read['success']     
            num_pages     = out_read['num_pages']          
            filters       = out_read['filter']     
            total_records = out_read['total_records']        

        if operation in ["create","update"]:
            pass
            # out_create_update_exchange = create_update_exchange(request) 
            # message = out_create_update_exchange['message']               
            # tranObjs = out_create_update_exchange['output']
            # error_message_list.extend(out_create_update_exchange['error_message_list'])               
            # error = out_create_update_exchange['error']   
            # status = out_create_update_exchange['success']          

        if operation == "delete":
            pass
            # out_delete_exchange = delete_exchange(request) 
            # message = out_delete_exchange['message']               
            # tranObjs = out_delete_exchange['output']               
            # error_message_list.extend(out_delete_exchange['error_message_list'])               
            # error = out_delete_exchange['error']     
            # status = out_delete_exchange['success']           

        if not error:
            for trans in tranObjs:
                TickerData = IndexHistoricDay.objects.filter(index=trans)
                first_ticker_date = TickerData.aggregate(Min('date'))
                last_ticker_date = TickerData.aggregate(Max('date'))
                result.append({
                    'id':trans.id
                    ,'name':trans.name
                    ,'ticker':trans.ticker
                    ,'exchange':trans.exchange.exchange_code
                    ,'price_update_date':str(trans.price_update_date)[:19]
                    ,'return_update_date':str(trans.return_update_date)[:19]
                    ,'created_at':str(trans.created_at)[:19]
                    ,'modified_at':str(trans.modified_at)[:19]
                    ,'min_ticker_date':str(first_ticker_date['date__min'])
                    ,'last_ticker_date':str(last_ticker_date['date__max'])
                    ,'total_prices':TickerData.count()
                    ,'return_date':str(trans.return_date)[:19]
                    ,'return_1d':trans.return_1d
                    ,'return_1m':trans.return_1m
                    ,'return_1y':trans.return_1y
                    ,'annualized_return':trans.annualized_return
                    ,'annualized_vol':trans.annualized_vol
                    ,'trade_date':str(trans.trade_date)[:19]
                    ,'price_high':trans.price_high
                    ,'price_low':trans.price_low
                    ,'price_close':trans.price_close
                    ,'price_open':trans.price_open
                    ,'price_close_adjusted':trans.price_close_adjusted
                    ,'volume':trans.volume
                })
    
    else:
        error = check_operation['error']
        message = "Operation Not Specified"
        error_message_list.append(check_operation['errormessage'])

    obj['result'] = result
    obj['filter'] = filters
    obj['num_pages'] = num_pages
    obj['total_records'] = total_records
    obj['message'] = message
    obj['status'] = status
    obj['error'] = error
    obj['error_list'] = error_message_list
    return HttpResponse(json.dumps(obj), content_type='application/json')

def read_index_prices(request):
    error = False
    success = False
    error_message_list = []
    message = "Request Recieved!"
    filters = {}
    num_pages = 1
    total_records = 0 
    tranObjs = IndexHistoricDay.objects.none()
    data_id = get_param(request,'data_id',None)
    ticker = get_param(request,'ticker',None)
    # isin = get_param(request,'isin',None)
    no_parameter = 0
    if data_id != None and data_id != "":
        tranObjs = IndexHistoricDay.objects.filter(index__id=data_id)
    elif ticker != None and ticker != "":
        tranObjs = IndexHistoricDay.objects.filter(index__ticker=ticker)
    else:
        no_parameter = 1
        tranObjs = IndexHistoricDay.objects.none()

    total_records = tranObjs.count()    

    if no_parameter == 1:
        message = "No parameter shared"
    else:
        message  = "Success!"
    success = True
    
    filters['sort_by'] = [
                        {'value':'date','label':'Date'},
                       ]
                

    filters['order_by'] = [{'value':'asc','label':'Ascending'},
                           {'value':'desc','label':'Descending'}]

    return({
        'output':tranObjs,
        'num_pages':num_pages,
        'total_records':total_records,
        'error':error,
        'error_message_list':error_message_list,
        'filter':filters,
        'message':message,
        'success':success
    })

def crud_index_prices(request):
    obj = {}
    status = False
    result = {}
    message = "Request Recieved"
    filters = {}
    tranObjs = Exchange.objects.none()
    operation = get_param(request, 'operation', None)
    error = False
    error_message_list = []
    num_pages = 1
    total_records = 0 
    
    check_operation = listvar_check(variable_name='operation',value=operation,allowedlist=operations_allowed_default)
    if not check_operation['error']:
        if operation == "read":
            pass
            out_read = read_index_prices(request) 
            message = out_read['message']               
            tranObjs = out_read['output']
            error_message_list.extend(out_read['error_message_list'])               
            error = out_read['error']     
            status = out_read['success']     
            num_pages     = out_read['num_pages']          
            filters       = out_read['filter']     
            total_records = out_read['total_records']          

        if operation in ["create","update"]:
            pass
            # out_create_update_exchange = create_update_exchange(request) 
            # message = out_create_update_exchange['message']               
            # tranObjs = out_create_update_exchange['output']
            # error_message_list.extend(out_create_update_exchange['error_message_list'])               
            # error = out_create_update_exchange['error']   
            # status = out_create_update_exchange['success']          

        if operation == "delete":
            pass
            # out_delete_exchange = delete_exchange(request) 
            # message = out_delete_exchange['message']               
            # tranObjs = out_delete_exchange['output']               
            # error_message_list.extend(out_delete_exchange['error_message_list'])               
            # error = out_delete_exchange['error']     
            # status = out_delete_exchange['success']           

        if not error:
            index = tranObjs[0].index
            
            result['index'] = {
                    'id':index.id
                    ,'name': index.name
                    ,'ticker': index.ticker
                    ,'exchange':index.exchange.exchange_code
                    ,'created_at':str(index.created_at)[:19]
                    ,'modified_at':str(index.modified_at)[:19]
                    ,'return_date':str(index.return_date)[:19]
                    ,'return_1d':index.return_1d
                    ,'return_1m':index.return_1m
                    ,'return_1y':index.return_1y
                    ,'annualized_return':index.annualized_return
                    ,'annualized_vol':index.annualized_vol
                    ,'trade_date':str(index.trade_date)[:19]
                    ,'price_high':index.price_high
                    ,'price_low':index.price_low
                    ,'price_close':index.price_close
                    ,'price_open':index.price_open
                    ,'price_close_adjusted':index.price_close_adjusted
                    ,'volume':index.volume
                    ,'price_update_date':str(index.price_update_date)[:19]
                    ,'return_update_date':str(index.return_update_date)[:19]
                    }
            result['prices']={}
            result['prices'] = []
            tranObjs = tranObjs.order_by('date')
            for trans in tranObjs:       
                result['prices'].append({
                    'date':str(trans.date)[:19]
                    ,'Price':round(trans.price_close,2)
                })

    
    else:
        error = check_operation['error']
        message = "Operation Not Specified"
        error_message_list.append(check_operation['errormessage'])

    obj['result'] = result
    obj['message'] = message
    obj['status'] = status
    obj['error'] = error
    obj['error_list'] = error_message_list
    return HttpResponse(json.dumps(obj), content_type='application/json')

def read_strategies(request):
    obj = {}
    result = []
    error = False
    success = False
    error_message_list = []
    message = "Request Recieved!"
    filters = {}
    num_pages = 1
    total_records = 0 
    tranObjs = StrategyDetails.objects.none()
    page_num = get_param(request, 'page_num', "1")
    page_size = get_param(request, 'page_size', "10")
    search = get_param(request,'search',None) 
    sort_by = get_param(request,'sort_by',None) 
    order = get_param(request,'order_by',None)    
    data_id = get_param(request,'data_id',None)

    if data_id != None and data_id != "":
        tranObjs = StrategyDetails.objects.filter(id=data_id)
    else:
        tranObjs = StrategyDetails.objects.all()

        # Filters/Sorting Start
        if search !=None and search !="":
            tranObjs = tranObjs.filter(Q(name__icontains=search) | Q(description__icontains=search))

        if sort_by !=None and sort_by !="" and sort_by != "none":
            if order == "asc":
                tranObjs = tranObjs.order_by(sort_by)
            else:
                tranObjs = tranObjs.order_by("-" + sort_by)
        # Filters/Sorting End
    
    # pagination variable

    total_records = tranObjs.count()    
    if page_num != None and page_num != "":
        page_num = int(page_num)
        tranObjs = Paginator(tranObjs, int(page_size))
        try:
            tranObjs = tranObjs.page(page_num)
        except:
            tranObjs = tranObjs
        num_pages = int(math.ceil(total_records / float(int(page_size))))
    # data = list(tranObjs)
    message  = "Success!"
    success = True
    
    filters['sort_by'] = [
                        {'value':'name','label':'Name'},
                        {'value':'alpha','label':'Alpha'},
                        {'value':'beta','label':'Beta'},
                        {'value':'sharpe_ratio','label':'Sharpe Ratio'},
                        {'value':'average_return','label':'Average Return'},
                        {'value':'max_drawdown','label':'Max Drawdown'},
                        {'value':'volatility','label':'Volatility'},
                        ]   

    filters['order_by'] = [{'value':'asc','label':'Ascending'},
                           {'value':'desc','label':'Descending'}]

    
    if not error:
        for trans in tranObjs:
            result.append({
                'id':trans.id
                ,'name': trans.name                
                ,'description': trans.description         
                ,'alpha': trans.alpha               
                ,'alpha_significance': trans.alpha_significance  
                ,'beta': trans.beta                
                ,'beta_significance': trans.beta_significance   
                ,'sharpe_ratio': trans.sharpe_ratio        
                ,'average_return': trans.average_return      
                ,'max_drawdown': trans.max_drawdown        
                ,'volatility': trans.volatility          
                ,'historic_start_date': str(trans.historic_start_date)[:19]
                ,'historic_end_date': str(trans.historic_end_date)[:19]
            })    

    obj['result'] = result
    obj['filter'] = filters
    obj['num_pages'] = num_pages
    obj['total_records'] = total_records
    obj['message'] = message
    obj['status'] = success
    obj['error'] = error
    obj['error_list'] = error_message_list
    return HttpResponse(json.dumps(obj), content_type='application/json')


def read_strategy_returns_multi(request):
    obj = {}
    result = {}
    error = False
    success = False
    error_message_list = []
    message = "Request Recieved!"
    filters = {}
    num_pages = 1
    total_records = 0 
    tranObjs = StrategyReturns.objects.none()
    strategy_name = get_param(request,'strategy_name',None)
    result['strategy'] = []
    # result['returns'] = []

    if strategy_name != None and strategy_name != "":
        list_strategy = strategy_name.split(",")
        strategies = StrategyDetails.objects.filter(name__in = list_strategy)
        if strategies.count() >0:
            for strategy in strategies:    
                result['strategy'].append(
                        {
                        'id':strategy.id
                        ,'name': strategy.name                
                        ,'description': strategy.description         
                        ,'alpha': strategy.alpha               
                        ,'alpha_significance': strategy.alpha_significance  
                        ,'beta': strategy.beta                
                        ,'beta_significance': strategy.beta_significance   
                        ,'sharpe_ratio': strategy.sharpe_ratio        
                        ,'average_return': strategy.average_return      
                        ,'max_drawdown': strategy.max_drawdown        
                        ,'volatility': strategy.volatility          
                        ,'historic_start_date': str(strategy.historic_start_date)[:19]
                        ,'historic_end_date': str(strategy.historic_end_date)[:19]
                        }
                    )
                # result['prices'] =

            # transObjs = StrategyReturns.objects.filter(strategy__in = list(strategies)).order_by('date')
            # date_list = list(map(lambda x : str(x.date)[:19],tranObjs))
            # date_list = list(dict.fromkeys(date_list))
            # total_dates = len(date_list)
            # df_final  = pd.DataFrame({'Date':[]}, columns = ['Date'])
            # print(df_final)
            # for strategy in strategies:
            #     sub_strat_data = StrategyReturns.objects.filter(strategy = strategy).order_by('date')
            #     dates_sub_strat = list(map(lambda x : str(x.date)[:19],sub_strat_data))
            #     return_strategy = list(map(lambda x : round(x.return_strategy,3),sub_strat_data))  
            #     high_water_mark  = list(map(lambda x : round(x.high_water_mark,3),sub_strat_data))   
            #     drawdown      = list(map(lambda x : round(x.drawdown,3),sub_strat_data))      
            #     cumulative_return   = list(map(lambda x : round(x.cumulative_return,3),sub_strat_data))
            #     strategy_name = strategy.name
            #     column_name_return = 'Return - ' + strategy_name
            #     column_name_hwm = 'HWM - ' + strategy_name
            #     column_name_drawdown = 'Drawdown - ' + strategy_name
            #     column_name_cumreturn = 'Cumulative Ret. - ' + strategy_name                
            #     column_list = ['Date',column_name_return,column_name_hwm,column_name_drawdown,column_name_cumreturn]
            #     print(column_list)
            #     data_dict =    {'Date':dates_sub_strat,
            #                                 column_name_return:return_strategy,
            #                                 column_name_hwm:high_water_mark,
            #                                 column_name_drawdown:drawdown,
            #                                 column_name_cumreturn:cumulative_return
            #                     }
            #     # print(data_dict)
            #     db_substrat = pd.DataFrame(data_dict, columns = column_list)
            #     print(db_substrat)
            #     df_final = pd.merge(df_final,
            #                         db_substrat[['Date',column_name_return,column_name_hwm,column_name_drawdown,column_name_cumreturn]],
            #                         on='Date', 
            #                         how='outer')
            #     print(df_final)
            # column_list = list(df_final.columns)
            # print(column_list)
            # total_dates = len(df_final)
            # for i in range(total_dates):       
            #     prices_dict = {}
            #     print('1')
            #     for col in column_list:
            #         print('2')
            #         print(col)
            #         prices_dict[col] = df_final[col][i]
            #         print('3')
            #     result['returns'].append(prices_dict)            
            
            message  = "Success!"
            success = True
        else:
            error = True
            message  = "Strategy Name Not Correct!"
    else:
        error = True
        message  = "Strategy Name Not Shared!"

    obj['result'] = result
    obj['filter'] = filters
    obj['message'] = message
    obj['status'] = success
    obj['error'] = error
    obj['error_list'] = error_message_list
    return HttpResponse(json.dumps(obj), content_type='application/json')

def read_strategy_returns(request):
    obj = {}
    result = {}
    error = False
    success = False
    error_message_list = []
    message = "Request Recieved!"
    filters = {}
    num_pages = 1
    total_records = 0 
    tranObjs = StrategyReturns.objects.none()
    strategy_id = get_param(request,'strategy_id',None)
    result['strategy'] = {}
    result['returns'] = {}

    all_strategies_list = list(map(lambda x : { 'value':x.name,'label': x.name.upper() } ,StrategyDetails.objects.all()))
    filters['strategies'] = all_strategies_list

    if strategy_id != None and strategy_id != "":
        # list_strategy = strategy_name.split(",")
        strategies = StrategyDetails.objects.filter(id = strategy_id)
        if strategies.count() >0:
            strategy = strategies[0]
            strat_dict = {'id':strategy.id
                    ,'name': strategy.name                
                    ,'description': strategy.description         
                    ,'alpha': strategy.alpha               
                    ,'alpha_significance': strategy.alpha_significance  
                    ,'beta': strategy.beta                
                    ,'beta_significance': strategy.beta_significance   
                    ,'sharpe_ratio': strategy.sharpe_ratio        
                    ,'average_return': strategy.average_return      
                    ,'max_drawdown': strategy.max_drawdown        
                    ,'volatility': strategy.volatility          
                    ,'historic_start_date': str(strategy.historic_start_date)[:19]
                    ,'historic_end_date': str(strategy.historic_end_date)[:19]
                    }
            result['strategy'] = strat_dict
                
            sub_strat_data = StrategyReturns.objects.filter(strategy = strategy).order_by('date')
            dates_sub_strat = list(map(lambda x : str(x.date)[:19],sub_strat_data))
            return_strategy = list(map(lambda x : round(x.return_strategy,3),sub_strat_data))  
            high_water_mark  = list(map(lambda x : round(x.high_water_mark,3),sub_strat_data))   
            drawdown      = list(map(lambda x : round(x.drawdown,3),sub_strat_data))      
            cumulative_return   = list(map(lambda x : round(x.cumulative_return,3),sub_strat_data))
            strategy_name = strategy.name
            # column_list = ['Date','Return','HWM','Drawdown','Cum Return']
            
            data_dict =    {
                            'Date':dates_sub_strat,
                            'Return':return_strategy,
                            'HWM':high_water_mark,
                            'Drawdown':drawdown,
                            'Cum Return':cumulative_return
                            }
            result['returns'] = data_dict
            # df_final = pd.DataFrame(data_dict, columns = column_list)
            # total_dates = len(df_final)
            # for i in range(total_dates):       
            #     prices_dict = {}
            #     for col in column_list:
            #         prices_dict[col] = df_final[col][i]
            #     result['returns'].append(prices_dict)        
            message  = "Success!"
            success = True
        else:
            error = True
            message  = "Strategy Name Not Correct!"
    else:
        error = True
        message  = "Strategy Name Not Shared!"

    obj['result'] = result
    obj['filter'] = filters
    obj['message'] = message
    obj['status'] = success
    obj['error'] = error
    obj['error_list'] = error_message_list
    return HttpResponse(json.dumps(obj), content_type='application/json')







