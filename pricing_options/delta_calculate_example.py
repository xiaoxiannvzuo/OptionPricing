from pricing_engines.blackcalculator import blackcalculator
from pricing_engines.svimodel import svimodel
from pricing_engines.OptionPlainVanilla import OptionPlainVanilla
from pricing_engines.Evaluation import Evaluation
from pricing_engines.OptionEngine import OptionEngine
from Utilities.utilities import *
import QuantLib as ql
import math
import datetime

hedge_date = datetime.date(2017,7,19)
evaluation = Evaluation(to_ql_date(hedge_date))
maturitydt = datetime.date(2017,9,27)
spot = 2.702
rf = 0.030
params = [-0.0689813692309 , 4.57986004886 , -0.980043687933 , -0.617957974368 , 0.117468005221]
vols = {2.2: 0.2449897447635236, 2.25: 0.22837076995826824, 2.3: 0.21949149068217633, 2.35: 0.20985304700906196, 2.4: 0.2041719266214876, 2.45: 0.20033927445461783, 2.5: 0.19807488063669001, 2.55: 0.19085764979481112, 2.6: 0.19159774017588876, 2.65: 0.1919016701828232, 2.7: 0.1934624432856883, 2.75: 0.19404949435809657}

ttm = (maturitydt-hedge_date).days/365
discount = math.exp(-rf*ttm)
dS = 0.001
iscall = False
engineType = 'AnalyticEuropeanEngine'

print('spot = ',spot)
print('='*100)
print("%10s %25s %25s %25s " % ("Strike","delta_total","delta_total_ql ","delta_constant_vol "))
print('-'*100)
underlying_ql = ql.SimpleQuote(spot)
daycounter = ql.ActualActual()
calendar = ql.China()
svi = svimodel(ttm,params)
for strike in vols.keys():
    option_call = OptionPlainVanilla(strike, to_ql_date(maturitydt), ql.Option.Call).get_european_option()
    vol = vols.get(strike)
    process = evaluation.get_bsmprocess_cnstvol(daycounter,calendar, underlying_ql, vol)
    engine = OptionEngine(process, engineType).engine
    option_call.setPricingEngine(engine)
    stdDev = vol * math.sqrt(ttm)
    forward = spot/discount
    black = blackcalculator(strike,forward,stdDev,discount,iscall)

    delta = black.delta(spot)
    # 隐含波动率对行权价的一阶倒数
    dSigma_dK = svi.calculate_dSigma_dK(strike,forward,ttm)
    # 全Delta
    delta_total = black.delta_total(spot,ttm,dSigma_dK)

    delta_total_ql = delta - option_call.vega() * (strike/spot)*dSigma_dK
    # Effective Delta
    delta_eff = svi.calculate_effective_delta(spot, dS,strike,discount,iscall)

    delta1 = round(delta, 6)
    delta_t1 = round(delta_total, 6)
    delta_eff1 = round(delta_eff, 6)
    print("%10s %25s %25s %25s " % (strike,delta_total, delta_total_ql,delta1))
print('='*100)
