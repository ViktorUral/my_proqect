import sqlite3
import json
import requests

conn = sqlite3.connect('games.sqlite')
cursor = conn.cursor()

API_KEY = 'BEE6EDBBEAC0D1A63F9A7554CD333085'
app_ids = ['730', '570', '1172470', '252950', '578080', '252490', '413150', '22350', '346110', '374320', '242760',
           '870780', '546560', '238960', '1145360', '435150', '1086940', '264710', '1085660',
           '105600', '218620', '261550', '255710', '246620', '219990', '230410', '268500', '440', '646570',
           '268910', '221910', '236390', '632360', '291550', '2358720', '1118200', '620', '1794680', '400',
           '294100', '550', '2231450', '227300', '1229490', '48700', '250900', '220', '4000', '367520',
           '548430', '1332010', '264710', '588650', '219150', '2379780', '427520', '239030', '207610',
           '1092790', '736260', '457140', '242760', '435150', '322330', '739630', '268910', '636480']

# STEAM_SPY
for APP_ID in app_ids:
    url = f'https://steamspy.com/api.php?request=appdetails&appid={APP_ID}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        json_data_g = json.dumps(list(data['tags'].keys())) if data['appid'] != 1145360 else json.dumps(
            list(data['tags'].keys())[:-1])
        try:
            cursor.execute('''INSERT INTO developers (name) VALUES (?)''',
                           (data['developer'],))
        except Exception:
            pass
        developer = cursor.execute(f"""SELECT id from developers d WHERE '{data['developer']}'=d.name""").fetchall()
        cursor.execute('''INSERT INTO game (id_game, genresdata, positive, negative, developer)
                VALUES (?, ?, ?, ?, ?)''',
                       (data['appid'], json_data_g, data['positive'], data['negative'], developer[0][0]))
conn.commit()

# STEAM
for APP_ID in app_ids:
    url = f'https://store.steampowered.com/api/appdetails?appids={APP_ID}&cc=RU&l=ru'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data[APP_ID]['success']:
            game_info = data[APP_ID]['data']
            try:
                trailer = game_info['movies'][0]['mp4']['480']
            except Exception:
                trailer = None
            cursor.execute('''UPDATE 
            game SET name=?, about=?, image=?, trailer=? WHERE ?=id_game''',
                           (game_info['name'], game_info['short_description'], game_info['header_image'],
                            trailer, game_info['steam_appid']))

    data = response.json()
    if data[APP_ID]['success']:
        game_info = data[APP_ID]['data']
        if 'price_overview' in game_info and game_info['price_overview']['final_formatted'].split()[0] != 'Free':
            price = game_info['price_overview']['final_formatted'].split()[0]
        else:
            price = 0
        if 'metacritic' in game_info:
            metacritic = game_info['metacritic']['score']
        else:
            metacritic = None
        release_date = game_info['release_date']['date']
        cursor.execute('''UPDATE 
        game SET year=?, price=?, mettacritick=? WHERE ?=id_game''',
                       (release_date, price, metacritic, game_info['steam_appid']))

conn.commit()
