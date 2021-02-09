import pandas as pd
import threading
import time

def prop_checker(word):    
    last = word[-1] 
    criteria = (ord(last) - 44032) % 28     
    if criteria == 0:  
        return False
    else:                
        return True

def data_collector(msg,db,nlp_log):
    speaker = db.loc[msg.author.id, "name"]
    content = msg.content
    length = len(content)
    log_time = pd.Timestamp.now().floor('s')
    df = pd.DataFrame({"speaker":[speaker],  "length": [length], "content": [content]}, index = [log_time])
    nlp_log = nlp_log.append(df)
    return nlp_log

def load_db():
    db = pd.read_csv('db.csv', index_col=0, header=0, encoding = 'utf-8')
    sdb = pd.read_csv('item/items.csv', index_col=0, header=0, encoding = 'utf-8')
    try:
        nlp_log = pd.read_csv('nlp_log.csv', index_col= 0, encoding='utf-8')
    except:
        nlp_log = pd.DataFrame()
    return db, sdb, nlp_log




