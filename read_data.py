import pandas as pd

def get_data():
    data = pd.read_excel('spring2023.xlsx', header=0)
    # data.dropna()
    data1 = pd.read_excel('fall2023.xlsx', header=0)
    data1['abbr_name'] = data1['Course']+data1['Number']
    data['abbr_name'] = data['Course']+data['Number']
    
    # res = offerings[~offerings['abbr_name'].isin(data1['abbr_name'])]
    # data = data[~data['abbr_name'].isin(data1['abbr_name'])]
    # # res = res[['full_name', 'abbr_name', 'credits','semester', 'school']]
    # print(data.head())
    # print(data[data['abbr_name'].str.startswith('EECS')])
    
    data.dropna(subset=['Course'], inplace=True)
    
    data['full_name']=data['Course title']
    data['credits'] = data['Max Hrs'].astype(int)
    data['semester'] = 'Spring2023'
    data['school'] = 1
    data['year'] = 2023
    data['prof']=data['Instructor']
    
    print(data.head())
    print(len(data))
    offerings = data.copy()
    
    offerings['start_time'] = offerings['Start']
    offerings['end_time'] = offerings['End']
    offerings = offerings[['full_name', 'abbr_name', 'start_time', 'end_time', 'semester', 'year', 'prof', 'school']]
    classes = data.groupby(['abbr_name'], as_index=False).agg({'full_name': 'first', 'credits': 'first', 'semester': 'first', 'school': 'first'})
    # classes['offerings'] = offerings.filter(lambda x: x['abbr_name'] == classes['abbr_name'])
    # offerings['course'] = classes.index[True].tolist()
    
    # set offerings['course'] to the index of the row in classes with the same abbr_name
    offerings['course'] = offerings['abbr_name'].apply(lambda x: classes[classes['abbr_name'] == x].index[0]+1)
    
    # offerings['course'] = classes.index.tolist().index()
    print(classes.head())
    print(len(classes))
    # print(classes[classes['abbr_name'] == 'EECS 168'])
    # distinct_classes = pd.concat([data, data1]).drop_duplicates(subset=['abbr_name'], keep=False)
    # res = pd.merge(classes, distinct_classes, on=list(classes.columns))
    # print(res.head())
    
    
    offerings.to_csv('offerings3.csv', index=False)
    # classes.to_csv('classes3.csv', index=False)
    
    return classes, offerings
    # offerings['']
    
    # return data
    # offerings = data.copy()
    
# get_data()
if __name__ == "__main__":
    get_data()