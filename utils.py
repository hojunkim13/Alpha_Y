import pandas as pd


def propChecker(word):    
    last = word[-1] 
    criteria = (ord(last) - 44032) % 28     
    if criteria == 0:  
        return False
    else:                
        return True

def dataCollector(msg, db, nlp_log):
    speaker = db.loc[msg.author.id, "name"]
    content = msg.content
    length = len(content)
    log_time = pd.Timestamp.now().floor('s')
    df = pd.DataFrame({"speaker":[speaker],  "length": [length], "content": [content]}, index = [log_time])
    nlp_log = nlp_log.append(df)
    return nlp_log

def load_db():
    try:
        db = pd.read_pickle("DB/DB.pkl")
    except FileNotFoundError:
        db = pd.DateFrame()
    
    try:
        sdb = pd.read_pickle("./DB/item/items.pkl")
    except FileNotFoundError:
        db = pd.DataFrame()

    try:
        nlp_log = pd.read_pickle('nlp_log.pkl')
    except:
        nlp_log = pd.DataFrame()
    return db, sdb, nlp_log




