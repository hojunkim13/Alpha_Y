def prop_checker(word):    
    last = word[-1] 
    criteria = (ord(last) - 44032) % 28     
    if criteria == 0:  
        return False
    else:                
        return True

