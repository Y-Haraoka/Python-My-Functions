#csvファイルを一つにまとめる関数
def CombineCSV(filepaths):
    import os
    import pandas as pd
    from glob import glob
        
    All_df = pd.DataFrame()
    
    filepaths = glob(filepaths+'/*.csv')

    for filepath in filepaths:
        df = pd.read_csv(filepath)
        sample_id = os.path.splitext(os.path.basename(filepath))[0] 
        df['sample'] = sample_id
        All_df = pd.concat([All_df, df])
    return All_df
