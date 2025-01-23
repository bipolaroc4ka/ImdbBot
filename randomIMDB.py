from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from imdb import Cinemagoer
import requests
import time
import re

def get_top_movies():
    # Настроим опции для безголового режима
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Открывает браузер в безголовом режиме
    chrome_options.add_argument("--disable-gpu")  # Отключает использование GPU
    chrome_options.add_argument("--no-sandbox")  # Отключает песочницу

    # Указываем путь к драйверу Chrome
    driver = webdriver.Chrome(options=chrome_options)

    # Открываем страницу IMDb
    driver.get("https://www.imdb.com/chart/top")

    # Даем странице время на подгрузку всех данных
    time.sleep(1)

    # Получаем HTML-код после выполнения JavaScript
    html = driver.page_source

    # Парсим страницу с помощью BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Находим все фильмы
    movieList = soup.findAll('li', class_=re.compile('ipc-metadata-list'))

    movies = []
    for movie in movieList:
        title = movie.find('h3', class_='ipc-title__text')  # Название фильма
        year = movie.find('span', class_='sc-300a8231-7 eaXxft cli-title-metadata-item')  # Год фильма
        rating = movie.find('span', class_='ipc-rating-star--rating')  # Рейтинг фильма
        link = movie.find('a', href=True)  # Ссылка на фильм

        if title and year and rating and link:
            title_text = title.text.strip()
            year_text = year.text.strip()
            rating_text = rating.text.strip()
            movie_link = "https://www.imdb.com" + link['href']
            
            movies.append({
                "title": title_text,
                "year": year_text,
                "rating": rating_text,
                "url": movie_link
            })
    
    driver.quit()
    return movies




def getMoviesfromDirector(name):
    ia = Cinemagoer()
    

    movies = []
    # Ищем персону по имени
    people = ia.search_person(name)
    if not people:
        print(f"No person found with the name: {name}")
        return []

    # Берем первую найденную персону

    
    person = people[0]
    print(f"{person['name']} (ID: {person.personID})")

    #for i in people:
        #if i['name'] == name:
            #print(i.personID)
            #person.append(i.personID)





    # Загружаем полную информацию о персоне
    
    #person_data = ia.get_person_filmography(person.personID)['titlesRefs'].keys()
    #for i in person:
    mID = list(ia.get_person_filmography(person.personID)['titlesRefs'].values())
        
    uniq = set()
    try:
        for m in mID:
             uniq.add(m.movieID)
        

        for i in uniq:
            film = ia.get_movie(f'{i}')
            movie_url = f"https://www.imdb.com/title/tt{i}/"
            movies.append({
                    "title": film['title'],
                    "year": film['year'],                
                    "url": movie_url
                    })
    except Exception as e:
        print(e)

    #print(film['title'], film['year'])
    #print(mID[0].movieID)
    #print(person_data)


    #print(uniqid)   
    #print(person_data)
    #titles_refs = person_data.get('titlesRefs', {})
    #pattern = r'\s\(\d{4}\)'  # Убираем год
    #movies_without_year = [re.sub(pattern, '', movie) for movie in titles_refs.keys()]
    #unique_movies = list(set(movies_without_year))  # Убираем дубли





    #for un in person_data:
        
        #try:
            #film = ia.search_movie(un)[0]
            #filmDeteils = film.movieID
            #movie_url = f"https://www.imdb.com/title/tt{filmDeteils}/"  # Формируем ссылку на фильм
            #movies.append({
                #"title": un,                
                #"url": movie_url
                #})
        #except Exception as e:
            #print(e)
        
    sorted_movies = sorted(movies, key=lambda x: x['year'])  
    for i in sorted_movies:
        print(i)
    return sorted_movies

   


def getMoviesfromDirector2(director_id):

    movies = []
    # Базовый URL IMDb
    base_url = "https://www.imdb.com/name/nm"

    # URL профиля режиссера
    director_url = f"{base_url}{director_id}/"
    print(director_url)
    # Отправляем GET-запрос
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    try:
        # Отправляем GET-запрос с заголовком User-Agent
        response = requests.get(director_url, headers=headers)
        response.raise_for_status()  # Проверяем наличие HTTP ошибок
    except requests.exceptions.RequestException as e:
        print(f"Ошибка: Не удалось получить данные для режиссера с ID {director_id}. Ошибка: {e}")
        return []

    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.text, "html.parser")
    #print(soup)
    # Логика поиска фильмов в блоке с ID "accordion-item-director-previous-projects"
    movie_section = soup.find(id="accordion-item-director-previous-projects")
    if not movie_section:
        print("Ошибка: Не удалось найти секцию с фильмами.")
        return []

    # Находим элементы фильмов в секции
    movies = []
    while True:
        movie_elements = movie_section.find_all("div", class_="ipc-metadata-list-summary-item__tc")

        for movie in movie_elements:
            # Получаем название фильма
            title_element = movie.find("a")
            title = title_element.text.strip() if title_element else "Неизвестно"

            # Получаем год выпуска (если доступен)
            year_element = movie.find("span", class_="ipc-metadata-list-summary-item__li")
            year = year_element.text.strip() if year_element else "Не указан"

            # Добавляем фильм в список
            movies.append({"title": title, "year": year})

        # Проверяем наличие кнопки "Показать ещё" для подгрузки дополнительных фильмов
        load_more_button = movie_section.find("button", class_="ipc-load-more__button")
        if load_more_button:
            # Получаем URL для подгрузки дополнительных данных
            next_page_url = load_more_button.get("data-href")
            if next_page_url:
                next_page_url = f"https://www.imdb.com{next_page_url}"
                try:
                    time.sleep(1)  # Задержка перед следующим запросом
                    response = requests.get(next_page_url, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                    movie_section = soup.find(id="accordion-item-director-previous-projects")
                    continue
                except requests.exceptions.RequestException as e:
                    print(f"Ошибка при загрузке дополнительных фильмов: {e}")
                    break
        break

    return movies   
#getMoviesfromDirector('Wes Anderson')       

















