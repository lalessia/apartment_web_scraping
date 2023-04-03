'''
- SCRAPING FIRST PAGE OF immobiliare.it 
    -Library: BeautifulSoup 
- GET Title and link announcment
'''

from bs4 import BeautifulSoup
import pandas as pd
import requests

url = ''
cities = ['villarosa']
i_cities = -1
column_name = []
current_page = 1
stop_scraping = False


def main():
    while True:
        global df
        global url
        

        print('current url:')
        print(url)

        if url != '':
            manage_next_page()

        global stop_scraping
        if(stop_scraping):
            break

        set_url()

        html_entities = ['ul', 'class', 'nd-list in-realEstateResults']
        imm_data = get_home_link(get_html_results(html_entities))
        if len(column_name) == 0:
            set_column_name(imm_data)
            df = pd.DataFrame(columns=column_name)
        get_home_details(imm_data)

        print('-----------------')
    print(df.info())
        
def manage_next_page():
    global url
    global current_page
    global stop_scraping

    sub_url = 'https://www.immobiliare.it/vendita-case/' + cities[i_cities] + '/?pag='
    sub_url_len = len(sub_url)

    #NB: Cambiare il last_page_number e farla diventare variabile globale
    last_page_number = int(url[sub_url_len:len(url)])
    last_page_number += 1

    entities = ['ul', 'class', 'nd-list in-realEstateResults']
    #results = get_html_results(entities)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    home_overview = soup.find("section", {"class":"in-wrapper is-listView in-searchList--list in-searchList"})
    print('home_overview')
    print(home_overview)

    if (home_overview is not None):
        current_page += 1
        tmp = sub_url + str(current_page)
       
        url = sub_url + str(current_page)
        print(tmp)
    else:
        print('Ho preso il messaggio di errore!')
        current_page = 1
        if (len(cities) == i_cities):
            stop_scraping = True

    print(url)


def set_url():
    global url
    global i_cities
    num_pag = 1

    if url == '':
        i_cities = i_cities + 1
        url = 'https://www.immobiliare.it/vendita-case/' + cities[i_cities] + '/?pag=1'
    else:
        #num_pag += 1
        pass
    return url


#METODO DA ELIMINARE - Controllare che da nessun'altra parte del codice non sia gia stato usato
def get_html_results(html_entities):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(html_entities[0], {html_entities[1]: html_entities[2]})

    return results

def get_home_link(results):
    data = []

    houses = results.find_all("li", class_="nd-list__item in-realEstateResults__item")

    for i in range(0, len(houses)):
        tmp = []

        house_detail = houses[i].find("div", class_='nd-mediaObject__content in-card__content in-realEstateListCard__content')
        a_href=house_detail.find("a",{"class":"in-card__title"}).get("href")
        title=house_detail.find("a",{"class":"in-card__title"}).get("title")

        tmp = [title, a_href]

        data.append(tmp)

    imm_data = pd.DataFrame(data, columns=['Title', 'Link'])
    return imm_data

def set_column_name(imm_data):
    for index, el in imm_data.iterrows():
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

def get_home_details(imm_data):

    detail_house_dict = {}
    for i in column_name:
        detail_house_dict[i] = None
    
    for index, el in imm_data.iterrows():
        url_detail = el.Link
        #print(url_detail)
        
        detail_house_dict['url'] = el.Link
        detail_house_dict['titolo'] = el.Title
        
        
        page_detail = requests.get(url_detail)
        soup_detail = BeautifulSoup(page_detail.content, "html.parser")
        
        location = soup_detail.find("a", {"class": "in-titleBlock__link"}) 
        location_detail = location.find_all("span", class_="in-location")
            
        for i in range (0, 3):
            if i == 0 and len(location_detail) >= 1:
                detail_house_dict['comune'] = location_detail[0].text
            if i == 1 and len(location_detail) >= 2:
                detail_house_dict['quartiere'] = location_detail[1].text
            if i == 2 and len(location_detail) >= 3:
                detail_house_dict['indirizzo'] = location_detail[2].text
                
        results = soup_detail.find("ul", {"class", "nd-list nd-list--pipe in-feat in-feat--full in-feat__mainProperty in-landingDetail__mainFeatures"})
        main_feature = results.find_all("li", class_="nd-list__item in-feat__item")

        for el in main_feature:
            if(el.get("aria-label") == 'locali'):
                detail_house_dict['num_vani'] = el.text
            elif(el.get("aria-label") == 'superficie'):
                detail_house_dict['superficiem^2'] = el.text
            elif(el.get("aria-label") == 'bagno'):
                detail_house_dict["bagni"] = el.text
            elif(el.get("aria-label") == 'asd'):
                detail_house_dict["bagni"] = el.text
                
        results = soup_detail.find("section", {"class": "in-wrapper is-detailView in-landingDetail"})
        house_detail = results.find_all("dl", class_="in-realEstateFeatures__list")
        
        for i in range(0, len(house_detail)):
            for j in range(0, (len(house_detail[i])//2)):
                title_feature = house_detail[i].find_all("dt", class_="in-realEstateFeatures__title")[j:j+1]
                value_feature = house_detail[i].find_all("dd", class_="in-realEstateFeatures__value")[j:j+1]
                
                detail_house_dict[title_feature[0].text] = value_feature[0].text
        
        # Convertire il dictionary in list portando solo i 'valori' nell'ordine
        lst_value = []
        
        for dh in detail_house_dict:
            lst_value.append(detail_house_dict[dh])
            
        df.loc[len(df)] = lst_value
    return True

if __name__ == "__main__":
    main() 






'''
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
'''
get_link_houses(houses): this method get the html (houses) in the principal page and extract all links and title relative at
single house 
'''
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

#get_house_detail(link_house): this method get the links one to one and extract the single information
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
'''