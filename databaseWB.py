# -*- coding: utf-8 -*-
"""
SV Portal Database
"""

import requests
import random as rand
from bs4 import BeautifulSoup as bs
import pandas as pd

#Used to get all card set info
#initial_link = 'https://shadowverse-wb.com/en/deck/cardslist' 
#initial_link = 'https://shadowverse-wb.com/en/deck/cardslist/card/?card_id=10012110'
initial_link = 'https://shadowverse-wb.com/en/deck/detail/?hash=2.1.c9iw.c9iw.c9iw.cCNE.cCNE.cCNE.cCQM.cCQM.cCQM.cY5s.cY5s.cY5s.cYb6.cYb6.cYb6.cabE.cabE.cabE.canu.canu.canu.cb1M.cwZU.cwZU.cwZU.cwl-.cwl-.cwl-.cw_m.cw_m.cw_m.czCO.czCO.czCO.czFM.czFM.czFM.czU-.czU-.czU-'
source = requests.get(initial_link).text
soup = bs(source, 'lxml')
pretty_soup = soup.prettify()

a = soup.find_all('div', attrs={"class":"card-pack-list-wrapper"})

card_box = soup.find_all('fieldset', attrs={"data-field":"card_set"})
card_set=card_box[0].find_all('label')


card_set_num_list = []
card_set_name_list = []
for card_set_spec in card_set:
    number = card_set_spec.input['value']
    name = card_set_spec.span.text
    card_set_num_list.append(number)
    card_set_name_list.append(name)
    
card_set_df = pd.DataFrame({'Set_Number':card_set_num_list, 'Set_Name':card_set_name_list})    


#Used to get all card infor pertaining to a cardset
set_number = card_set_df['Set_Number'][1]
set_name = card_set_df['Set_Name'][1]
initial_link = 'https://shadowverse-portal.com/cards?lang=en' 
added_fields = f'&card_set%5B%5D={set_number}&format=1'
source = requests.get(initial_link + added_fields).text
soup = bs(source, 'lxml')
pretty_soup = soup.prettify()

card_box = soup.find_all('a', attrs={"class":"el-card-visual-content"})
card_href_list = []
for card_box_spec in card_box:
    card_href_list.append(card_box_spec['href'])


set_num_list = []
set_name_list = []
name_list = []
trait_list = []
class_list = []
type_list = []
rarity_list = []
vial_list = []
flavor_list = []
flavor_e_list = []
skill_list = []
skill_e_list = []
atk_list = []
atk_e_list = []
life_list = []
life_e_list = []

for href_spec in card_href_list:
    initial_link = 'https://shadowverse-portal.com'    
    added_fields = href_spec + '?lang=en'
    chosen_card_number = href_spec.split('/')[2]
    source = requests.get(initial_link + added_fields).text
    soup = bs(source, 'lxml')
    pretty_soup = soup.prettify()
    
    
    
    card_info = soup.find('ul', class_="card-info-content")
    card_text = card_info.find_all('span')
    flavors   = soup.find_all('p', class_="card-content-description") 
    
    set_num_list.append(set_number)
    set_name_list.append(set_name)
    name_list.append(soup.title.text.split(' |')[0])
    trait_list.append(card_text[1].text.split('\r\n')[1])
    class_list.append(card_text[3].text.split('\r\n')[1])
    rarity_list.append(card_text[5].text.split('\r\n')[1])
    vial_list.append(card_text[7].text.split('\r\n')[1])
    flavor_list.append(flavors[0].text.split('\r\n')[1])
    
    if int(chosen_card_number[-4]) == 1: #follower
        skill_txt = soup.find_all('p', class_="card-content-skill")        
        if skill_txt[0].text == '\n':
            skill_list.append('None')
        else:
            skill_list.append(str(skill_txt[0]).split('>',1)[1].split('</p>',1)[0].split('\r\n')[-2])            
        if skill_txt[1].text == '\n':
            skill_e_list.append('None')
        else:
            skill_e_list.append(str(skill_txt[1]).split('>',1)[1].split('</p>',1)[0].split('\r\n')[-2]) 
        flavor_e_list.append(flavors[1].text.split('\r\n')[1])
        atk_list.append(soup.find_all('p', class_="el-card-status is-atk")[0].text.split('\r\n')[1])  
        atk_e_list.append(soup.find_all('p', class_="el-card-status is-atk")[1].text.split('\r\n')[1])
        life_list.append(soup.find_all('p', class_="el-card-status is-life")[0].text.split('\r\n')[1])   
        life_e_list.append(soup.find_all('p', class_="el-card-status is-life")[1].text.split('\r\n')[1]) 
        type_list.append('Follower')    
        
    else: #non-follower
        skill_list.append(str(soup.find_all('p', class_="card-content-skill")[0]).split('>',1)[1].split('</p>',1)[0].split('\r\n')[1])
        skill_e_list.append('N/A')
        flavor_e_list.append('N/A')
        atk_list.append('N/A')  
        atk_e_list.append('N/A')
        life_list.append('N/A')   
        life_e_list.append('N/A')
        if int(chosen_card_number[-4]) == 4:
            type_list.append('Spell')
        elif int(chosen_card_number[-4]) == 3:
            type_list.append('Ctd. Amulet')   
        elif int(chosen_card_number[-4]) == 2:
            type_list.append('Amulet')               
        
card_database_df = pd.DataFrame(
    {'Set_Number':set_num_list, 
     'Set_Name':set_name_list, 
     'Card_Name':name_list,
     'Card_Type':type_list,
     'Class':class_list,
     'Trait(s)':trait_list,     
     'Rarity':rarity_list,
     'Vials':vial_list,   
     'Attack (Unevo)':atk_list, 
     'Life (Unevo)':life_list,      
     'Skill (Unevo)':skill_list,
     'Attack (Evo)':atk_e_list, 
     'Life (Evo)':life_e_list,      
     'Skill (Evo)':skill_e_list,     
     }
    )  

with pd.ExcelWriter("output.xlsx") as writer:
    card_set_df.to_excel(writer, sheet_name='Set Index')
    card_database_df.to_excel(writer, sheet_name='Card Database')
  
    
  
    
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import requests
import sys

driver = webdriver.Chrome()
driver.get("https://shadowverse-wb.com/en/deck/detail/?hash=2.1.c9iw.c9iw.c9iw.cCNE.cCNE.cCNE.cCQM.cCQM.cCQM.cY5s.cY5s.cY5s.cYb6.cYb6.cYb6.cabE.cabE.cabE.canu.canu.canu.cb1M.cwZU.cwZU.cwZU.cwl-.cwl-.cwl-.cw_m.cw_m.cw_m.czCO.czCO.czCO.czFM.czFM.czFM.czU-.czU-.czU-")
html = driver.page_source
soup = bs(html, 'lxml')
pretty_soup = soup.prettify()
#regex = re.compile('.*listing-col-.*')
for EachPart in soup.select('li[class*="card-wrapper"]'):
    print(EachPart)
def LogInBooth(self):
    url = "https://shadowverse-wb.com/en/deck/detail/?hash=2.1.c9iw.c9iw.c9iw.cCNE.cCNE.cCNE.cCQM.cCQM.cCQM.cY5s.cY5s.cY5s.cYb6.cYb6.cYb6.cabE.cabE.cabE.canu.canu.canu.cb1M.cwZU.cwZU.cwZU.cwl-.cwl-.cwl-.cw_m.cw_m.cw_m.czCO.czCO.czCO.czFM.czFM.czFM.czU-.czU-.czU-" #force cache into EN
    if self.webdriver_type == "Chrome":
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(executable_path = self.webdriver_path, chrome_options=chrome_options)
        self.driver.get(url)
    elif self.webdriver_type == "Edge":
        self.driver = webdriver.Edge(executable_path = self.webdriver_path)
        self.driver.get(url)
    elif self.webdriver_type == "Firefox":
        self.driver = webdriver.Firefox(executable_path = self.webdriver_path)
        self.driver.get(url)
    else:
        print("Invalid Webdriver")
        sys.exit()  
    
  
    
  
    
  
    
  
