
#%%
from numpy import NaN
import pandas as pd
from pandas.core.algorithms import value_counts
from pandas import to_numeric, to_datetime, get_dummies
import random
import matplotlib.pyplot as plt
from matplotlib.pyplot import axes, axis, figure, title
import pylab as pl
import re
plt.rcParams["figure.figsize"] = (22,14)

#%%
twingle1 = pd.read_csv('data/01_a_twingle_Seebrücke_2018-2019.csv',sep=';')
twingle2 = pd.read_csv('data/01_b_twingle_Seebrücke_2020_1.csv',sep=';')
twingle3 = pd.read_csv('data/01_c_twingle_Seebücke_2020_2.csv',sep=';')
twingle_dauer = pd.read_csv('data/02_twingle_Dauerspende.csv',sep=';')
twingle_Winter = pd.read_csv('data/03_twingle_Winterkampagne.csv',sep=';')
twingle_united = pd.read_csv('data/04_twingle_UnitedWeShare.csv',sep=';')
#TODO Check if Fundbox data contains everythin
Fundbox_2020 = pd.read_csv('data/FundraisingBox_Donations_2020_non_anonymized.csv',sep=';',encoding='latin1')

Transfert_1 = pd.read_excel('data/Kontoauszüge Seebrücke 2020.xlsx') #Everything is incoming
Transfert_2 = pd.read_excel('data/Kontoauszüge 2018-2019.xlsx',header=1) #INcoming => +
Transfert_3 = pd.read_excel('data/new_konto_2020.xlsx',parse_dates=True) #INcoming => +

#%%
# Select usefull twingle data
twingle_df = pd.concat([twingle1,twingle2,twingle3,twingle_dauer,twingle_Winter,twingle_united])
twingle_df = twingle_df[['timestamp','amount','recurring','donation_rhythm','user_city','user_country','user_email','user_company']]
twingle_df.columns = ['donated_at','amount','by_recurring','interval','city','country','email_address','company_name']

#%%
#Modify donation_rhythm to monthy interval
twingle_df['interval'].value_counts()

#%%
twingle_df['interval'] = twingle_df['interval'].str.replace('yearly','12').copy()
twingle_df['interval'] = twingle_df['interval'].str.replace('quarterly','3').copy()
twingle_df['interval'] = twingle_df['interval'].str.replace('monthly','1').copy()
twingle_df['interval'] = twingle_df['interval'].str.replace('one_time','').copy()
twingle_df['interval'] = to_numeric(twingle_df['interval'],downcast='integer').copy()

#modify to timestamp
twingle_df['donated_at'] = to_datetime(twingle_df['donated_at'])

#%%
# Select usefull Fundbox data
Fundbox_df = Fundbox_2020[['donated_at','amount','by_recurring','interval','city','country','email_address','company_name']]
Fundbox_df['donated_at'] = to_datetime(Fundbox_df['donated_at']).copy()
Fundbox_df['by_recurring'] = Fundbox_df['by_recurring'].fillna(0) #Unlike Twingle, non reccuring are nulls

#%%
#Considering that only 15 person transferred money more than once, for simplicity, I will count every transfert as a one time donation
# For the same reason, I ignored the name col and didn't try to match it with the other datasets
Transfert_1['Kontoinhaber*in'].value_counts()
#%%

#Get rid of outgoing transfert  
Transfert_2 = Transfert_2.loc[Transfert_2[' + '] > 0].copy()
Transfert_3 = Transfert_3.loc[Transfert_3['Soll/Haben'] == 'H'].copy()

#Clean the amount col 
Transfert_1['Betrag'] = Transfert_1['Betrag'].str.replace('Euro','')
Transfert_1['Betrag'] = Transfert_1['Betrag'].str.replace(' ','')
Transfert_1['Betrag'] = Transfert_1['Betrag'].str.replace(',','')
Transfert_1['Betrag'] = to_numeric(Transfert_1['Betrag'])

Transfert_2 = Transfert_2[['Unnamed: 0',' + ','Stadt','Unnamed: 1']]
Transfert_2.columns = ['donated_at','amount','city','company_name']

Transfert_1 = Transfert_1[['Datum','Betrag','Kontoinhaber*in']]
Transfert_1.columns = ['donated_at','amount','company_name']

Transfert_3.columns = ['donated_at','address','company_name','currency','amount','in/out']
Transfert_3 = Transfert_3[['donated_at','amount','company_name']]


#%%
Transfert_df = pd.concat([Transfert_1,Transfert_2,Transfert_3],ignore_index=True)
Transfert_df['donated_at'] = to_datetime(Transfert_df['donated_at'],errors='coerce')
Transfert_df = Transfert_df.dropna(subset=['donated_at'])

Transfert_df['by_recurring'] = 0
Transfert_df['email_address'] = random.sample(range(1,10000),len(Transfert_df))

#%%
#* Drop verein donations
verein_index = Transfert_df[Transfert_df['company_name'].str.contains('e\. V',flags=re.IGNORECASE)==True].index
Transfert_df.drop(verein_index,inplace=True)

#%%
#Keep just companies in the company col
Transfert_df['company_name'] = Transfert_df.company_name[Transfert_df['company_name'].str.contains('gmbh',flags=re.IGNORECASE)==True]

#%%
#Merge Twingle and Fundbox data
df = pd.concat([twingle_df,Fundbox_df,Transfert_df],ignore_index=True)

#%%
#Clean city col
df['city'] = df['city'].str.strip()
df['city'] = df['city'].str.lower()

#%%
#Factorise email to annonymize the dataset and delete email col 
cat = df['email_address'] 
codes, uniques = pd.factorize(cat)  
df['person_id'] = codes
df.drop('email_address',axis=1,inplace=True)

#%%
df['company_name'] = df['company_name'].notnull().astype('int')
df.rename(columns={'company_name':'company'})
#%%
df.to_csv('data_seebrücke_anno.csv')



#%%
#! Fundbox gives person_id
Fundbox1 = pd.read_csv('data/05_FundraisingBox_Seebruecke_Spende.csv',sep=';')
Fundbox2 = pd.read_csv('data/06_FundraisingBox_Seebuecke_donations.csv',sep=';')
Fundbox3 = pd.read_csv('data/07_FundraisingBox_Seebruecke_foerdern_Newsletter.csv',sep=';')
Fundbox4 = pd.read_csv('data/08_FundraisingBox_Seebruecke_Winterkampagne.csv',sep=';')
Fundbox5 = pd.read_csv('data/09_FundraisingBox_Seebruecke_winter_donation_campaign.csv',sep=';')
#! Strange one
#Fundbox6 = pd.read_csv('data/10_FundraisingBox_Seebruecke_foerdern_Social_Media.csv',sep=';',encoding='cp1252')
Fundbox7 = pd.read_csv('data/11_FundraisingBox_Seebruecke_foerdern_der_freitag.csv',sep=';')
# %%
#Transfert_df_5000 = Transfert_df.loc[Transfert_df['amount'] >= 5000]
#Transfert_df_5000

fund_df = pd.concat([Fundbox1,Fundbox2,Fundbox3,Fundbox4,Fundbox5,Fundbox7])

#%%
fund_df.amount.sum()
#%%
Fundbox_df.amount.sum()
#%%

small_fund = fund_df[['donated_at','amount']]

#%%
small_fund.donated_at = to_datetime(small_fund.donated_at)
#%%
small_fund.donated_at.hist()
pl.suptitle("Old Fundbox")
#%%
Fundbox_df.donated_at.hist()
pl.suptitle("New Fundbox Data")

