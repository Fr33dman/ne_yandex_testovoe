from bs4 import BeautifulSoup
import requests
import re

import settings
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from models import engine, News


def clean_a_tags(subtitle: str) -> str:
    """
    Отчищает тэги <a> в тексте от ненужных параметров (оставляет только гиперссылки)
    :param subtitle: html строка с гиперссылками
    :return: отчищенная html строка с гиперссылками
    """
    delete_attrs = re.compile('<a href=".+?"(.+?>)')
    delete_string = re.findall(delete_attrs, subtitle)
    for string in delete_string:
        subtitle = subtitle.replace(string[:-1], '')
    return subtitle


def parse_news_website(a) -> dict:
    uri = 'https://vc.ru/'
    page = requests.get(uri)
    soup = BeautifulSoup(page.text, 'html.parser')

    result = {
        'author': None,
        'title': None,
        'body': None,
        'source_url': None,
        'images': None,
        'videos': None,
    }

    div_news = soup.find('div', **{'data-gtm': f'Feed — Item {a} — Click'})

    author = div_news.find('div', **{'class': 'content-header-author__name'})
    result['author'] = author.getText().strip()

    title = div_news.find('div', **{'class': 'content-title content-title--short l-island-a'})
    skip_text = title.find('span', **{'class': 'content-editorial-tick'})
    if skip_text:
        skip_text.extract()
    result['title'] = f'<b>{title.getText().strip()}</b>'

    body = div_news.select('div[class="l-island-a"]')[0]
    body_html = str(body.find('p')).replace('<p>', '').replace('</p>', '')
    result['body'] = clean_a_tags(body_html)

    source_url = div_news.find('a', **{'class': 'content-link'}).get('href')
    result['source'] = source_url

    figure_images = div_news.findAll('figure', **{'class': 'figure-image'})
    images = {}
    if figure_images:
        div_content_image = figure_images[0].findAll('div', {'class': 'content-image'})[0]
        image_info = div_content_image.findAll('div')
        for img in image_info:
            image_src = img.get('data-image-src')
            image_info = img.get('data-image-title')
            if image_src:
                images[image_src] = image_info
    result['images'] = images if images else None

    figure_videos = div_news.findAll('figure', **{'class': 'figure-video'})
    videos = []
    if figure_videos:
        video_info = figure_videos.findAll('div')
        for img in video_info:
            video_src = img.get('data-source-url')
            if video_src:
                videos.append(video_src)
    result['videos'] = videos if videos else None

    return result


def news2message(news: dict) -> str:
    """
    Подставляет данные из словаря с новостью в шаблон
    :param news: новость собранная в словарь
    :return: готовое к отправке сообщение
    """
    template = 'Источник: {author}\n\n' \
               '{title}\n' \
               '{body}\n' \
               '<a href="{source_url}">Читать полностью в источнике</a>'
    result = template.format(author=news.get('author'), title=news.get('title'),
                             body=news.get('body'), source_url=news.get('source'))

    # Добавляем ссылки на видео если таковые имеются
    videos = news.get('videos')
    if videos:
        for video in videos:
            result = f'{result}\n{video}'

    return result


class SimpleBot:
    # token = settings.BOT_TOKEN
    token = '5217948757:AAFiLo0sdatr12asCOMN6CYKBVc2JTBDYNU'
    base_url = 'https://api.telegram.org/bot{token}/{method}'
    # channel = settings.TELEGRAM_CHANNEL
    channel = '-1001763325487'

    def send_message(self, message: str) -> requests.Response:
        url = self.base_url.format(token=self.token, method='sendMessage')
        data = {
            'chat_id': self.channel,
            'text': message,
            'parse_mode': 'HTML',
        }
        return requests.post(url, data=data)

    def reply_image(self, message_id: int, image_link: str, caption: str = None) -> requests.Response:
        url = self.base_url.format(token=self.token, method='sendPhoto')
        data = {
            'chat_id': self.channel,
            'photo': image_link,
            'reply_to_message_id': message_id,
        }

        if caption:
            if len(caption) > 200:
                caption = caption[:200]
            data['caption'] = caption

        return requests.post(url, data=data)

    def work(self, index):
        news = parse_news_website(index)
        with Session(engine) as session:
            news_exists = session.query(exists().where(News.source == news.get('source'))).scalar()
        if news_exists:
            return
        message = news2message(news)
        response_message = self.send_message(message)
        if response_message.status_code != 200:
            return

        message_id = response_message.json().get('result').get('message_id')
        images = news.get('images')
        if images:
            for image_link, image_description in images.items():
                response_image = self.reply_image(message_id, image_link, image_description)
                if response_image.status_code != 200:
                    return

        with Session(engine) as session:
            instance = News(
                author=news.get('author'),
                title=news.get('title'),
                body=news.get('body'),
                source=news.get('source'),
            )
            session.add(instance)
            session.commit()


if __name__ == '__main__':
    bot = SimpleBot()
    for i in range(1, 12):
        bot.work(i)
