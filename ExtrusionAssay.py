#Extrusionの解析に使う関数たち


'''
関数（１）
目的
複数のcsvファイルを1つのcsvファイルにまとめる

引数
filepaths: csvファイルの入ったフォルダーへのfile pathを入力する。
r'C:\Users\hoge'
'''


def Combine_CSV(filepaths):
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



'''
関数(2)
目的
TypeとNoについての行を追加
・Type: 各群の総称　例えばControlやRasなど
・No: 各画像の番号
Typeは、画像ファイル名に使用した表記と一致させる
DayNOは数字を入力する

引数>
df          : Dataframe
DayNo       : Day number (e.g. 1, 2)
Type1, Type2: 各群の総称 (e.g. Control, Ras)
'''

def Column_Add_Df(df, DayNo, Type1, Type2, Type3='hoge', Type4='hogehoge', Type5='hogehogehoge'):
    import numpy as np
    
    condition = [
        (df['sample'].str.contains(Type1)),
        (df['sample'].str.contains(Type2)),
        (df['sample'].str.contains(Type3)),
        (df['sample'].str.contains(Type4)),
        (df['sample'].str.contains(Type5)),

    ]

    choices = [Type1, Type2, Type3, Type4, Type5]

    df['Type'] = np.select(condition, choices, default=0)


    condition2 = [
        (df['sample'].str.contains('_01|_1')),
        (df['sample'].str.contains('_02|_2')),
        (df['sample'].str.contains('_03|_3')),
        (df['sample'].str.contains('_04|_4')),
        (df['sample'].str.contains('_05|_5')),
        (df['sample'].str.contains('_06|_6')),
        (df['sample'].str.contains('_07|_7')),
        (df['sample'].str.contains('_08|_8')),
        (df['sample'].str.contains('_09|_9')),
        (df['sample'].str.contains('_10')),
        (df['sample'].str.contains('_11')),
        (df['sample'].str.contains('_12')),
        (df['sample'].str.contains('_13')),
        (df['sample'].str.contains('_14')),
        (df['sample'].str.contains('_15')),
        (df['sample'].str.contains('_16')),
        (df['sample'].str.contains('_17')),
        (df['sample'].str.contains('_18')),
        (df['sample'].str.contains('_19')),
        (df['sample'].str.contains('_20')),

    ]

    choices2 = ['01','02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12','13', '14', '15', '16', '17', '18', '19', '20']

    df['No'] = np.select(condition2, choices2, default=0)

    df['ID'] = df['Type'].str.cat(df['No'], sep = '_')
    df = df.rename(columns={'count': 'Day'+str(DayNo)+'_No'}) 
    df = df.drop('sample', axis=1)

    return df



'''
関数(3)
Day1とDay2について、閾値を決めて、それらの条件を満たす細胞数をカウントしたデータフレームを返す関数。

引数>
df        : Dataframe
Area_Max  : Area(細胞サイズ)の最大値。Yolkなどの偽陽性部分を解析から除くため。
Are_min   : Area(細胞サイズ)の最小値。Debrisなどの偽陽性部分を解析から除くため。
Circ_min  : Circurality(真円度)の最小値。筋肉細胞などの異所的な細胞を解析から除くため。
CellNo_min: 1個体当たりの最小の細胞数。個体当たりの細胞数が少ないものは解析に影響するので、ある程度の細胞数(10)が出ているもののみを解析に使用する
'''
def Sep_Select_Df(df, Area_Max = 400, Area_min = 60, Circ_min = 0.7, CellNo_min = 10):
    import pandas as pd
    
    df = df[['sample', 'Area', 'Circ.']] #必要なデータだけ抽出
    df = df[df['Area'] < Area_Max]
    df = df[df['Area'] > Area_min]
    df = df[df['Circ.'] > Circ_min]
    df = df.groupby(['sample']).count()['Area']
    df = pd.DataFrame({'sample': df.index, 'count': df.values})

    Day1_data = df[df['sample'].str.contains('Day1|day1|DAY1')]
    Day1_data = Day1_data[Day1_data['count'] >= CellNo_min]
    Day2_data = df[df['sample'].str.contains('Day2|day2|DAY2')]
    return Day1_data, Day2_data



'''
関数(4)
Day1とDay2のデータフレームを結合して、相対的な細胞数を算出する関数

引数>
df1: Day1 dataframe
df2: Day2 dataframe
ID : dataframeをまとめる際のIDとなるもの。IDは関数(2)Column_Add_Dfで定義したもの。
'''

def Combine_Day1Day2(df1, df2, ID='ID'):
    import pandas as pd

    #how=leftにするとDay2のときに細胞数が0で欠損してしまったIDについてもnanが入る！
    Day1Day2_data = pd.merge(df1, df2, on=ID, how = 'left')
    Day1Day2_data = Day1Day2_data.rename(columns = {"Type_x":"Type", "No_x":"No" })

    Day1Day2_data = Day1Day2_data.fillna(0) #そして生じたnanを0に変換

    Day1Day2_data = Day1Day2_data[['ID','Day1_No', 'Day2_No', 'No','Type']] #並べ替え
    Day1Day2_data = Day1Day2_data.eval('Relative_No = Day2_No/Day1_No*100') #相対的な細胞数の列を追加
     
    return Day1Day2_data


#関数(5)
#dataframeをトリミングする関数。
#DefaultだとMax-minのそれぞれ10%をトリミングする。
def TrimedDataframe(df, target, trim = 0.1, Type = 'hoge'):
    import scipy as sp
    import numpy as np
    import pandas as pd

    trim_array      = sp.stats.trimboth(df[target], trim)
    trim_df         = pd.DataFrame(data= trim_array)
    trim_df['Type'] = Type
    return trim_df





    