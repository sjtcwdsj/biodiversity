import numpy as np
import pandas as pd
import os
categorys=['CR','EN','NT','VU']

res=None

for category in categorys:
    data=pd.read_csv(os.path.join('/root/work/BIO/fix/res/loss/potancsv',f'y_{category}.csv'))
    
    if res is None:
        res=data
    else:
        res['thekey']=res['thekey']+data['thekey']

res['thekey']=res['thekey']/4
res.to_csv('/root/work/BIO/fix/res/loss/potancsv/thres.csv',index=0)


