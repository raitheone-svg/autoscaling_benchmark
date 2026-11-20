Provenance: REAL:Alibaba-microservices-v2022-MSMetrics

Table I — forecast accuracy (test split)
method | MAE | RMSE | sMAPE%
Reactive (HPA) | 5.3748 | 10.6095 | 3.7
Moving average | 6.9551 | 10.209 | 4.8
Holt (ES) | 6.5682 | 12.9433 | 4.4
GBDT | 5.7418 | 9.2167 | 4.6
LSTM | 5.1112 | 9.593 | 3.7

Table II — cost to hold SLO violations <= 5%
method | cost | headroom | SLO achieved
Reactive (HPA) | 186.7444 | 0.1 | 0.0282 | +0% vs reactive
Moving average | 181.4124 | 0.05 | 0.0282 | +3% vs reactive
Holt (ES) | 192.7735 | 0.15 | 0.0345 | -3% vs reactive
GBDT | 183.5879 | 0.1 | 0.0491 | +2% vs reactive
LSTM | 183.9046 | 0.1 | 0.0191 | +2% vs reactive
