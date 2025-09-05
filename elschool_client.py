import aiohttp
import json
import random
import urllib.parse


class ElschoolClient:
    def __init__(self, jwtoken, refresh_token):
        self.session = None
        self.base_url = "https://elschool.ru"
        self.jwtoken = jwtoken
        self.refresh_token = refresh_token
        self.ajax_token = None

    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        await self._initialize_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        if self.session:
            await self.session.close()

    async def _initialize_session(self):
        """Инициализация асинхронной сессии"""
        if self.session is None:
            # Создаем сессию с пустым cookie jar
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Origin': self.base_url,
                    'Referer': f'{self.base_url}/Logon/Index',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )

            # Устанавливаем куки напрямую через заголовки
            self.session.cookie_jar.update_cookies({
                'JWToken': self.jwtoken,
                'RefreshToken': self.refresh_token
            })

    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            self.session = None

    def generate_mouse_coordinates(self, start_x=400, start_y=300, num_points=12):
        """Генерирует правдоподобную траекторию мыши"""
        coords = []
        x, y = start_x, start_y

        for i in range(num_points):
            x += random.randint(-10, 10)
            y += random.randint(-10, 10)

            if random.random() < 0.2:
                x += random.randint(-50, 50)
                y += random.randint(-50, 50)

            x = max(100, min(1000, x))
            y = max(100, min(800, y))

            coords.append([x, y])

        return coords

    def prepare_request_body(self, coordinates):
        """Подготавливает тело запроса"""
        payload_data = {
            "event": "user_coords",
            "data": coordinates,
            "host": "elschool.ru"
        }

        json_str = json.dumps(payload_data)
        url_encoded = urllib.parse.quote(json_str)
        hex_payload = url_encoded.encode('utf-8').hex()

        return hex_payload

    async def refresh_token_func(self):
        """Обновляем JWT токен (асинхронно)"""
        print('Начинаю обновление токена')
        try:
            await self._initialize_session()

            # Получаем актуальный AJAX token с главной страницы
            async with self.session.get(f'{self.base_url}/Logon/Index') as response:
                html = await response.text()

                # Ищем token в HTML
                if 'ajax-token' in html:
                    start = html.find('ajax-token') + 20
                    end = html.find('"', start)
                    self.ajax_token = html[start:end]

            # Генерируем данные мыши
            mouse_coords = self.generate_mouse_coordinates()
            hex_body = self.prepare_request_body(mouse_coords)

            # Отправляем запрос на обновление
            refresh_url = f"{self.base_url}/be88bff3d3ee9b54864e50789d7a72cd"

            headers = {
                'X-Ajax-Token': self.ajax_token,
                'Content-Type': 'application/octet-stream',
                'Content-Length': str(len(hex_body) // 2)
            }

            async with self.session.post(
                refresh_url,
                data=bytes.fromhex(hex_body),
                headers=headers
            ) as response:
                if response.status == 200:
                    print("Токен обновлен успешно")
                    return True

        except Exception as e:
            print(f"Ошибка обновления токена: {e}")

        return False

    async def auth(self):
        """Асинхронная авторизация"""
        api_url = f"{self.base_url}/users/privateoffice"

        try:
            await self._initialize_session()

            async with self.session.get(api_url, allow_redirects=False) as response:
                # print(await response.text())
                if response.status == 200:
                    text = await response.text()
                    return True, text
                elif response.status == 401:
                    if await self.refresh_token_func():
                        # Повторяем запрос после обновления
                        async with self.session.get(api_url) as new_response:
                            if new_response.status == 200:
                                text = await new_response.text()
                                return True, text
                            else:
                                # print(new_response.status)
                                pass

            return False, ''

        except Exception as e:
            print(f"Ошибка авторизации: {e}")
            return False, ''

    async def get_url(self, url):
        try:
            await self._initialize_session()

            async with self.session.get(url) as response:
                # print(await response.text())
                if response.status == 200:
                    text = await response.text()
                    return True, text
                elif response.status == 401:
                    if await self.refresh_token_func():
                        # Повторяем запрос после обновления
                        async with self.session.get(url) as new_response:
                            if new_response.status == 200:
                                text = await new_response.text()
                                return True, text

            return False, ''

        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return False, ''
