from konlpy.tag import Okt
from konlpy.utils import pprint
import pandas as pd
import matplotlib

df = pd.read_csv("NLP_log.csv", index_col = 0, encoding="utf-8")
df.index = pd.DatetimeIndex(df.index)
def analyze_data(df, *date):
    if date[-1].endswith("월"):
        #! input : 1월
        df = df.loc[df.index.dt.month == int(data[-1].replace("월",""))]
        df.index = df.index.weekday
    elif data[-1].endswith("주"):
        #! input : 1월 1주
        mask = df.index.dt.month == int(data[0].replace("월","")) and \
                df.index.dt.weekdays() == int(data[-1].replace("주",""))
        df = df.loc[mask]
        df.index = df.index.day
    elif data[-1].endswith("일"):
        #! input : 1월 1일
        mask = df.index.dt.month == int(data[0].replace("월","")) and \
                df.index.dt.day == int(data[-1].replace("일",""))
        df = df.loc[mask]
        df.index = df.index.hour
    total_chat_freq = len(df)
    talker_rate = df["speaker"].value_counts() / len(df)
    
    # df.index = df.index.dt.floor(freq)
    # pass
    # freq_df = 
    