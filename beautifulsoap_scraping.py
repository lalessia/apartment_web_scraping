'''
- SCRAPING FIRST PAGE OF immobiliare.it 
    -Library: BeautifulSoup 
- GET Title and link announcment
'''

from bs4 import BeautifulSoup
import pandas as pd
import requests

column_name = []
url = ''


def get_house_from_single_page():
    current_url = ''
    url = get_url(current_url)
    current_url = url 

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find("ul", {"class": "nd-list in-realEstateResults"})
    houses = results.find_all("li", class_="nd-list__item in-realEstateResults__item")

    link_title_house = get_link_houses(houses)

    if(len(column_name) == 0):
        create_column_name(link_title_house)

    get_house_detail(link_title_house)

def get_url(url):
    if(url == ''):
        url = "https://www.immobiliare.it/vendita-case/firenze/"
    else:
        print('TO DO')
    return url

'''
get_link_houses(houses): this method get the html (houses) in the principal page and extract all links and title relative at
single house 
'''
def get_link_houses(houses):
    data = []
    for i in range(0, len(houses)):
        house_detail = houses[i].find("div", class_='nd-mediaObject__content in-card__content in-realEstateListCard__content')

        tmp = []

        a_href=house_detail.find("a",{"class":"in-card__title"}).get("href")
        title=house_detail.find("a",{"class":"in-card__title"}).get("title")

        tmp = [title, a_href]

        data.append(tmp)

    imm_data = pd.DataFrame(data, columns=['Title', 'Link'])
    return imm_data

'''
get_house_detail(link_house): this method get the links one to one and extract the single information
'''
def get_house_detail(link_house):
    print(column_name)

def create_column_name(link_house):
    for index, el in link_house.iterrows():
        url_detail = el.Link
        page_detail = requests.get(url_detail)
        soup_detail = BeautifulSoup(page_detail.content, "html.parser")
        results = soup_detail.find("section", {"class": "in-wrapper is-detailView in-landingDetail"})
    
        main_feature = results.find_all("dl", class_="in-realEstateFeatures__list")
        
        for i in range(0, len(main_feature)):
            title_feature = main_feature[i].find_all("dt", class_="in-realEstateFeatures__title")
            for el in title_feature:
                if str(el.text) not in column_name:
                    column_name.append(el.text)
    
    column_name.insert(0, 'url')
    column_name.insert(1, 'titolo')
    column_name.insert(2, 'comune')
    column_name.insert(3, 'quartiere')
    column_name.insert(4, 'indirizzo')
    column_name.insert(5, 'num_vani')
    column_name.insert(6, 'superficiem^2')
    column_name.insert(7, 'bagni')

get_house_from_single_page()

