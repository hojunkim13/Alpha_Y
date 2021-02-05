def prop_checker(word):    
    last = word[-1] 
    criteria = (ord(last) - 44032) % 28     
    if criteria == 0:  
        return False
    else:                
        return True

def load_db():
    try:
        db = pd.read_csv('db.csv', index_col = 0, header = 0)
    except:
        db = pd.DataFrame()
    sdb = pd.read_csv('item/items.csv', index_col = 0, header= 0)
    return db, sdb

def log_db(db):
    db.to_csv('db.csv')
    threading.Timer(5, function=log_db, args=(db,)).start()

def get_points(speaker, prob):
    rand_points = np.random.choice(range(1,11), p = prob)
    try:
        if rand_points == 10:
            db.loc[speaker,'wallet'] = db.loc[speaker,'wallet'] + 100
            return True
        else:
            db.loc[speaker,'wallet'] = db.loc[speaker,'wallet'] + rand_points * 0.1
    except KeyError:
        db.loc[speaker,'wallet'] = 0