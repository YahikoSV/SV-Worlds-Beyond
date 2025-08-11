import random as rn
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

#Prefix Code
code_dict = {
     'B' : 'Bronze'
    ,'S' : 'Silver'
    ,'G' : 'Gold'
    ,'L' : 'Legendary'
    ,'T' : 'Ticket'
    }

#Unique Cards per Rarity
unique_dict = {
     'Bronze'    : 45    
    ,'Silver'    : 37
    ,'Gold'      : 37
    ,'Legendary' : 23
    ,'Ticket'    : 4
}

#Rates per Rarity (Normal)
rate_dict_n = {
     'Bronze'    : 0.6744
    ,'Silver'    : 0.250
    ,'Gold'      : 0.060
    ,'Legendary' : 0.015    
    ,'Ticket'    : 0.0006
}

#Rates per Rarity (Silver+ Pity)
rate_dict_s = {
     'Bronze'    : 0
    ,'Silver'    : 0.9244
    ,'Gold'      : 0.060
    ,'Legendary' : 0.015    
    ,'Ticket'    : 0.0006
}

#Rates per Rarity (Legendary Pity)
rate_dict_l = {
     'Bronze'    : 0
    ,'Silver'    : 0
    ,'Gold'      : 0
    ,'Legendary' : 1  
    ,'Ticket'    : 0
}

#Vials liquefied per Rarity
vials_liquefied_non = {
     'Bronze'    : 10
    ,'Silver'    : 50
    ,'Gold'      : 200
    ,'Legendary' : 1200  
    ,'Ticket'    : 0
}

#Vials liquefied per Animated Rarity
vials_liquefied_ani = {
     'Bronze'    : 30
    ,'Silver'    : 120
    ,'Gold'      : 450
    ,'Legendary' : 2500  
    ,'Ticket'    : 0
}

rarity_list = list(unique_dict.keys())
rate_animated = 0.08

#Inputs
simulations = 5000
num_packs = 500
cards_in_pack = 8
num_pack_pity = 10

#Vial System Inputs
#liquefy_priority = 'Normal' #Normal, Animated
num_copies_restrict = 3  #Can't vial until reaching n copies

#Plotting Inputs
pack_increment = 10
histogram_snapshot = 100
histogram_bins = 20
pack_increment_list = np.arange(pack_increment,num_packs + pack_increment, pack_increment)
total_vials_list = np.zeros((simulations,int(num_packs/pack_increment)))
vial_increment_list = np.zeros((simulations,int(num_packs/pack_increment)))
total_vials_list_ani = np.zeros((simulations,int(num_packs/pack_increment)))
vial_increment_list_ani = np.zeros((simulations,int(num_packs/pack_increment)))


#################################################################################

def pull_card(rarity_list, rate_dict, u_dict, rate_animated):
    for card_pack in range(0,cards_in_pack) :
        random_rarity_num = rn.random() #gacha rarity
        random_animated_num = rn.random()
        if random_rarity_num < rate_dict['Bronze']:
            card_rarity = rarity_list[0]
        elif random_rarity_num < rate_dict['Bronze'] + rate_dict['Silver']:
            card_rarity = rarity_list[1]
        elif random_rarity_num < rate_dict['Bronze'] + rate_dict['Silver'] + rate_dict['Gold']:
            card_rarity = rarity_list[2]
        elif random_rarity_num < rate_dict['Bronze'] + rate_dict['Silver'] + rate_dict['Gold'] + rate_dict['Legendary']:
            card_rarity = rarity_list[3]       
        else:
            card_rarity = rarity_list[4]
        random_name = rn.randrange(0,u_dict[card_rarity]) #gacha name
        random_animated = 'A' if random_animated_num < rate_animated else 'N'
        card_id_w_ani = card_rarity[0]+str(random_name)+random_animated
        card_id = card_rarity[0]+str(random_name)
        return card_id, card_id_w_ani

    
def potential_vials(card_w_copies_over, count_cards, count_cards_w_ani, card_liquefy_1st_prefix, vials_liquefy_1st, vials_liquefy_2nd):
    vials_gained = 0
    for card_id in cards_w_copies_over:
        excess = count_cards[card_id] - num_copies_restrict
        min_excess_non_prio = min(excess,count_cards_w_ani[f'{card_id}{card_liquefy_1st_prefix}'])
        vials_gained_card = vials_liquefy_1st[code_dict[card_id[0]]] * (min_excess_non_prio) + vials_liquefy_2nd[code_dict[card_id[0]]] * (excess - min_excess_non_prio)
        vials_gained += vials_gained_card
    return vials_gained or 0 #To not return None type


for sim_num in range(0,simulations):
    count_pack_pity = 0 #last pack (legendary)
    count_card_pity = 0 #last card (silver+, legendary)
    count_card_list = []
    count_card_list_w_ani = []
    new_vial_total = 0 
    new_vial_total_ani = 0
    #Pulling Session
    for pack in range(0,num_packs):
        count_pack_pity += 1 #disabling this removes legendary pity
        for card in range(0,cards_in_pack):
            count_card_pity += 1 
            if count_pack_pity == num_pack_pity and card == cards_in_pack - 1: #Legendary: No leggo in 10 packs and is the 8th pack
                card_id, card_id_w_ani = pull_card(rarity_list, rate_dict_l, unique_dict, rate_animated)
            elif count_card_pity == cards_in_pack: #Silver+: No Silver+ and is the 8th pack
                card_id, card_id_w_ani = pull_card(rarity_list, rate_dict_s, unique_dict, rate_animated)
            else: #Normal
                card_id, card_id_w_ani = pull_card(rarity_list, rate_dict_n, unique_dict, rate_animated)       
            count_card_list.append(card_id) #add to cardlist
            count_card_list_w_ani.append(card_id_w_ani) #add to cardlist
            if card_id[0] in [rarity_list[3][0]]: #check if card is Legendary
                count_pack_pity = 0
            if card_id[0] in [i[0] for i in rarity_list[1:4]]: #check if card is Silver+
                count_card_pity = 0                                           
        count_card_pity = 0
    
    
        if (pack + 1) % pack_increment == 0:
            #Count your cards and vials
            count_cards = Counter(count_card_list)   
            count_cards_w_ani = Counter(count_card_list_w_ani)
            current_vial_total = new_vial_total
            current_vial_total_ani = new_vial_total_ani
            
            #Vial Potential
            cards_w_copies_over = [card_id for card_id, copies in count_cards.items() if copies > num_copies_restrict]
            new_vial_total = potential_vials(cards_w_copies_over, count_cards, count_cards_w_ani, 'N', vials_liquefied_non, vials_liquefied_ani)  
            new_vial_total_ani = potential_vials(cards_w_copies_over, count_cards, count_cards_w_ani, 'A', vials_liquefied_ani, vials_liquefied_non)
              
            vials_gained_increment = new_vial_total - current_vial_total
            vial_increment_list[sim_num][int(((pack+1)/pack_increment)-1)] = vials_gained_increment
            total_vials_list[sim_num][int(((pack+1)/pack_increment)-1)] = new_vial_total
            
            vials_gained_increment_ani = new_vial_total_ani - current_vial_total_ani
            vial_increment_list_ani[sim_num][int(((pack+1)/pack_increment)-1)] = vials_gained_increment_ani
            total_vials_list_ani[sim_num][int(((pack+1)/pack_increment)-1)] = new_vial_total_ani
            #print(pack+1, new_vial_total, current_vial_total, vials_gained_increment)



#Graphs

#1 player        
critical_mass = plt.plot(pack_increment_list,vial_increment_list[0])
critical_mass_ani = plt.plot(pack_increment_list,vial_increment_list_ani[0])
plt.title(f'Vials per {pack_increment} packs (1 player)')
plt.legend(['Normal','Animated'])
plt.xlabel('Card Packs')
plt.ylabel('Vials liquefiable')
plt.text(0,7000,f'100 Packs = {int(vial_increment_list[0][int((histogram_snapshot/pack_increment)-1)])}-{int(vial_increment_list_ani[0][int((histogram_snapshot/pack_increment)-1)])}')
#plt.text(0,7000,f'Average = {int(np.mean(vial_increment_list))}')
plt.show()

total_mass = plt.plot(pack_increment_list,total_vials_list[0])
total_mass_ani = plt.plot(pack_increment_list,total_vials_list_ani[0])
plt.title('Vials total (1 player)')
plt.xlabel('Card Packs')
plt.ylabel('Vials liquefiable')
plt.text(0,100000,f'100 Packs = {int(total_vials_list[0][int((histogram_snapshot/pack_increment)-1)])}-{int(total_vials_list_ani[0][int((histogram_snapshot/pack_increment)-1)])}')
plt.show()


avg_vial_increment_list = [vial_increment_list[:,i].sum()/len(vial_increment_list[:,i]) for i in range(0,vial_increment_list.shape[1])]
avg_total_vials_list =  [total_vials_list[:,i].sum()/len(total_vials_list[:,i]) for i in range(0,total_vials_list.shape[1])]
avg_vial_increment_list_ani = [vial_increment_list_ani[:,i].sum()/len(vial_increment_list_ani[:,i]) for i in range(0,vial_increment_list_ani.shape[1])]
avg_total_vials_list_ani =  [total_vials_list_ani[:,i].sum()/len(total_vials_list_ani[:,i]) for i in range(0,total_vials_list_ani.shape[1])]


#Histogram of N players at X packs
hist_vials_per_player = plt.hist(total_vials_list[:,int((histogram_snapshot/pack_increment)-1)],histogram_bins) 
plt.title(f'Vial distribuition of {simulations} players @{histogram_snapshot} packs')
plt.xlabel('Vials liquefiable')
plt.ylabel('Players')
plt.text(11000,500,f'Median : {int(np.median(total_vials_list[:,int((histogram_snapshot/pack_increment)-1)]))}')
plt.show(hist_vials_per_player)


#N Players
avg_critical_mass = plt.plot(pack_increment_list,avg_vial_increment_list)
avg_critical_mass_ani = plt.plot(pack_increment_list,avg_vial_increment_list_ani)
plt.title(f'Average Vials per {pack_increment} packs (n={simulations})')
plt.legend(['Normal','Animated'])
plt.xlabel('Card Packs')
plt.ylabel('Vials liquefiable')
plt.text(0,3740,f'100 Packs = {int(avg_vial_increment_list[int((histogram_snapshot/pack_increment)-1)])}-{int(avg_vial_increment_list_ani[int((histogram_snapshot/pack_increment)-1)])}')
#plt.text(100,4200,f'Average = {int(np.mean(avg_vial_increment_list))}')
plt.show()
plt.show()

avg_total_mass = plt.plot(pack_increment_list,avg_total_vials_list)
avg_total_mass_ani = plt.plot(pack_increment_list,avg_total_vials_list_ani)
plt.title(f'Average Vials total (n={simulations})')
plt.legend(['Normal','Animated'])
plt.xlabel('Card Packs')
plt.ylabel('Vials liquefiable')
plt.text(0,100000,f'100 Packs = {int(avg_total_vials_list[int((histogram_snapshot/pack_increment)-1)])}-{int(avg_total_vials_list_ani[int((histogram_snapshot/pack_increment)-1)])}')
plt.show()
