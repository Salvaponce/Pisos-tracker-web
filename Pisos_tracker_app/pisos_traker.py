import os
import re
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

class PisosAPI:
    def __init__(self, place, base_url, filters):
        self.place = place
        self.base_url = base_url
        self.filters = filters
        options = self.get_web_driver_options()
        self.set_browser_options(options)
        self.driver = self.get_chrome_web_driver(options)

    def get_chrome_web_driver(self, options):
        GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
        CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
        options.binary_location = os.environ.get("GOOGLE_CHROME_PATH")
        return webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')), chrome_options=options)
        #return webdriver.Chrome(executable_path='Pisos_tracker_app/chromedriver.exe', chrome_options=options)

    def get_web_driver_options(self):
        return webdriver.ChromeOptions()

    def set_browser_options(self, options): 
        options.add_argument('--ignore-certificate-errors')  
        options.add_argument('--incognito')     
        options.add_argument("--headless")        
        options.headless = True
        options.add_argument("window-size=1400,800")
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

    def run(self):
        print(f'Buscando en {self.place}...')
        links = self.get_houses_links()
        #time.sleep(5)
        if not links:
            print('Parar Script')
            return
        print('Obteniendo informacion...')
        #print(links)
        houses = self.get_house_info(links)
        self.driver.quit()
        return houses

    # Buscamos los links de la casa que buscamos entre los precios que hemos elegido   
    def get_houses_links(self):
        house = ""
        if 'pisos' in self.base_url:
            if self.filters == 'Barato':
                house = self.get_by_pisos(f'https://www.pisos.com/alquiler/pisos-{self.place}/asc/')
            elif self.filters == 'Recientes':
                house = self.get_by_pisos(f'https://www.pisos.com/alquiler/pisos-{self.place}//fecharecientedesde-desc/')
            else:
                house = self.get_by_pisos(f'https://www.pisos.com/alquiler/pisos-{self.place}/')
        elif 'idealista' in self.base_url:
            if self.filters == 'Barato':
                house=self.get_by_idealista(f'https://www.idealista.com/alquiler-viviendas/{self.place}-{self.place}/?ordenado-por=precios-asc')
            elif self.filters == 'Recientes':
                house=self.get_by_idealista(f'https://www.idealista.com/alquiler-viviendas/{self.place}-{self.place}/?ordenado-por=fecha-publicacion-desc')
            else:
                house=self.get_by_idealista(f'https://www.idealista.com/alquiler-viviendas/{self.place}-{self.place}/')
        elif 'habitaclia' in self.base_url:
            if self.filters == 'Barato':
                house=self.get_by_habitaclia(f'https://www.habitaclia.com/alquiler-{self.place}.html?ordenar=precio_mas_bajo')
            elif self.filters == 'Recientes':
                house=self.get_by_habitaclia(f'https://www.habitaclia.com/alquiler-{self.place}.html?ordenar=mas_recientes')
            else:
                house=self.get_by_habitaclia(f'https://www.habitaclia.com/alquiler-{self.place}.html')
        #elif 'yaencontre' in self.base_url:
        #    if self.filters == 'Barato':
        #        house=self.get_by_yaencontre(f'https://www.yaencontre.com/alquiler/pisos/{self.place}/o-precio-asc')
        #    elif self.filters == 'Recientes':
        #        house=self.get_by_yaencontre(f'https://www.yaencontre.com/alquiler/pisos/{self.place}/o-recientes')
        #    else:
        #        house=self.get_by_yaencontre(f'https://www.yaencontre.com/alquiler/pisos/{self.place}/')
        return house
       

    def get_by_pisos(self, link):
        self.driver.get(link)
        #time.sleep(2)
        result_link_list = self.driver.find_elements_by_class_name('ad-preview--has-desc')
        links = [self.base_url + link.get_attribute('data-lnk-href') for link in result_link_list][:3]
        return links

    def get_by_idealista(self, link):
        self.driver.get(link)
        #time.sleep(2)
        result_link_list = self.driver.find_elements_by_class_name('item-link')
        links = [self.base_url + link.get_attribute('href') for link in result_link_list][:3]
        return links

    def get_by_habitaclia(self, link):
        self.driver.get(link)
        #time.sleep(2)
        result_link_list = self.driver.find_elements_by_class_name('js-item-with-link')
        links = [link.get_attribute('data-href') for link in result_link_list][:3]
        return links

    def get_house_info(self, links): 
        houses = []       
        for link in links:
            self.driver.get(link)
            price = self.get_price()
            adress = self.get_adress()
            position = self.get_position()
            image = self.get_image()  
            house_info = {}   
            #print(link, adress, image, price)     
            if price and adress and image:
                house_info = {
                'link':link,
                'adress': adress,
                'position': position,
                'image':image,  
                'price':price
                }
                houses.append(house_info)
        return houses

    def get_price(self):
        price = 0
        try:
            if 'pisos' in self.base_url:
                price = self.driver.find_element_by_class_name('jsPrecioH1').text
            elif 'idealista' in self.base_url:
                price = self.driver.find_element_by_class_name('txt-bold').text
            elif 'habitaclia' in self.base_url:
                price_list = self.driver.find_elements_by_class_name('font-2')
                for elem in price_list:
                    try:
                        if elem.get_attribute('itemprop') == 'price':
                            return elem.text
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)
            return None
        return price

    def get_adress(self):
        adress = ""
        try:
            if 'pisos' in self.base_url or 'habitaclia' in self.base_url:
                adress = self.driver.find_element_by_tag_name('h1').text
            elif 'idealista' in self.base_url:
                adress = self.driver.find_element_by_class_name('main-info__title-main').text
        except Exception as e:
            print(e)
            return None
        return adress

    def get_position(self):
        position = ""
        try:
            if 'pisos' in self.base_url:
                position = self.driver.find_element_by_class_name('position').text        
            elif 'idealista' in self.base_url:
                position = self.driver.find_element_by_class_name('main-info__title-minor').text
        except Exception as e:
            print(e)
            return None
        return position

    def get_image(self):
        image_url = ""
        try:
            if 'pisos' in self.base_url:
                image = self.driver.find_element_by_class_name('mainphoto-image')
                image_url = image.get_attribute('style')
                image_url = image_url[image_url.find('url(') + 4:]
                image_url = re.sub(r'[\"\;\)]',"",image_url)
            elif 'idealista' in self.base_url:
                image = self.driver.find_element_by_tag_name('img')
                image_url = image.get_attribute('src')
            elif 'habitaclia' in self.base_url:
                image = self.driver.find_elements_by_tag_name('img')[2]
                image_url = image.get_attribute('src')
                #image_url = re.sub(r'[\"\;\)]',"",image_url)
        except Exception as e:
            print(e)
            return None
        return image_url
    
    # Convertimos el texto donde esta el precio en un numero flotante
    def conver_price(self, price):
        p_price = re.findall(r'[0-9]+', price)
        return float(p_price[0] + "." + p_price[1])    
