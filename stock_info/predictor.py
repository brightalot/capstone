from sklearn import linear_model
import pandas as pd
import mojito
import os
from dotenv import load_dotenv

load_dotenv()

class model_class:
    def __init__(self):
        self.reg = linear_model.Lasso(alpha=0.1)

    @staticmethod
    def _reverse_int_list(data, key):
        return [int(i) for i in data[key]][::-1]

    def _prepare_features(self, data):
        # data는 dict 형식이라고 가정
        oprc_data = self._reverse_int_list(data, 'stck_oprc')
        clpr_data = self._reverse_int_list(data, 'stck_clpr')
        hgpr_data = self._reverse_int_list(data, 'stck_hgpr')
        lwpr_data = self._reverse_int_list(data, 'stck_lwpr')
        vol_data = self._reverse_int_list(data, 'acml_vol')
        pbmn_data = self._reverse_int_list(data, 'acml_tr_pbmn')
        sign_data = self._reverse_int_list(data, 'prdy_vrss_sign')
        vrss_data = self._reverse_int_list(data, 'prdy_vrss')
        
            # 🔍 여기에 디버깅 출력
        print(f"🔍 oprc_data 길이: {len(oprc_data)}")

        # 데이터 길이 체크
        min_len = min(len(oprc_data), len(clpr_data), len(hgpr_data), len(lwpr_data),
                      len(vol_data), len(pbmn_data), len(sign_data), len(vrss_data))
        if min_len < 100:
            raise ValueError(f"예측이 제공되지 않는 종목입니다.")
        X = []
        for i in range(1, 100):  # 99개 데이터
            X.append([
                i,
                oprc_data[i],
                clpr_data[i],
                hgpr_data[i],
                lwpr_data[i],
                vol_data[i],
                pbmn_data[i],
                sign_data[i],
                vrss_data[i]
            ])
        return X, oprc_data, clpr_data, hgpr_data, lwpr_data, vol_data, pbmn_data, sign_data, vrss_data

    def predict_hgpr(self, data):
        X, oprc_data, clpr_data, hgpr_data, lwpr_data, vol_data, pbmn_data, sign_data, vrss_data = self._prepare_features(data)
        y = hgpr_data[1:100]
        self.reg.fit(X, y)

        next_input = [[
            99,
            oprc_data[99],
            clpr_data[99],
            hgpr_data[99],
            lwpr_data[99],
            vol_data[99],
            pbmn_data[99],
            sign_data[99],
            vrss_data[99]
        ]]
        return int(self.reg.predict(next_input)[0])

    def predict_lwpr(self, data):
        X, oprc_data, clpr_data, hgpr_data, lwpr_data, vol_data, pbmn_data, sign_data, vrss_data = self._prepare_features(data)
        y = lwpr_data[1:100]
        self.reg.fit(X, y)

        next_input = [[
            99,
            oprc_data[99],
            clpr_data[99],
            hgpr_data[99],
            lwpr_data[99],
            vol_data[99],
            pbmn_data[99],
            sign_data[99],
            vrss_data[99]
        ]]
        return int(self.reg.predict(next_input)[0])


class stock_class:
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
        self.data = raw_data  # 전체 구조 유지

    def return_data(self):
        # 'output2'를 추출해서 dict(orient='list') 형식으로 반환
        if isinstance(self.data, dict) and 'output2' in self.data:
            df = pd.DataFrame(self.data['output2'])
            return df.to_dict(orient='list')
        return self.data
