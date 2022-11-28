import os
import re
import time
import copy
import shutil
import _thread
import gspread
import requests
from time import sleep
from telebot import types
import functions as objects
from bs4 import BeautifulSoup
from datetime import datetime
from functions import bold, time_now

stamp1 = time_now()
objects.environmental_files()
client1 = gspread.service_account('person1.json')
used1 = client1.open('memes').worksheet('used-links')
main1 = client1.open('memes').worksheet('main')
used_links_time = used1.col_values(2)
channels_post = main1.col_values(2)
used_links = used1.col_values(1)
channels = main1.col_values(1)

file_db = []
dislike = '👎🏿 '
idMe = 396978030
white_like = '👍🏻 '
yellow_like = '👍 '
idChannelMain = -1001173823433
idChannelFilter = -1001226018838
allowed_persons = [idMe, 470292601, 457209276, 574555477]
# =================================================================


def likes(like, like_col, dislike_col):
    likes_row = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=like + str(like_col), callback_data='like'),
               types.InlineKeyboardButton(text=dislike + str(dislike_col), callback_data='dislike')]
    likes_row.add(*buttons)
    return likes_row


def stamp_dict(stamp):
    data = {
        'weekday': datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%a'),
        'hour': datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%H')
    }
    return data


for w in used_links:
    if w != '':
        week = int(datetime.now().timestamp()) - 7 * 24 * 60 * 60
        if week < int(used_links_time[used_links.index(w)]):
            try:
                outer_response = requests.get(w, stream=True)
            except IndexError and Exception:
                outer_response = False
            search_videos = re.search(r'.*\.mp4\?token=.*', w)
            if search_videos:
                outer_extension = '.mp4'
            else:
                outer_extension = '.jpg'
            with open('starting' + outer_extension, 'wb') as outer_file:
                if outer_response:
                    shutil.copyfileobj(outer_response.raw, outer_file)
            with open('starting' + outer_extension, 'rb') as outer_file:
                outer_reading = outer_file.read()
            if outer_reading not in file_db:
                file_db.append(outer_reading)

Auth = objects.AuthCentre(os.environ['TOKEN'])
bot = Auth.start_main_bot('non-async')
executive = Auth.thread_exec
Auth.start_message(stamp1)
# ====================================================================================


def post_media(raw, id_address, likes_keys):
    global used1
    media = []
    doc = None
    caption = None
    close_docs = []
    media_pointer = 1
    founded_ad = False
    for i in raw['links']:
        search_video = re.search(r'.*\.mp4\?token=.*', i)
        if media_pointer == 1 and raw['text'] != 'None':
            search_ad_1 = re.search(r'https://t.me/.*', raw['text'])
            search_ad_2 = re.search('@.+', raw['text'])
            if search_ad_1 or search_ad_2:
                founded_ad = True
            text = re.sub(r'https://t.me/joinchat/\S{22}', '', raw['text'])
            caption = re.sub(r'@.+?\W', '', text)
            caption = re.sub('@.+', '', caption)
        if search_video:
            extension = '.mp4'
            type_function = types.InputMediaVideo
        else:
            extension = '.jpg'
            type_function = types.InputMediaPhoto
        response = requests.get(i, stream=True)
        with open(str(media_pointer) + extension, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        with open(str(media_pointer) + extension, 'rb') as out_file:
            doc_reading = out_file.read()
        doc = open(str(media_pointer) + extension, 'rb')
        close_docs.append(doc)
        if doc_reading not in file_db:
            media.append(type_function(doc, caption=caption))
            file_db.append(doc_reading)
            media_pointer += 1
            if i not in used_links:
                try:
                    used1.insert_row([i, int(datetime.now().timestamp())], 1)
                except IndexError and Exception:
                    used1 = gspread.service_account('person1.json').open('memes').worksheet('used-links')
                    used1.insert_row([i, int(datetime.now().timestamp())], 1)
                used_links_time.insert(0, int(datetime.now().timestamp()))
                used_links.insert(0, i)
                sleep(1)
        else:
            doc = None
    if founded_ad is False:
        if len(raw['links']) == 1 and raw['type'] == 'gif' and doc is not None:
            bot.send_document(id_address, doc, caption=caption)
        elif len(raw['links']) == 1 and raw['type'] == 'video' and doc is not None:
            bot.send_video(id_address, doc, caption=caption)
        elif len(raw['links']) == 1 and raw['type'] == 'photo' and doc is not None:
            bot.send_photo(id_address, doc, caption=caption)
        else:
            if len(media) > 0:
                bot.send_media_group(id_address, media)
                # здесь был постинг кнопок для собранных в группу медиа, отключил, все равно кнопки не работают
                # if len(pin) > 0:
                #    if pin[0].chat.username is not None:
                #        bot.send_message(id_address, 'https://t.me/' +
                #                         pin[0].chat.username + '/' + str(pin[0].message_id),
                #                         disable_web_page_preview=True)
    for i in close_docs:
        i.close()


def posting(link, true_stamp):
    text = requests.get(link + '?embed=1')
    soup = BeautifulSoup(text.text, 'html.parser')
    is_post_not_exist = soup.find('div', class_='tgme_widget_message_error')
    is_post_not_forward = soup.find('div', class_='tgme_widget_message_forwarded_from')
    post = {'post': link, 'median': 0, 'viewers': 0, 'stamp': 0,
            'data': '', 'text': 'None', 'type': 'None', 'links': []}
    if str(is_post_not_exist) == 'None':
        date = soup.find('time', class_='datetime')
        text = soup.find('div', class_='tgme_widget_message_text js-message_text')
        view = soup.find('span', class_='tgme_widget_message_views')
        picture = soup.find_all('a', class_='tgme_widget_message_photo_wrap')
        if len(picture) > 0:
            for i in picture:
                search = re.search(r'url\(\'(.*?)\'\)', str(i.get('style')))
                if search:
                    if len(picture) == 1:
                        post['type'] = 'photo'
                    post['links'].append(search.group(1))
        video = soup.find_all('video', class_='js-message_video')
        if len(video) > 0:
            for i in video:
                gif_condition = ['preload', 'muted', 'autoplay', 'loop', 'playsinline']
                if len([e for e in gif_condition if e not in i.attrs]) == 0:
                    post['type'] = 'gif'
                elif len(video) == 1:
                    post['type'] = 'video'
                post['links'].append(i.get('src'))
        if str(view) != 'None':
            if str(is_post_not_forward) != 'None':
                post['links'] = 'forwarded message'
                post['viewers'] = 0
            else:
                viewers = 1
                search = re.search('([MK])', view.get_text())
                if search:
                    if search.group(1) == 'M':
                        viewers = 1000000
                    elif search.group(1) == 'K':
                        viewers = 1000
                viewers *= float(re.sub('[MK]', '', view.get_text()))
                post['viewers'] = int(viewers)
        if str(text) != 'None':
            post['text'] = text.get_text()
        if str(date) != 'None':
            stamp = int(time.mktime(datetime.strptime(date.get('datetime'), '%Y-%m-%dT%H:%M:%S+00:00').timetuple()))
            post['data'] = date.get('datetime')
            if stamp >= true_stamp:
                post['stamp'] = stamp
            else:
                post['stamp'] = -1
    else:
        post['viewers'] = 'None'
        post['stamp'] = 'None'
    return post


def goodies(stamp, number):
    global main1
    goodies_raw = []
    empty_channels = ''
    for i in channels:
        imp = 0
        channel_db = []
        post_channel = i
        limiter_point = 0
        post_stamp = stamp
        post_id = int(channels_post[channels.index(i)])
        post_stag = copy.copy(post_id)
        post_last = copy.copy(post_id)
        post_stag_limiter = post_id * 0.01
        if post_stag_limiter < 40:
            post_stag_limiter = 40
        elif post_stag_limiter > 70:
            post_stag_limiter = 70
        while imp <= 10:
            post = posting(post_channel + str(post_id), stamp)
            if post['links'] != [] and post['viewers'] != 'None' and post['stamp'] != 'None':
                if post['stamp'] != -1:
                    channel_db.append(post)
                post_last = post_id
                imp = 0
            elif post['links'] == [] and post['viewers'] == 'None' and post['stamp'] == 'None':
                if post_stag == post_id:
                    post_last -= 1
                imp += 1
            post_id += 1
        post_last += 1

        if post_stag != post_last:
            try:
                main1.update_cell(channels.index(i) + 1, 2, post_last)
            except IndexError and Exception:
                main1 = gspread.service_account('person1.json').open('memes').worksheet('main')
                main1.update_cell(channels.index(i) + 1, 2, post_last)

        while post_stamp >= stamp:
            post_stag -= 1
            post_back = posting(post_channel + str(post_stag), stamp)
            if post_back['links'] != [] and post_back['viewers'] != 'None' and post_back['stamp'] != 'None':
                limiter_point = 0
                if post_back['stamp'] != 'None':
                    post_stamp = post_back['stamp']
                if post_back['stamp'] != -1:
                    channel_db.append(post_back)
            else:
                limiter_point += 1
            if limiter_point > post_stag_limiter:
                break

        channel_db.sort(key=lambda arr: arr['viewers'])

        if len(channel_db) % 2 == 0 and len(channel_db) != 0:
            lot1 = channel_db[len(channel_db) // 2]['viewers']
            lot2 = channel_db[len(channel_db) // 2 - 1]['viewers']
            median = int(round((lot1 + lot2) / 2, 2))
        elif len(channel_db) == 0:
            median = 0
        else:
            median = channel_db[len(channel_db) // 2]['viewers']

        if len(channel_db) > 0:
            good_post = channel_db[len(channel_db) - 1]
            if median != 0:
                good_post['median'] = good_post['viewers'] / median
            else:
                good_post['median'] = 0
            goodies_raw.append(good_post)
        else:
            empty_channels += '\n' + post_channel
    goodies_raw.sort(key=lambda arr: arr['median'])
    good_posting = list(reversed(goodies_raw))
    if len(good_posting) <= number:
        for i in good_posting:
            post_media(i, idChannelFilter, likes(white_like, 0, 0))
    else:
        for i in range(0, number):
            post_media(good_posting[i], idChannelFilter, likes(white_like, 0, 0))
    if len(empty_channels) > 0:
        bot.send_message(idMe, bold('Никаких постов от:') + empty_channels, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    try:
        if call.data == 'like' or call.data == 'dislike':
            like_number = 0
            dislike_number = 0
            already_posted = None
            like_type = white_like
            like_dislike_array = []
            like_json = call.message.json
            if like_json is not None:
                like_dislike_array = like_json['reply_markup']['inline_keyboard'][0]
            for i in like_dislike_array:
                if i['callback_data'] == 'like':
                    search_like = re.search(white_like, i['text'])
                    search = re.search(r'(\d+)', i['text'])
                    if search:
                        like_number += int(search.group(1))
                    if search_like is None:
                        like_type = yellow_like
                        already_posted = True
                elif i['callback_data'] == 'dislike':
                    search = re.search(r'(\d+)', i['text'])
                    if search:
                        dislike_number += int(search.group(1))
            if call.data == 'like':
                like_number += 1
                if call.from_user.id in allowed_persons and already_posted is None:
                    like_type = yellow_like
                    if call.message.caption:
                        caption = call.message.caption
                    else:
                        caption = None
                    if call.message.video:
                        bot.send_video(idChannelMain, call.message.video.file_id, caption=caption, parse_mode='HTML')
                    elif call.message.document:
                        bot.send_document(idChannelMain, call.message.document.file_id,
                                          caption=caption, parse_mode='HTML')
                    elif call.message.photo:
                        bot.send_photo(idChannelMain, call.message.photo[len(call.message.photo) - 1].file_id,
                                       caption=caption, parse_mode='HTML')
                    elif call.message.text.startswith('https://t.me/'):
                        post = posting(call.message.text, int(datetime.now().timestamp()))
                        post_media(post, idChannelMain, likes(white_like, 0, 0))

            elif call.data == 'dislike':
                dislike_number += 1
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.answer_callback_query(call.id, text='')
    except IndexError and Exception:
        executive(str(call))


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    try:
        if message.chat.id in allowed_persons:
            if message.text.startswith('https://t.me/'):
                post = posting(message.text, int(datetime.now().timestamp()))
                post_media(post, idChannelFilter, likes(white_like, 0, 0))
            elif message.text.startswith('/mem'):
                search = re.search(r'(\d+) (\d+)', message.text)
                if search:
                    goodies(int(datetime.now().timestamp()) - int(search.group(1)) * 60 * 60, int(search.group(2)))
                    bot.send_message(message.chat.id, bold('Выполнено успешно ✅'), parse_mode='HTML')
                else:
                    bot.send_message(message.chat.id, bold('херня какая-то ❌'), parse_mode='HTML')
            elif message.text == '/update':
                global main1, channels, channels_post
                main1 = gspread.service_account('person1.json').open('memes').worksheet('main')
                channels_post = main1.col_values(2)
                channels = main1.col_values(1)
                bot.send_message(message.chat.id, bold('Обновлено успешно ✅'), parse_mode='HTML')
            elif message.text.startswith('/log'):
                bot.send_document(idMe, open('log.txt', 'rt'))
            else:
                bot.send_message(message.chat.id, bold('ссылка не подошла'), parse_mode='HTML')
    except IndexError and Exception:
        executive(str(message))


def hourly():
    while True:
        try:
            sleep(300)
            objects.printer('работаю ' + objects.log_time(time_now() - 2 * 60 * 60))
            goodies(time_now() - 2 * 60 * 60, 5)
            sleep(3300)
        except IndexError and Exception:
            executive()


def daily():
    while True:
        try:
            now_dict = stamp_dict(time_now())
            if now_dict['hour'] == '21':
                objects.printer('работаю ' + objects.log_time(time_now() - 24 * 60 * 60))
                goodies(time_now() - 24 * 60 * 60, 10)
                sleep(3600)
            sleep(300)
        except IndexError and Exception:
            executive()


def weekly():
    while True:
        try:
            now_dict = stamp_dict(time_now())
            if now_dict['weekday'] == 'Wed' and now_dict['hour'] == '18':
                objects.printer('работаю ' + objects.log_time(time_now() - 7 * 24 * 60 * 60))
                goodies(time_now() - 7 * 24 * 60 * 60, 10)
                sleep(3600)
            sleep(300)
        except IndexError and Exception:
            executive()


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60)
    except IndexError and Exception:
        bot.stop_polling()
        sleep(1)
        telegram_polling()


def start():
    gain = [hourly, daily, weekly]
    for func in gain:
        _thread.start_new_thread(func, ())
    telegram_polling()


if __name__ == '__main__':
    start()
