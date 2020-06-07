from pricingdata.views import *
from pricingdata.models import *
from dataclean.models import *

# TickerHistoricDay.objects.all().delete()
# Company.objects.all().delete()
# Exchange.objects.all().delete()
DailyReturn.objects.all().delete()
MonthlyReturn.objects.all().delete()

# <<<< ------ Creating NSE Exchange ------>>>>

# ExchangeClass.create_exchange(            
#             exchange_name = 'National Stock Exchange of India'
#             ,exchange_code = 'NSE'
#             ,exchange_country = 'India'
#             ,exchange_timezone = 'Asia/Kolkata'
#             ,exchange_timezone_short = 'IST'
#             ,timezone_gmt_off_milliseconds = 19800000
# )

# <<<< ------ Download all NSE tickers ------>>>>
# NseIndia.update_all_equity()


# <<<< ------ Download all historic data ------>>>>
# NseIndia.update_all_historic_ticker()










