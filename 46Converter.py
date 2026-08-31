# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


code_list = pd.read_excel('Tables/64xmalcode.xlsx',dtype={'code':'string'})
code_dict = dict(zip(code_list['number'],code_list['code']))
code_dict_r = dict(zip(code_list['code'],code_list['number']))

def cardnum_to_code(number):
    digit_1, remain_1 = number//64**3  , number % 64**3
    digit_2, remain_2 = remain_1//64**2, remain_1 % 64**2
    digit_3, digit_4 =  remain_2//64   , remain_2 % 64
    return f'{code_dict[digit_1]}{code_dict[digit_2]}{code_dict[digit_3]}{code_dict[digit_4]}'

def code_to_cardnum(code):
    add_1 = code_dict_r[code[0]] * 64**3
    add_2 = code_dict_r[code[1]] * 64**2
    add_3 = code_dict_r[code[2]] * 64**1
    add_4 = code_dict_r[code[3]] * 64**0
    return add_1+add_2+add_3+add_4    


#link = 'https://shadowverse-wb.com/en/deck/detail/?hash=1.2.cEZs.cEZs.cEaA.dmj6.dmyk.dmyk.dmyk.dmyu.eXnk.eXnu.eXnu.eXnu.evTW.evTW.evTW.evi-.evi-.evi-.evj8.evj8.evj8.evm6.evm6.evm6.evyc.evyc.evyc.ewCE.ewCE.ewCE.ewCO.ewCO.ewCO.fHts.fIck.fIck.fIck.fIcu.fIcu.fIcu'
def link_to_decklist(link,filename):
    link_processed = (link.split('.')[3:])
    columns = ['code', 'card_num', 'card_name', 'card_class', 'card_type', 'quantity', 'cost', 'atk', 'def', 'skills', 'comments']
    deck_df = pd.DataFrame(columns=columns)
    for code_i in link_processed:
        if code_i in deck_df['code'].values:
            idx_num = deck_df.index[deck_df['code'] == code_i]
            deck_df.loc[idx_num,'quantity'] += 1
        else:
            card_num = code_to_cardnum(code_i)
            initial_link = f'https://sva.hypd.asia/en/card/{str(card_num)}' 
            source = requests.get(initial_link).text
            soup = bs(source, 'lxml')          
            card_type = soup.find_all('li')[1].text
            new_row = {'code' : code_i,
                       'card_num' : card_num,
                       'card_name' : soup.find('h1').text,
                       'card_class' : soup.find_all('li')[0].text,
                       'card_type' : card_type,
                       'quantity' : 1,
                       'cost' : int(soup.find_all('li')[2].text[5:]),
                       'atk' : int(soup.find_all('li')[3].text[7:]) if card_type == 'Follower' else 'N/A',
                       'def' : int(soup.find_all('li')[4].text[8:]) if card_type == 'Follower' else 'N/A',
                       'skills' : str(soup.find_all('p')[0]),
                       'comments' : ''}
            deck_df = pd.concat([deck_df, pd.DataFrame([new_row])], ignore_index=True)   
    deck_df.to_excel(f'Decklists/{filename}.xlsx')
    
deck_df = pd.read_excel('Decklists/Evo_Forest.xlsx',index_col=0)



with open("Mulligan/Evo_Forest.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)
a = content.split('\n')
Obj_Phase = False
Mull_Phase = False
n = 0
for line in a:
    n += 1
    print(n)
    if line == '~~Objective~~':
        Obj_Phase = True
        Mull_Phase = False
    elif line == '~~Mulligan_Rules~~':
        Mull_Phase = True
        Obj_Phase = False
    elif Obj_Phase == True:
        info = [x for x in line.split(' ') if x != '']
        if len(info) ==3:
            real_name = deck_df.loc[deck_df.index[deck_df['card_name'].str.contains(info[1], case=False, na= False)][0]]['card_name']           
            print(info[0],info[1],info[2],real_name)
    elif Mull_Phase == True:
        info = [x for x in line.split(' ') if x != '']
        if len(info) ==2:
            real_name = deck_df.loc[deck_df.index[deck_df['card_name'].str.contains(info[0], case=False, na= False)][0]]['card_name']                        
            print(info[0],info[1],real_name)

        


