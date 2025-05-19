from sklearn import linear_model
import pandas as pd
import mojito
import os
from dotenv import load_dotenv

load_dotenv()

class StockPredictor:
    def __init__(self):
        self.reg = linear_model.Lasso(alpha=0.1)

    @staticmethod
    def _reverse_int_list(data, key):
        return [int(i) for i in data[key]][::-1]

    def _prepare_features(self, data):
        # data는 dict 형식이라고 가정
        oprc = self._reverse_int_list(data, 'stck_oprc')
        clpr = self._reverse_int_list(data, 'stck_clpr')
        hgpr = self._reverse_int_list(data, 'stck_hgpr')
        lwpr = self._reverse_int_list(data, 'stck_lwpr')
        vol = self._reverse_int_list(data, 'acml_vol')
        pbmn = self._reverse_int_list(data, 'acml_tr_pbmn')
        sign = self._reverse_int_list(data, 'prdy_vrss_sign')
        vrss = self._reverse_int_list(data, 'prdy_vrss')

        print(f"🔍 oprc 길이: {len(oprc)}")

        min_len = min(len(oprc), len(clpr), len(hgpr), len(lwpr),
                      len(vol), len(pbmn), len(sign), len(vrss))
        if min_len < 100:
            raise ValueError("예측이 제공되지 않는 종목입니다.")

        X = []
        for i in range(1, 100):  # 99개 데이터
            X.append([
                i,
                oprc[i],
                clpr[i],
                hgpr[i],
                lwpr[i],
                vol[i],
                pbmn[i],
                sign[i],
                vrss[i]
            ])
        
        latest_input = [[
            99,
            oprc[99],
            clpr[99],
            hgpr[99],
            lwpr[99],
            vol[99],
            pbmn[99],
            sign[99],
            vrss[99]
        ]]
        
        return X, hgpr, lwpr, latest_input

    def predict_high(self, data):
        X, hgpr, _, latest_input = self._prepare_features(data)
        y = hgpr[1:100]
        self.reg.fit(X, y)
        return int(self.reg.predict(latest_input)[0])

    def predict_low(self, data):
        X, _, lwpr, latest_input = self._prepare_features(data)
        y = lwpr[1:100]
        self.reg.fit(X, y)
        return int(self.reg.predict(latest_input)[0])


class StockDataHandler:
    def __init__(self):
        my_key = os.getenv("MY_APP_KEY_2")
        my_secret = os.getenv("MY_APP_SECRET_KEY_2")
        my_acc_no = os.getenv("MY_ACC_NO_2")
        self.broker = mojito.KoreaInvestment(
            api_key=my_key,
            api_secret=my_secret,
            acc_no=my_acc_no
        )
        self.kospi_symbols = self.broker.fetch_kospi_symbols()
        self.kosdaq_symbols = self.broker.fetch_kosdaq_symbols()
        self.data = None

    def code_by_name(self, name):
        kospi = dict(self.kospi_symbols)
        kosdaq = dict(self.kosdaq_symbols)

        for i, stock_name in enumerate(kospi.get('한글명', [])):
            if stock_name == name:
                return kospi['단축코드'][i]
        for i, stock_name in enumerate(kosdaq.get('한글명', [])):
            if stock_name == name:
                return kosdaq['단축코드'][i]
        return None

    def resp_Time(self, timeframe, code):
        raw_data = self.broker.fetch_ohlcv(
            symbol=code,
            timeframe=timeframe,
            adj_price=True
        )
        self.data = raw_data

    def return_data(self):
        if isinstance(self.data, dict) and 'output2' in self.data:
            df = pd.DataFrame(self.data['output2'])
            return df.to_dict(orient='list')
        return self.data