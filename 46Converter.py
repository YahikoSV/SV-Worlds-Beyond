# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import random as rn
import time

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

link = 'https://shadowverse-wb.com/en/deck/detail/?hash=1.1.e4Gg.e4Gg.e4Gg.eVLe.eVLe.et1G.et1G.fds6.fds6.fds6.dhqm.dhqm.etGk.etGk.etGk.fe5k.feLM.feLM.feLM.fe8s.fe8s.fe8s.e6x8.e6x8.e6x8.fea-.fea-.fea-.etl-.etl-.etl-.feOU.feOU.feOU.etm8.etm8.etm8.fGAU.fGAU.fGAU'
#link = 'https://shadowverse-wb.com/en/deck/detail/?hash=1.2.cEZs.cEZs.cEZs.eXnu.eXnu.eXnu.evi-.evi-.evi-.fgIM.fgIM.fgIM.fIQE.fIQE.dmEA.dmEA.dmEA.fgX-.fgX-.fgX-.fgb6.fgb6.fgb6.dmyk.dmyk.dmyk.fgqk.fgqk.fgqk.e9NO.e9NO.e9NO.fgnc.fgnc.fgnc.fh1E.fh1E.fh1E.fIcu.fIcu'
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
    try:
        with open(f"Mulligan/{filename}.txt", "x", encoding="utf-8") as file:
            file.write("~~Objective~~\n~~Mulligan_Rules~~")
    except FileExistsError:
        print("The file already exists! No data was overwritten.")
    return deck_df

deck_df = link_to_decklist(link,'Ramp_Dragon')    
deck_df = pd.read_excel('Decklists/Loot_Sword_Beyond.xlsx',index_col=0)


def mullobj_db(filename):
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
    a = content.split('\n')
    Obj_Phase = False
    Mull_Phase = False
    
    mull_df = pd.DataFrame(columns=['card_name','qty_cond','condition_met'])
    obj_df = pd.DataFrame(columns=['card_name','qty_cond','turn_num','condition_met','condition_met_total'])
    
    for line in a:
        if '~~Objective~~' in line:
            Obj_Phase = True
            Mull_Phase = False
        elif '~~Mulligan_Rules~~' in line:
            Mull_Phase = True
            Obj_Phase = False
        elif Obj_Phase == True:
            info = [x for x in line.split(' ') if x != '']
            if len(info) ==3:
                if info[1][0].lower() == '$':
                    print(info[0],info[1],info[2])
                    obj_df = pd.concat([obj_df, pd.DataFrame([{'card_name':info[1],
                                                                 'qty_cond':int(info[2]),
                                                                 'turn_num':int(info[0][1:]),
                                                                 'condition_met':0,
                                                                 'condition_met_total':0}])],ignore_index=True) 
                else:    
                    real_name = deck_df.loc[deck_df.index[deck_df['card_name'].str.contains(info[1], case=False, na= False)][0]]['card_name']           
                    print(info[0],info[1],info[2],real_name)
                    obj_df = pd.concat([obj_df, pd.DataFrame([{'card_name':real_name,
                                                                 'qty_cond':int(info[2]),
                                                                 'turn_num':int(info[0][1:]),
                                                                 'condition_met':0,
                                                                 'condition_met_total':0}])],ignore_index=True)
        elif Mull_Phase == True:
            info = [x for x in line.split(' ') if x != '']
            if len(info) ==2:
                if info[0][0].lower() == '$':
                    print(info[0],info[1])
                    mull_df = pd.concat([mull_df, pd.DataFrame([{'card_name':info[0],
                                                                 'qty_cond':int(info[1]),
                                                                 'condition_met':0}])],ignore_index=True)                
                else:
                    real_name = deck_df.loc[deck_df.index[deck_df['card_name'].str.contains(info[0], case=False, na= False)][0]]['card_name']                        
                    print(info[0],info[1],real_name)
                    mull_df = pd.concat([mull_df, pd.DataFrame([{'card_name':real_name,
                                                                 'qty_cond':int(info[1]),
                                                                 'condition_met':0}])],ignore_index=True)
    return mull_df,obj_df
mull_df, obj_df = mullobj_db("Mulligan/Ramp_Dragon_Normal_1st.txt")

        
### FIRST METHOD - ALL DATAFRAMES### 93s
def initializePiles(deck_df):
    hand = pd.DataFrame(columns=['card_name','cost'])
    void = pd.DataFrame(columns=['card_name','cost'])    
    deck = pd.DataFrame(columns=['card_name','cost'])
    for i in range(0,len(deck_df)):
        quantity = deck_df.loc[i]['quantity']
        new_row = {
            'card_name' : deck_df.loc[i]['card_name'],
            'cost'      : deck_df.loc[i]['cost'],
            }
        for j in range(0,quantity):
            deck = pd.concat([deck, pd.DataFrame([new_row])], ignore_index=True) 
    return deck,hand,void
        
        
def transferAtoB(pile_A, pile_B, qty=1, chosen=[]):  
    if len(chosen) == 0:
        chosen_cards = rn.sample(list(pile_A.index),k=qty)
    else:
        chosen_cards = chosen
    pile_B = pd.concat([pile_B, pile_A.loc[chosen_cards]], ignore_index=False) 
    pile_A = pile_A.drop(chosen_cards)
    return pile_A, pile_B
    
start_time = time.time() 
iterations = 1000
all_conditions_met = 0
for i in range(0,iterations):   
    ### Mulligan Phase
    #Step 1 InitializePiles
    deck,hand,void =  initializePiles(deck_df)
    #Step 2 Draw 4 Cards
    deck,void = transferAtoB(deck, void, qty=4)
    #Step 3 Check every mulligan rule if condition is met
    keep_list = []
    for row in range(0,len(mull_df)):
        if len(void[void['card_name'] == mull_df.loc[row]['card_name']]) >= mull_df.loc[row]['qty_cond']:
            chosen = list(void.index[void['card_name'].str.contains(mull_df.loc[row]['card_name'], case=False, na= False)][0:mull_df.loc[row]['qty_cond']])
            void,hand = transferAtoB(void, hand, chosen=chosen)  
    #Step 4 Redraw X Cards discarded, return discarded cards to deck
    deck,hand =transferAtoB(deck, hand, qty=4-len(hand))
    void,deck =transferAtoB(void, deck, qty=len(void))
    
    ### Game Phase
    turn = 0
    for turn_num in range(1,obj_df['turn_num'].max()+1):
        ### Draw
        deck,hand =transferAtoB(deck, hand, qty=1)    
        ### Check if object satisfies condition
        turn_obj_df = obj_df[obj_df['turn_num'] == turn_num].reset_index()
        for row in range(0,len(turn_obj_df)):
            if len(hand[hand['card_name'] == turn_obj_df.loc[row]['card_name']]) >= turn_obj_df.loc[row]['qty_cond']: 
                obj_df.loc[turn_obj_df.loc[row]['index'],'condition_met'] = 1
                obj_df.loc[turn_obj_df.loc[row]['index'],'condition_met_total'] += 1
    if obj_df['condition_met'].sum() == len(obj_df):
        all_conditions_met += 1
    obj_df['condition_met'] = 0
for row in range(0,len(obj_df)):
    print(f'{obj_df.loc[row]["turn_num"]} {obj_df.loc[row]["card_name"]} = {obj_df.loc[row]["condition_met_total"]}/{iterations}')
print(f'All conditions met {all_conditions_met}/{iterations}')
total_time = time.time() - start_time
print(total_time)        
obj_df['condition_met_total'] = 0
    
'''
#MVP
DONE! 0: Create Deck/Hand/Void
DONE! 1. Draw 4 cards
DONE! 2. Check if mulligan rules satisfy per row 
DONE! - if true, keep card
DONE! - if false, mull card
DONE! - keep X mull cards in a different 'hand'
DONE! - Draw X cards
DONE! 3. Every turn draw 1 card
DONE! - If objective turn is reached check objective
DONE! - Counts wins/lose/win% for that objective
DONE! - at the last turn and condition, count wins/lose/win% that satisfies ALL objectives
'''

'''
Feedback: Very SLOW! - need to change some dataframes into index lookup lists
'''
        
###SECOND METHOD ###LIST METHOD 8secs
def initializePiles(deck_df):
    hand = []
    void = []  
    deck = []
    for j in range(0,len(deck_df)):
        quantity = deck_df.loc[j]['quantity']
        card_name = deck_df.loc[j]['card_name'] 
        deck.extend([card_name] * quantity)
    return deck,hand,void

def transferAtoB(pile_A, pile_B, qty=1, chosen=[]):  
    if len(chosen) == 0:
        chosen_cards = rn.sample(pile_A,k=qty)
    else:
        chosen_cards = chosen
    pile_B.extend(chosen_cards)
    for card in chosen_cards:
        pile_A.remove(card)
    return pile_A, pile_B

start_time = time.time() 
iterations = 1000
all_conditions_met = 0
for i in range(0,iterations):   
    ### Mulligan Phase
    #Step 1 InitializePiles
    deck,hand,void =  initializePiles(deck_df)
    #Step 2 Draw 4 Cards
    deck,void = transferAtoB(deck, void, qty=4)
    #Step 3 Check every mulligan rule if condition is met
    keep_list = []
    for row in range(0,len(mull_df)):
        if void.count(mull_df.loc[row]['card_name']) >= mull_df.loc[row]['qty_cond']:
            keep_list.extend([mull_df.loc[row]['card_name']] * mull_df.loc[row]['qty_cond'])
    void,hand = transferAtoB(void, hand, chosen=keep_list)  
    #Step 4 Redraw X Cards discarded, return discarded cards to deck
    deck,hand =transferAtoB(deck, hand, qty=4-len(hand))
    void,deck =transferAtoB(void, deck, qty=len(void))
    
    ### Game Phase
    turn = 0
    for turn_num in range(1,obj_df['turn_num'].max()+1):
        ### Draw
        deck,hand = transferAtoB(deck, hand, qty=1)    
        ### Check if object satisfies condition
        turn_obj_df = obj_df[obj_df['turn_num'] == turn_num].reset_index()
        for row in range(0,len(turn_obj_df)):
            if  hand.count(turn_obj_df.loc[row]['card_name']) >= turn_obj_df.loc[row]['qty_cond']: 
                obj_df.loc[turn_obj_df.loc[row]['index'],'condition_met'] = 1
                obj_df.loc[turn_obj_df.loc[row]['index'],'condition_met_total'] += 1
    if obj_df['condition_met'].sum() == len(obj_df):
        all_conditions_met += 1
    obj_df['condition_met'] = 0
for row in range(0,len(obj_df)):
    print(f'{obj_df.loc[row]["turn_num"]} {round(obj_df.loc[row]["condition_met_total"]/iterations*100,2)}% {obj_df.loc[row]["card_name"]} = {obj_df.loc[row]["condition_met_total"]}/{iterations}')
print(f'All {round(all_conditions_met/iterations*100,2)}% {all_conditions_met}/{iterations}')
total_time = time.time() - start_time
print(total_time)        
obj_df['condition_met_total'] = 0    
    


'''
3pts objective
1.) Generic conditions 2cost, follower
    - From int obj to class obj
2.) and/or/prioity conditions
3.) extra draw functionality


'''

### THIRD METHOD CLASS METHOD
from collections import Counter

class Card:
    def __init__(self,c_name,c_type,c_cost):
        self.card_name = c_name
        self.card_type = c_type
        self.card_cost = int(c_cost)

def initializePiles(deck_df):
    hand = []
    void = []  
    deck = []
    for j in range(0,len(deck_df)):
        quantity = deck_df.loc[j]['quantity']
        card_class = Card(deck_df.loc[j]['card_name'],deck_df.loc[j]['card_type'],deck_df.loc[j]['cost'])
        deck.extend([card_class] * quantity)
    return deck,hand,void       

def transferAtoB(pile_A, pile_B, qty=0, chosen=[]):  
    if chosen == []:
        chosen_cards = rn.sample(pile_A,k=qty)
    else:
        chosen_cards = chosen
    pile_B.extend(chosen_cards)
    for card in chosen_cards:
        pile_A.remove(card)
    return pile_A, pile_B


def run_simulator(deck_df,mull_df,obj_df):
    start_time = time.time() 
    iterations = 2000
    all_conditions_met = 0
    for i in range(0,iterations):  
        deck,hand,void =  initializePiles(deck_df)
        deck,void = transferAtoB(deck, void, qty=4)
        cnt_cost = Counter(card.card_cost for card in void)
        cnt_type = Counter(card.card_type for card in void)
        cnt_name = Counter(card.card_name for card in void)
        
        for row_num in range(0,len(mull_df)):
            card_name_req = mull_df.loc[row_num]['card_name']
            card_qty_req = mull_df.loc[row_num]['qty_cond']
            if card_name_req[0] == '$': #special condition
                if card_name_req[0:5].lower() == '$cost': #sp1: cost
                    candidates = [card for card in void if card.card_cost == int(card_name_req[6:])]
                    void,hand = transferAtoB(void, hand, chosen=candidates[0:card_qty_req])   
                    #print(row_num,'cost',[card.card_name for card in hand],[card.card_name for card in void])
                elif card_name_req[0:5].lower() == '$type': #sp2: follower
                    candidates = [card for card in void if card.card_type == card_name_req[6:]]
                    void,hand = transferAtoB(void, hand, chosen=candidates[0:card_qty_req])
                    #print(row_num,'follow',[card.card_name for card in hand],[card.card_name for card in void])
            else:
                candidates = [card for card in void if card.card_name == card_name_req]
                void,hand = transferAtoB(void, hand, chosen=candidates[0:card_qty_req])   
                #print(row_num,'name',[card.card_name for card in hand],[card.card_name for card in void])
                
        deck,hand =transferAtoB(deck, hand, qty=4-len(hand))
        void,deck =transferAtoB(void, deck, qty=len(void))    
        
        ### Game Phase
        for turn_num in range(1,obj_df['turn_num'].max()+1):
            ### Draw
            deck,hand = transferAtoB(deck, hand, qty=1)    
            ### Check if object satisfies condition
            turn_obj_df = obj_df[obj_df['turn_num'] == turn_num].reset_index()
            cnt_cost = Counter(card.card_cost for card in hand)
            cnt_type = Counter(card.card_type for card in hand)
            cnt_name = Counter(card.card_name for card in hand)
            for row_num in range(0,len(turn_obj_df)):
                card_name_req = turn_obj_df.loc[row_num]['card_name']
                card_qty_req = turn_obj_df.loc[row_num]['qty_cond']
                if card_name_req[0:5].lower() == '$cost': #sp1: cost
                    candidates = [card for card in hand if card.card_cost == int(card_name_req[6:])]
                elif card_name_req[0:5].lower() == '$type': #sp2: follower
                    candidates = [card for card in hand if card.card_type == card_name_req[6:]]
                else:
                    candidates = [card for card in hand if card.card_name == card_name_req]
                obj_df.loc[turn_obj_df.loc[row_num]['index'],'condition_met'] = 1 if len(candidates) >= card_qty_req else 0
                obj_df.loc[turn_obj_df.loc[row_num]['index'],'condition_met_total'] += 1 if len(candidates) >= card_qty_req else 0            
        if obj_df['condition_met'].sum() == len(obj_df):
            all_conditions_met += 1
        obj_df['condition_met'] = 0
        
    for row in range(0,len(obj_df)):
        #print(f'{obj_df.loc[row]["turn_num"]} {round(obj_df.loc[row]["condition_met_total"]/iterations*100,2)}% {obj_df.loc[row]["card_name"]} = {obj_df.loc[row]["condition_met_total"]}/{iterations}')
        print(f'{round(obj_df.loc[row]["condition_met_total"]/iterations*100,2)}%')
    print(f'All {round(all_conditions_met/iterations*100,2)}% {all_conditions_met}/{iterations}')
    total_time = time.time() - start_time
    print(total_time)        
    obj_df['condition_met_total'] = 0    

run_simulator(deck_df,mull_df,obj_df)
