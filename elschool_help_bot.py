import requests
import asyncio
import sqlite3
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import traceback
import datetime

bot = AsyncTeleBot('token')

connect = sqlite3.connect('name_of_database.db', check_same_thread = False)
cursor = connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users_posting(
	user_id INTEGER,
	login TEXT,
	hash_password TEXT
	)
""")
connect.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS all_users(
	user_id INTEGER,
	login TEXT,
	hash_password TEXT
	)
""")
connect.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS states(
	user_id INTEGER,
	type_of_state TEXT
	)
""")
connect.commit()
@bot.message_handler(commands = ['sendall'])
async def sendall(message):
	if message.from_user.id == ADMIN_ID and len(list(message.text.split('\n'))) > 1:
		t = "\n".join(list(message.text.split('\n'))[1:])
		cursor.execute("SELECT * FROM all_users")
		records = cursor.fetchall()
		gth = types.InlineKeyboardMarkup()
		gth1 = types.InlineKeyboardButton(text = '❎Закрыть', callback_data='delete')
		gth.add(gth1)
		for row in records:
			try:
				await bot.send_message(row[0], t, reply_markup=gth, parse_mode='markdown')
			except:
				await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
@bot.callback_query_handler(lambda call: call.data == 'delete')
async def delete(call):
	await bot.delete_message(call.from_user.id, call.message.message_id)
@bot.message_handler(commands = ['start'])
async def start(message):
	menu = types.InlineKeyboardMarkup()
	menu1 = types.InlineKeyboardButton(text = '👤Личный кабинет', callback_data = 'profile')
	menu11 = types.InlineKeyboardButton(text = '📊Статистика', callback_data = 'stat1')
	menu2 = types.InlineKeyboardButton(text = '🛠Техподдержка', callback_data = 'help')
	menu3 = types.InlineKeyboardButton(text = '👨‍💻Исходный код', url = 'https://github.com/theslothbear/Elschool-Help-Bot')
	#menu4 = types.InlineKeyboardButton(text = '⚙Настройки', callback_data = 'nastr')
	menu.add(menu1)
	menu.add(menu11)
	#menu.add(menu4)
	menu.add(menu2, menu3)
	if message.from_user.id == ADMIN_ID:
		await bot.send_message(ADMIN_ID, '🏠*Главное меню Elschool Help Bot (v.1.0.1)*\n\nЧтобы запустить парсинг оценок - /parsemarksstart\nОтправить сообщение всем юзерам - /sendall + |n + markdown', parse_mode = 'markdown', reply_markup = menu)
	else:
		await bot.send_message(message.from_user.id, '🏠*Главное меню Elschool Help Bot (v.1.0.1)*', parse_mode = 'markdown', reply_markup = menu)

@bot.message_handler(commands = ['parsemarksstart'])
async def parse_marks(message):
	if message.from_user.id == ADMIN_ID:
		while True:
			try:
				cursor.execute("SELECT * FROM users_posting")
				recordsrt = cursor.fetchall()
				for rowrt in recordsrt:
					cursor.execute(f"""CREATE TABLE IF NOT EXISTS t{rowrt[0]}(
						predmet TEXT,
						m5_marks TEXT,
						m4_marks TEXT,
						m3_marks TEXT,
						m2_marks TEXT,
						m1_marks TEXT,
						str_marks TEXT
						)
						""")
					connect.commit()
					session = requests.Session()
					url = 'https://elschool.ru/Logon/Index'
					user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
					r = session.get(url, headers = {
					    'User-Agent': user_agent_val
					}, verify = False)
					session.headers.update({'Referer':url})
					session.headers.update({'User-Agent':user_agent_val})
					_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
					post_request = session.post(url, {
					     'login': f'{rowrt[1]}',
					     'password': f'{rowrt[2]}',
					     '_xsrf':_xsrf,
					})
					r1 = session.get('https://elschool.ru/users/diaries', headers = {
					    'User-Agent': user_agent_val
					}, verify = False)
					session.headers.update({'Referer':url})
					session.headers.update({'User-Agent':user_agent_val})
					_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
					s = r1.text.split('class="btn">Табель</a>')[0].split(r'href="')[-1].split(r'"')[0]
					#print(f'https://elschool.ru/users/diaries/{s}')
					r2 = session.get(f'https://elschool.ru/users/diaries/{s}', headers = {
					    'User-Agent': user_agent_val
					}, verify = False)
					session.headers.update({'Referer':url})
					session.headers.update({'User-Agent':user_agent_val})
					_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")

					spg, fl, col4 = [], True, -1
					for i in range(1, 100):
						str_marks = ''
						s1 = list(r2.text.split(f'<tbody period="{i}"'))
						if len(s1) > 1:
							pr = s1[0].split(r'<th colspan="')[-1].split('>')[1].split('<')[0]
							spo = []
							l1 = list(s1[1].split(r'<td class="grades-period-name">1')[1].split('<span>'))
							if s1[1].split(r'<td class="grades-period-name">1')[1][1:4] == 'чет':
								col4 = s1[1].split(r'<td class="grades-period-name">4')[1].split('<td class="grades-period-name">1')[0].count('<span>')
								col3 = s1[1].split(r'<td class="grades-period-name">3')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col4
								col2 = s1[1].split(r'<td class="grades-period-name">2')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col3 - col4
								col1 = s1[1].split(r'<td class="grades-period-name">1')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col2 - col3 - col4
					        	#print(f'{pr}: 1 четверть - {col1}, 2 четверть - {col2}, 3 четверть - {col3}, 4 четверть - {col4}')
							elif s1[1].split(r'<td class="grades-period-name">1')[1][1:4] == 'три':
								col3 = s1[1].split(r'<td class="grades-period-name">3')[1].split('<td class="grades-period-name">1')[0].count('<span>')
								col2 = s1[1].split(r'<td class="grades-period-name">2')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col3
								col1 = s1[1].split(r'<td class="grades-period-name">1')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col2 - col3
							for r in l1[1:]:
								yu = r.split('</span>')[0]
								spo.append(yu)
								str_marks += f'{yu} '
							if col4 != -1:
								spg.append({'Предмет': f'{pr}', 'Оценки': f'{" ".join(spo)}', 'Colvo': f'{col1} {col2} {col3} {col4}', 'str': str_marks[0:len(str_marks)-1]})
							else:
								spg.append({'Предмет': f'{pr}', 'Оценки': f'{" ".join(spo)}', 'Colvo': f'{col1} {col2} {col3}', 'str': str_marks[0:len(str_marks)-1]})

						else:
							break
					if spg == []:
						tyi = types.InlineKeyboardMarkup()
						pr1 = types.InlineKeyboardButton(text = '✏Изменить аккаунт ELSCHOOL', callback_data='podkl')
						zx2 = types.InlineKeyboardButton(text = '🔙В меню', callback_data = 'menu')
						tyi.add(pr1)
						tyi.add(zx2)
						cursor.execute("DELETE FROM users_posting WHERE user_id=?", (rowrt[0],))
						connect.commit()
						await bot.send_message(rowrt[0], '❌*Ошибка!* \nПохоже, логин либо пароль введены неправильно😿\n\n*Уведомления отключены*', reply_markup=tyi, parse_mode='markdown')
					else:
						cursor.execute(f"SELECT * FROM t{rowrt[0]}")
						records = cursor.fetchall()
						cursor.execute(f"DELETE FROM t{rowrt[0]}")
						connect.commit()
						if col4 != -1:
							for s in spg:
								m1m_1, m2m_1, m3m_1, m4m_1, m5m_1, n = 0, 0, 0, 0, 0, 1
								m1m_2, m2m_2, m3m_2, m4m_2, m5m_2 = 0, 0, 0, 0, 0
								m1m_3, m2m_3, m3m_3, m4m_3, m5m_3 = 0, 0, 0, 0, 0
								m1m_4, m2m_4, m3m_4, m4m_4, m5m_4 = 0, 0, 0, 0, 0
								c1, c2, c3, c4 = map(int, s['Colvo'].split())
								for mark in list(s['Оценки'].split()):
									if int(mark) == 5:
										if n <= c1:
											m5m_1 +=1
										elif n <= c1 + c2:
											m5m_2 += 1
										elif n <= c1 + c2 + c3:
											m5m_3 += 1
										else:
											m5m_4 += 1
										n+=1
									elif int(mark) == 4:
										if n <= c1:
											m4m_1 +=1
										elif n <= c1 + c2:
											m4m_2 += 1
										elif n <= c1 + c2 + c3:
											m4m_3 += 1
										else:
											m4m_4 += 1
										n+=1
									elif int(mark) == 3:
										if n <= c1:
											m3m_1 +=1
										elif n <= c1 + c2:
											m3m_2 += 1
										elif n <= c1 + c2 + c3:
											m3m_3 += 1
										else:
											m3m_4 += 1
										n+=1
									elif int(mark) == 2:
										if n <= c1:
											m2m_1 +=1
										elif n <= c1 + c2:
											m2m_2 += 1
										elif n <= c1 + c2 + c3:
											m2m_3 += 1
										else:
											m2m_4 += 1
										n+=1
									elif int(mark) == 1:
										if n <= c1:
											m1m_1 +=1
										elif n <= c1 + c2:
											m1m_2 += 1
										elif n <= c1 + c2 + c3:
											m1m_3 += 1
										else:
											m1m_4 += 1
										n+=1
								for row in records:
									if row[0] == s['Предмет']:
										m5f, m4f, m3f, m2f, m1f = sum(map(int,row[1].split())), sum(map(int,row[2].split())), sum(map(int,row[3].split())), sum(map(int,row[4].split())), sum(map(int,row[5].split())) #старые
										ws = types.InlineKeyboardMarkup()
										ws1 = types.InlineKeyboardButton(text = '👀Посмотреть', url = 'https://elschool.ru/')
										p = 'Предмет'
										if len(s[p]) > 32:
											prr = s[p][0:30] + '...'
										else:
											prr = s[p]
										ws.add(types.InlineKeyboardButton(text = f'📊Статистика по предмету', callback_data = f'P{prr}'))
										#ws2 = types.InlineKeyboardMarkup(text = 'Посмотреть статистику по предмету', callback_data='qwertyuiop')
										ws.add(ws1)
										if m5m_1 + m5m_2 + m5m_3 +m5m_4 >= m5f:
											for i in range(m5m_1 + m5m_2 + m5m_3 +m5m_4 - m5f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'🟢<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 5 🟢'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m5m_1 - m5m_2 - m5m_3 - m5m_4 + m5f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 5</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										if m4m_1 + m4m_2 + m4m_3 +m4m_4 >= m4f:
											for i in range(m4m_1 + m4m_2 + m4m_3 +m4m_4 - m4f):
												p, d = 'Предмет', str(datetime.datetime.now())
												try:
													await bot.send_message(rowrt[0], (fr'🔵<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 4 🔵'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m4m_1 - m4m_2 - m4m_3 - m4m_4 + m4f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 4</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										if m3m_1 + m3m_2 + m3m_3 +m3m_4 >= m3f:
											for i in range(m3m_1 + m3m_2 + m3m_3 +m3m_4 - m3f):
												p, d = 'Предмет', str(datetime.datetime.now())
												try:
													await bot.send_message(rowrt[0], (fr'🟠<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 3 🟠'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m3m_1 - m3m_2 - m3m_3 - m3m_4 + m3f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 3</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										if m2m_1 + m2m_2 + m2m_3 +m2m_4 >= m2f:
											for i in range(m2m_1 + m2m_2 + m2m_3 +m2m_4 - m2f):
												p, d = 'Предмет', str(datetime.datetime.now())
												try:
													await bot.send_message(rowrt[0], (fr'🔴<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 2 🔴'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m2m_1 - m2m_2 - m2m_3 - m2m_4 + m2f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 2</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										if m1m_1 + m1m_2 + m1m_3 + m1m_4 >= m1f:
											for i in range(m1m_1 + m1m_2 + m1m_3 + m1m_4 - m1f):
												p, d = 'Предмет', str(datetime.datetime.now())
												try:
													await bot.send_message(rowrt[0], (fr'🔴<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 1 🔴'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')							
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m1m_1 - m1m_2 - m1m_3 - m1m_4 + m1f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 1</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
								ser = [s['Предмет'], f'{m5m_1} {m5m_2} {m5m_3} {m5m_4}', f'{m4m_1} {m4m_2} {m4m_3} {m4m_4}', f'{m3m_1} {m3m_2} {m3m_3} {m3m_4}', f'{m2m_1} {m2m_2} {m2m_3} {m2m_4}', f'{m1m_1} {m1m_2} {m1m_3} {m1m_4}', s['str']]
								cursor.execute(f"INSERT INTO t{rowrt[0]} VALUES(?,?,?,?,?,?,?);", ser)
								connect.commit()
						else:
							for s in spg:
								m1m_1, m2m_1, m3m_1, m4m_1, m5m_1, n = 0, 0, 0, 0, 0, 1
								m1m_2, m2m_2, m3m_2, m4m_2, m5m_2 = 0, 0, 0, 0, 0
								m1m_3, m2m_3, m3m_3, m4m_3, m5m_3 = 0, 0, 0, 0, 0
								c1, c2, c3 = map(int, s['Colvo'].split())
								for mark in list(s['Оценки'].split()):
									if int(mark) == 5:
										if n <= c1:
											m5m_1 +=1
										elif n <= c1 + c2:
											m5m_2 += 1
										else:
											m5m_3 += 1
										n+=1
									elif int(mark) == 4:
										if n <= c1:
											m4m_1 +=1
										elif n <= c1 + c2:
											m4m_2 += 1
										else:
											m4m_3 += 1
										n+=1
									elif int(mark) == 3:
										if n <= c1:
											m3m_1 +=1
										elif n <= c1 + c2:
											m3m_2 += 1
										else:
											m3m_3 += 1
										n+=1
									elif int(mark) == 2:
										if n <= c1:
											m2m_1 +=1
										elif n <= c1 + c2:
											m2m_2 += 1
										else:
											m2m_3 += 1
										n+=1
									elif int(mark) == 1:
										if n <= c1:
											m1m_1 +=1
										elif n <= c1 + c2:
											m1m_2 += 1
										else:
											m1m_3 += 1
										n+=1
								for row in records:
									if row[0] == s['Предмет']:
										m5f, m4f, m3f, m2f, m1f = sum(map(int,row[1].split())), sum(map(int,row[2].split())), sum(map(int,row[3].split())), sum(map(int,row[4].split())), sum(map(int,row[5].split())) #старые
										ws = types.InlineKeyboardMarkup()
										ws1 = types.InlineKeyboardButton(text = '👀Посмотреть', url = 'https://elschool.ru/')
										p = 'Предмет'
										if len(s[p]) > 32:
											prr = s[p][0:30] + '...'
										else:
											prr = s[p]
										ws.add(types.InlineKeyboardButton(text = f'📊Статистика по предмету', callback_data = f'P{prr}'))
										#ws2 = types.InlineKeyboardMarkup(text = 'Посмотреть статистику по предмету', callback_data='qwertyuiop')
										ws.add(ws1)
										if m5m_1 + m5m_2 + m5m_3 >= m5f:
											for i in range(m5m_1 + m5m_2 + m5m_3 - m5f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'🟢<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 5 🟢'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m5m_1 - m5m_2 - m5m_3 + m5f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 5</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										if m4m_1 + m4m_2 + m4m_3 >= m4f:
											for i in range(m4m_1 + m4m_2 + m4m_3 - m4f):
												p, d = 'Предмет', str(datetime.datetime.now())
												try:
													await bot.send_message(rowrt[0], (fr'🔵<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 4 🔵'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m4m_1 - m4m_2 - m4m_3 + m4f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 4</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										if m3m_1 + m3m_2 + m3m_3 >= m3f:
											for i in range(m3m_1 + m3m_2 + m3m_3 - m3f):
												p, d = 'Предмет', str(datetime.datetime.now())
												try:
													await bot.send_message(rowrt[0], (fr'🟠<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 3 🟠'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m3m_1 - m3m_2 - m3m_3 + m3f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 3</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										if m2m_1 + m2m_2 + m2m_3 >= m2f:
											for i in range(m2m_1 + m2m_2 + m2m_3 - m2f):
												p, d = 'Предмет', str(datetime.datetime.now())
												try:
													await bot.send_message(rowrt[0], (fr'🔴<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 2 🔴'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m2m_1 - m2m_2 - m2m_3 + m2f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 2</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										if m1m_1 + m1m_2 + m1m_3 >= m1f:
											for i in range(m1m_1 + m1m_2 + m1m_3 - m1f):
												p, d = 'Предмет', str(datetime.datetime.now())
												try:
													await bot.send_message(rowrt[0], (fr'🔴<b>Новая оценка</b> по предмету <b>"{s[p]}"</b>: 1 🔴'
														f'\n\n'
														fr'Дата выставления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')							
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
										else:
											for i in range(0 - m1m_1 - m1m_2 - m1m_3 + m1f):
												p, d = 'Предмет', str(datetime.datetime.now())
												await bot.send_message(ADMIN_CHANNEL, f'—{s[p]}')
												try:	
													await bot.send_message(rowrt[0], (fr'❎<b>Ваша оценка 1</b> по предмету <b>"{s[p]}"</b> была удалена❎.'
														f'\n\n'
														fr'Дата удаления: <b>{d[0:len(d)-7]} МСК.</b>'), reply_markup=ws, parse_mode='HTML')
												except:
													await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
								ser = [s['Предмет'], f'{m5m_1} {m5m_2} {m5m_3}', f'{m4m_1} {m4m_2} {m4m_3}', f'{m3m_1} {m3m_2} {m3m_3}', f'{m2m_1} {m2m_2} {m2m_3}', f'{m1m_1} {m1m_2} {m1m_3}', s['str']]
								cursor.execute(f"INSERT INTO t{rowrt[0]} VALUES(?,?,?,?,?,?,?);", ser)
								connect.commit()
					await asyncio.sleep(1.0)
				await bot.send_message(ADMIN_CHANNEL, 'Парсинг оценок выполнен')
				await asyncio.sleep(300.0)
			except:
				await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
	else:
		await bot.delete_message(message.from_user.id, message.message_id)
@bot.callback_query_handler(lambda call: call.data == 'profile')
async def profile(call):
	cursor.execute("SELECT * FROM all_users")
	records, r = cursor.fetchall(), ['0', 'Не задано', 'Не задано']
	for row in records:
		if row[0] == call.from_user.id:
			r = row
			break
	if r != ['0', 'Не задано', 'Не задано']:
		pr = types.InlineKeyboardMarkup()
		pr1 = types.InlineKeyboardButton(text = '✏Изменить аккаунт ELSCHOOL', callback_data='podkl')
		pr2 = types.InlineKeyboardButton(text = '🔙Назад', callback_data = 'menu')
		pr.add(pr1)
		pr.add(pr2)
		await bot.send_message(call.from_user.id, f'<b>👤Профиль {call.from_user.first_name} {call.from_user.last_name}</b>\n\n🔹Логин Elschool: {r[1]}\n\n🔹Пароль: <span class="tg-spoiler">{r[2]}</span>', parse_mode='HTML', reply_markup = pr)
	else:
		pr = types.InlineKeyboardMarkup()
		pr1 = types.InlineKeyboardButton(text = '➕Подключить аккаунт ELSCHOOL', callback_data='podkl')
		pr2 = types.InlineKeyboardButton(text = '🔙Назад', callback_data = 'menu')
		pr.add(pr1)
		pr.add(pr2)
		await bot.send_message(call.from_user.id, f'*👤Профиль {call.from_user.first_name} {call.from_user.last_name}*\n\n🔹Логин Elschool: _Не привязан_', parse_mode='MarkdownV2', reply_markup=pr)

@bot.callback_query_handler(lambda call: call.data == 'podkl')
async def podkl(call):
	ty = types.InlineKeyboardMarkup()
	ty0 = types.InlineKeyboardButton(text = '📗Пользовательское соглашение', url = 'https://telegra.ph/Polzovatelskoe-soglashenie-Elschool-Help-Bot-03-18')
	ty1 = types.InlineKeyboardButton(text = '➡Продолжить', callback_data = 'podklok')
	ty2 = types.InlineKeyboardButton(text = '🔙Назад', callback_data = 'menu')
	ty.add(ty0)
	ty.add(ty1)
	ty.add(ty2)
	await bot.send_message(call.from_user.id, f'🌐Соединение с аккаунтом *ELSCHOOL*\n\n❗Нажимая кнопку "Продолжить", Вы *подтверждаете*, что ознакомились с пользовательским соглашением и *согласны* с ним.', reply_markup=ty, parse_mode='markdown')

@bot.callback_query_handler(lambda call: call.data == 'podklok')
async def podklok(call):
	cursor.execute("DELETE FROM states WHERE user_id=?", (call.from_user.id,))
	connect.commit()
	sdf = [call.from_user.id, 'login-and-password']
	cursor.execute("INSERT INTO states VALUES(?,?);", sdf)
	connect.commit()
	await bot.send_message(call.from_user.id, '🌐Соединение с аккаунтом *ELSCHOOL*\n\nВведите Ваши логин и пароль от электронного журнала Elschool, каждое в новой строке\n\n_Пример:_\n_Иванов Иван_\n_надёжный-пароль12345_\n\n*Важно:* это должен быть аккаунт *ученика!*', parse_mode='markdown')

@bot.message_handler(content_types = ['text'])
async def get(message):
	cursor.execute("SELECT * FROM states")
	records = cursor.fetchall()
	r = []
	for row in records:
		if row[0] == message.from_user.id:
			r = row
			break
	if r:
		if r[1] == 'login-and-password':
			sp = list(message.text.split('\n'))
			if len(sp) == 2 and not '<' in sp[0] and not '>' in sp[0] and not '<' in sp[1] and not '>' in sp[1] and not '&' in sp[1] and not '&' in sp[0]:
				qw = [message.from_user.id, sp[0], sp[1]]
				cursor.execute("DELETE FROM all_users WHERE user_id=?", (message.from_user.id,))
				connect.commit()
				cursor.execute("DELETE FROM users_posting WHERE user_id=?", (message.from_user.id,))
				connect.commit()
				cursor.execute("INSERT INTO all_users VALUES(?,?,?);", qw)
				connect.commit()
				cursor.execute("INSERT INTO users_posting VALUES(?,?,?);", qw)
				connect.commit()
				cursor.execute("DELETE FROM states WHERE user_id=?", (message.from_user.id,))
				connect.commit()
				zx = types.InlineKeyboardMarkup()
				#zx1 = types.InlineKeyboardButton(text = 'Перейти к ⚙настройкам', callback_data = 'nastr')
				zx2 = types.InlineKeyboardButton(text = '🔙В меню', callback_data = 'menu')
				#zx.add(zx1)
				zx.add(zx2)
				await bot.send_message(message.from_user.id, '✅Аккаунт Elschool успешно привязан', reply_markup = zx)
			else:
				await bot.reply_to(message, 'Некорректный ввод. Попробуйте ещё раз. По образцу.\n\n_Иванов Иван_\n_надёжный-пароль12345_', parse_mode='markdown')
	else:
		await bot.delete_message(message.from_user.id, message.message_id)

@bot.callback_query_handler(lambda call: call.data == 'menu')
async def menu(call):
	menu = types.InlineKeyboardMarkup()
	menu1 = types.InlineKeyboardButton(text = '👤Личный кабинет', callback_data = 'profile')
	menu11 = types.InlineKeyboardButton(text = '📊Статистика', callback_data = 'stat1')
	menu2 = types.InlineKeyboardButton(text = '🛠Техподдержка', callback_data = 'help')
	menu3 = types.InlineKeyboardButton(text = '👨‍💻Исходный код', url = 'https://github.com/theslothbear/Elschool-Help-Bot')
	#menu4 = types.InlineKeyboardButton(text = '⚙Настройки', callback_data = 'nastr')
	menu.add(menu1)
	menu.add(menu11)
	#menu.add(menu4)
	menu.add(menu2, menu3)
	if call.from_user.id == ADMIN_ID:
		await bot.send_message(ADMIN_ID, '🏠*Главное меню Elschool Help Bot (v.1.0.1)*\n\nЧтобы запустить парсинг оценок - /parsemarksstart', parse_mode = 'markdown', reply_markup = menu)
	else:
		await bot.send_message(call.from_user.id, '🏠*Главное меню Elschool Help Bot (v.1.0.1)*', parse_mode = 'markdown', reply_markup = menu)

@bot.callback_query_handler(lambda call: call.data[0:4] == 'stat')
async def stat(call):
		if call.data[4:] == '':
			n = 1
		else:
			n = int(call.data[4:])
		mst1 = types.InlineKeyboardButton(text = '👪Поделиться', switch_inline_query = 'potom sdelau')
		zx2 = types.InlineKeyboardButton(text = '🔙В меню', callback_data = 'menu')
		try:
			cursor.execute(f"SELECT * FROM t{call.from_user.id}")
			records = cursor.fetchall()
			amount_all_marks, sum_all_marks, sp_maxball, sp_minball = 0, 0, [[-1, '']], [[6, '']]
			predm = types.InlineKeyboardMarkup()
			#predm.add(mst1)
			h = 0
			for row in records:
				h+=1
				if h in range(6*(n-1) + 1, 6*n + 1):
					if len(row[0]) > 32:
						prr = row[0][0:30] + '...'
					else:
						prr = row[0]
					predm.add(types.InlineKeyboardButton(text = f'🔹{row[0]}', callback_data = f'P{prr}'))
				amount_all_marks += sum(map(int,row[1].split())) * 5
				sum_all_marks += sum(map(int,row[1].split()))
				amount_all_marks += sum(map(int,row[2].split())) * 4
				sum_all_marks += sum(map(int,row[2].split()))
				amount_all_marks += sum(map(int,row[3].split())) * 3
				sum_all_marks += sum(map(int,row[3].split()))
				amount_all_marks += sum(map(int,row[4].split())) * 2
				sum_all_marks += sum(map(int,row[4].split()))
				amount_all_marks += sum(map(int,row[5].split())) * 1
				sum_all_marks += sum(map(int,row[5].split()))

				amount_all_marks12 = sum(map(int,row[1].split())) * 5
				sum_all_marks12 = sum(map(int,row[1].split()))
				amount_all_marks12 += sum(map(int,row[2].split())) * 4
				sum_all_marks12 += sum(map(int,row[2].split()))
				amount_all_marks12 += sum(map(int,row[3].split())) * 3
				sum_all_marks12 += sum(map(int,row[3].split()))
				amount_all_marks12 += sum(map(int,row[4].split())) * 2
				sum_all_marks12 += sum(map(int,row[4].split()))
				amount_all_marks12 += sum(map(int,row[5].split())) * 1
				sum_all_marks12 += sum(map(int,row[5].split()))
				if sum_all_marks12 == 0:
					sum_all_marks12 += 1
				sr_ball = amount_all_marks12 / sum_all_marks12
				if sr_ball > sp_maxball[0][0] and sr_ball != 0:
					sp_maxball = [[sr_ball, row[0]]]
				elif sr_ball == sp_maxball[0][0]:
					sp_maxball.append([sr_ball, row[0]])

				if sr_ball < sp_minball[0][0] and sr_ball != 0:
					sp_minball = [[sr_ball, row[0]]]

				elif sr_ball == sp_minball[0][0]:
					sp_minball.append([sr_ball, row[0]])

			if sum_all_marks == 0:
				sum_all_marks += 1

			strmaxpr, strminpr = '', ''
			for r in sp_maxball:
				strmaxpr += (f'*"{r[1]}"*, ')
			for r in sp_minball:
				strminpr += (f'*"{r[1]}"*, ')
			t = len(records)
			r = 0
			if t % 6 != 0:
				r=1
			if n != int(t/6) + r and n!=1:
				predm.add(types.InlineKeyboardButton(text = '⏪', callback_data=f'stat{n-1}'), types.InlineKeyboardButton(text = '⏩', callback_data=f'stat{n+1}'))
			elif n != 1:
				predm.add(types.InlineKeyboardButton(text = '⏪', callback_data=f'stat{n-1}'))
			elif n != int(t/6) + r:
				predm.add(types.InlineKeyboardButton(text = '⏩', callback_data=f'stat{n+1}'))
			predm.add(zx2)
			if strmaxpr != '' and strminpr != '' :
				await bot.send_message(call.from_user.id, f'*📊Годовая статистика оценок {call.from_user.first_name} {call.from_user.last_name}*\n\n🔹*Общий* средний балл по *всем* предметам: {round(amount_all_marks/sum_all_marks, 2)}\n\n🔺Наибольший средний балл за год — {round(sp_maxball[0][0], 2)} по предметам {strmaxpr[0:len(strmaxpr)-2]}.\n\n🔻Наименьший средний балл за год — {round(sp_minball[0][0], 2)} по предметам {strminpr[0:len(strminpr)-2]}.\n\n_Для просмотра статистики по отдельному предмету используйте кнопки ниже:_', parse_mode='markdown', reply_markup=predm)
			else:
				await bot.send_message(call.from_user.id, f'*📊Годовая статистика оценок {call.from_user.first_name} {call.from_user.last_name}*\n\n🔹*Общий* средний балл по *всем* предметам: {round(amount_all_marks/sum_all_marks, 2)}\n\n🔺Наибольший средний балл за год — _недостаточно данных_.\n\n🔻Наименьший средний балл за год — _недостаточно данных_.\n\n_Для просмотра статистики по отдельному предмету используйте кнопки ниже:_', parse_mode='markdown', reply_markup=predm)
			try:
				await bot.delete_message(call.from_user.id, call.message.message_id)
			except:
				pass
		except:
			pr = types.InlineKeyboardMarkup()
			pr1 = types.InlineKeyboardButton(text = '➕Подключить аккаунт ELSCHOOL', callback_data='podkl')
			pr2 = types.InlineKeyboardButton(text = '🔙Назад', callback_data = 'menu')
			pr.add(pr1)
			pr.add(pr2)
			await bot.send_message(call.from_user.id, '🌐Привяжите аккаунт ELSCHOOL к аккаунту, чтобы получить доступ к разделу 📊Статистика', reply_markup=pr)
@bot.callback_query_handler(lambda call: call.data[0] == 'P')
async def predmet(call):
	predmet = call.data[1:]
	cursor.execute(f"SELECT * FROM t{call.from_user.id}")
	records = cursor.fetchall()
	amount_all_marks, sum_all_marks = 0, 0 
	for row in records:
		if row[0][0:len(predmet)-3] == predmet[0:len(predmet)-3]:
			summ = 0 
			am_marks = 0 
			sp_gr = []
			for mark in list(map(int, row[6].split())):
				summ+=mark
				am_marks+=1
				sp_gr.append(round(summ/am_marks, 2))
			import matplotlib.pyplot as plt
			plt.clf()
			plt.title('Изменение среднего балла за год')
			plt.plot(sp_gr)
			plt.savefig(f'{call.from_user.id}.png')
			amount_all_marks += sum(map(int,row[1].split())) * 5
			sum_all_marks += sum(map(int,row[1].split()))
			amount_all_marks += sum(map(int,row[2].split())) * 4
			sum_all_marks += sum(map(int,row[2].split()))
			amount_all_marks += sum(map(int,row[3].split())) * 3
			sum_all_marks += sum(map(int,row[3].split()))
			amount_all_marks += sum(map(int,row[4].split())) * 2
			sum_all_marks += sum(map(int,row[4].split()))
			amount_all_marks += sum(map(int,row[5].split())) * 1
			sum_all_marks += sum(map(int,row[5].split()))
			if sum_all_marks == 0:
				sum_all_marks = 1
			sr_ball = amount_all_marks / sum_all_marks
			best, bad = 'нет данных', 'нет данных'
			if sum(map(int, row[5].split())) > 0:
				bad = 1
				best = 1
			if sum(map(int, row[4].split())) > 0:
				if bad == 'нет данных':
					bad = 2
				best = 2
			if sum(map(int, row[3].split())) > 0:
				if bad == 'нет данных':
					bad = 3
				best = 3
			if sum(map(int, row[2].split())) > 0:
				if bad == 'нет данных':
					bad = 4
				best = 4
			if sum(map(int, row[1].split())) > 0:
				if bad == 'нет данных':
					bad = 5
				best = 5
			pil = types.InlineKeyboardMarkup()
			if len(row[1].split()) == 4:
				pil.add(types.InlineKeyboardButton(text = '🔸1 четверть', callback_data = f'Q1{row[0][0:30]}'), types.InlineKeyboardButton(text = '🔸2 четверть', callback_data = f'Q2{row[0][0:30]}'))
				pil.add(types.InlineKeyboardButton(text = '🔸3 четверть', callback_data = f'Q3{row[0][0:30]}'), types.InlineKeyboardButton(text = '🔸4 четверть', callback_data = f'Q4{row[0][0:30]}'))
			else:
				pil.add(types.InlineKeyboardButton(text = '🔸1 триместр', callback_data = f'Q1{row[0][0:30]}'))
				pil.add(types.InlineKeyboardButton(text = '🔸2 триместр', callback_data = f'Q2{row[0][0:30]}'))
				pil.add(types.InlineKeyboardButton(text = '🔸3 триместр', callback_data = f'Q3{row[0][0:30]}'))
			#pil1 = types.InlineKeyboardButton(text = '👪Поделиться', switch_inline_query = '')
			piln = types.InlineKeyboardButton(text = '🔙Назад', callback_data = 'stat1')
			#pil.add(pil1)
			pil.add(piln)
			await bot.send_photo(call.from_user.id, photo = open(f'{call.from_user.id}.png', 'rb') , caption = f'*📊Годовая статистика оценок {call.from_user.first_name} {call.from_user.last_name}* по предмету "*{row[0]}*"\n\n🔹*Общий* средний балл *за год* — {round(sr_ball, 2)}\n\n*🔝Лучшая* оценка — *{best}*,\n*🔻Худшая* оценка — *{bad}*\n\n*Всего оценок — {len(sp_gr)}, из них:*\n🟢5 — {sum(map(int, row[1].split()))},\n🔵4 — {sum(map(int, row[2].split()))},\n🟠3 — {sum(map(int, row[3].split()))},\n🔴2 — {sum(map(int, row[4].split()))},\n🔴1 — {sum(map(int, row[5].split()))} \n\n_Используйте кнопки ниже для просмотра статистики по отдельным четвертям / триместрам._', parse_mode='markdown', reply_markup=pil)
			break
		#else:
			#print(row[0][0:len(predmet)], predmet)

@bot.callback_query_handler(lambda call: call.data[0] == 'Q')
async def chetv(call):
	#await bot.send_message(call.from_user.id, 'В разработке (доступно только администраторам)')
	#return
	try:
		number = int(call.data[1])
		predm = call.data[2:]
		cursor.execute(f"SELECT * FROM t{call.from_user.id}")
		records = cursor.fetchall()
		for row in records:
			if row[0][0:len(predm)] == predm:
				if number == 1:
					s, sne= 0, 0
					s += int(list(row[1].split())[0])
					s += int(list(row[2].split())[0])
					s += int(list(row[3].split())[0])
					s += int(list(row[4].split())[0])
					s += int(list(row[5].split())[0])
				elif number == 2:
					s, sne = 0, 0
					sne += int(list(row[1].split())[0])
					sne += int(list(row[2].split())[0])
					sne += int(list(row[3].split())[0])
					sne += int(list(row[4].split())[0])
					sne += int(list(row[5].split())[0])
					s += int(list(row[1].split())[1])
					s += int(list(row[2].split())[1])
					s += int(list(row[3].split())[1])
					s += int(list(row[4].split())[1])
					s += int(list(row[5].split())[1])
				elif number == 3:
					s, sne = 0, 0
					sne += int(list(row[1].split())[0])
					sne += int(list(row[2].split())[0])
					sne += int(list(row[3].split())[0])
					sne += int(list(row[4].split())[0])
					sne += int(list(row[5].split())[0])
					sne += int(list(row[1].split())[1])
					sne += int(list(row[2].split())[1])
					sne += int(list(row[3].split())[1])
					sne += int(list(row[4].split())[1])
					sne += int(list(row[5].split())[1])
					s += int(list(row[1].split())[2])
					s += int(list(row[2].split())[2])
					s += int(list(row[3].split())[2])
					s += int(list(row[4].split())[2])
					s += int(list(row[5].split())[2])
				else:
					s, sne = 0, 0
					sne += int(list(row[1].split())[0])
					sne += int(list(row[2].split())[0])
					sne += int(list(row[3].split())[0])
					sne += int(list(row[4].split())[0])
					sne += int(list(row[5].split())[0])
					sne += int(list(row[1].split())[1])
					sne += int(list(row[2].split())[1])
					sne += int(list(row[3].split())[1])
					sne += int(list(row[4].split())[1])
					sne += int(list(row[5].split())[1])
					sne += int(list(row[1].split())[2])
					sne += int(list(row[2].split())[2])
					sne += int(list(row[3].split())[2])
					sne += int(list(row[4].split())[2])
					sne += int(list(row[5].split())[2])
					s += int(list(row[1].split())[3])
					s += int(list(row[2].split())[3])
					s += int(list(row[3].split())[3])
					s += int(list(row[4].split())[3])
					s += int(list(row[5].split())[3])			

				summ, am_marks, sp_gr = 0, 0, []
				if s != 0:
					sp = list(row[6].split())[sne:sne+s]
				else:
					sp = []
				for mark in sp:
					summ+=int(mark)
					am_marks+=1
					sp_gr.append(round(summ/am_marks, 2))
				import matplotlib.pyplot as plt
				plt.clf()
				plt.title(f'Изменение среднего балла за {number} четверть/триместр')
				plt.plot(sp_gr)
				plt.savefig(f'{call.from_user.id}.png')
				pil = types.InlineKeyboardMarkup()
				piln = types.InlineKeyboardButton(text = '🔙Назад', callback_data = 'stat1')
				pil.add(piln)
				f = 0
				if sp_gr == []:
					sp_gr = [0.0]
					f = 1
					best, bad = 'нет данных', 'нет данных'
				else:
					best, bad = max(sp),  min(sp)
				await bot.send_photo(call.from_user.id, photo = open(f'{call.from_user.id}.png', 'rb') , caption = f'*📊Cтатистика оценок {call.from_user.first_name} {call.from_user.last_name}* по предмету "*{row[0]}*" за *{number} четверть*.\n\n🔹Средний балл  — {sp_gr[-1]}\n\n*🔝Лучшая* оценка — *{best}*,\n*🔻Худшая* оценка — *{bad}*\n\n*Всего оценок — {len(sp_gr)-f}, из них:*\n🟢5 — {int(list(row[1].split())[number-1])},\n🔵4 — {int(list(row[2].split())[number-1])},\n🟠3 — {int(list(row[3].split())[number-1])},\n🔴2 — {int(list(row[4].split())[number-1])},\n🔴1 — {int(list(row[5].split())[number-1])}', parse_mode='markdown', reply_markup=pil)
				break
	except:
		await bot.send_message(ADMIN_CHANNEL, f'{traceback.format_exc()}')
@bot.callback_query_handler(lambda call: call.data == 'help')
async def help(call):
	qws = types.InlineKeyboardMarkup()
	piln = types.InlineKeyboardButton(text = '🔙Назад', callback_data = 'menu')
	qws.add(piln)
	await bot.send_message(call.from_user.id, '*Нашли баг❓ \nЕсть идея или предложение❓*\n\nВы всегда можете обратиться к *@the_sloth_bear*, либо к [специальному боту](https://t.me/elschool_help_support_bot)', parse_mode = 'markdown', reply_markup=qws)
asyncio.run(bot.polling(none_stop=True, interval=0))
