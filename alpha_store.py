
import telebot
from telebot import TeleBot, types
import logging
import time
from telebot.types import ReplyKeyboardMarkup,InlineKeyboardMarkup,InlineKeyboardButton
from telebot.types import InputMediaPhoto
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import mysql.connector

from DDL import *
from DML import *
from DQL import *
from config import *

known_users=[]


if __name__ == "__main__":
    create_alpha_store_database()
    create_user_table()
    create_product_table()
    create_sale_table()
    create_sale_row_table()


logging.basicConfig(filename='alpha_store_doc.log',filemode='a',level=logging.INFO,format='%(asctime)s - %(message)s - %(levelname)s ')

API_TOKEN=bottoken

user_steps=dict()

shopping_cart=dict()

commands={
'keyboard'        :'--------------------------------------🔵',
}

admins_commands={
'qr_admin'        :'this line is for admin',
'add_product'     :'add your products'
}

texts={
'help'            :'برای دیدن محصولات یا صفحه اصلی میتوانید با فشردن بر روی کلمه keyboard آنها را مشاهده کنید:\n',
'help_admin'      : "*****دسترسی مخصوص ادمین*****: \n",
'messages_anyone' :'مقدار وارد شده اشتباه است❌\n برای اطلاعات بیشتر میتوانید به راهنمای ربات مراجعه کنید.',
'admin_ac'        :'سلام شما ادمین هستید.خوش امدید.',
}


def get_user_steps(cid):
    return user_steps.setdefault(cid,0)
bot=telebot.TeleBot(API_TOKEN,num_threads=10)
hideboard=ReplyKeyboardRemove()


def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
            logging.info(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(API_TOKEN)
bot.set_update_listener(listener)  # register listener


@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid=message.chat.id
    if cid not in known_users:
        cid=message.chat.id
        first_name=message.chat.first_name
        last_name=message.chat.last_name
        username=message.chat.username
        insert_user_info(cid=cid, first_name=first_name, last_name=last_name, phone_number=None, username=username, email=None, privilage='user')
    bot.reply_to(message,'🔵سلام خیلی خوش امدید به فروشگاه الفا.\n\n📌در این فروشگاه شما میتوانید انواع گوشیها و ساعت های هوشمند و ...کلی لواز دیگرو انتخاب کنید و خریداری کنید یا حتی باهم مقایسشون کنید.\n\n📣پیشنهاد ما این هستش که اگه میخواید با روند بهتر بات بیشتر اشنا بشید گزینه menuرا انتخاب کنید و بعد هم در مرحله اخر گزینه helpرا انتخاب نمایید')

@bot.message_handler(commands=['qr_admin'])
def qr_admin_command(message):
    cid = message.chat.id
    if cid in admins:
        bot.send_message(cid,texts['admin_ac'])
    else:
        echo_message(message)


@bot.message_handler(commands=['add_product'])
def add_product_command(message):
    cid=message.chat.id
    if cid not in admins:
        echo_message(message)
        return
    cid=message.chat.id
    text="""
please send product photo with following caption template:
*name*brand*description*price*inventory*category*
"""
    bot.send_message(cid,text)
    user_steps[cid]=1000

bot.message_handler(func=lambda message:get_user_steps(message.chat.id)==1000)
def step_by_step(message):
    cid = message.chat.id
    if cid in admins:
        bot.send_message(cid,'please send photo with caption')

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    cid = message.chat.id
    if cid in admins and user_steps[cid]==1000:
        caption=message.caption
        file_id=message.photo[-1].file_id
        name,brand ,description, price, inventory, category=caption.strip('*').split('*')
        insert_product_info(name=name,brand=brand ,description=description, image_file_id=file_id, price=float(price), inventory=int(inventory), category=category)
        bot.send_message(cid,'product info inserted succesesfully')
        user_steps[cid]=0
    else:
        echo_message(message)


# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = texts['help']
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    if cid in admins:
        help_text +=texts['help_admin']
        for key in admins_commands:  # generate help text out of the commands dictionary defined at the top
            help_text += "/" + key + ": "
            help_text += admins_commands[key] + "\n"

    bot.send_message(cid, help_text)  # send the generated help page    

@bot.message_handler(commands=['keyboard'])
def keyboard_m(message):
    cid=message.chat.id
    markup=ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
    markup.add('گوشی ها📱','لوازم جانبی⌚️','منوی کاربری👤','سبد خرید🛒')
    bot.send_message(cid,'⬇️از موارد زیر درخواست مورد نظر را انتخاب کنید⬇️',reply_markup=markup)

#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@bot.message_handler(func=lambda message: message.text == 'گوشی ها📱')
def show_phone_brands(message):
    cid = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('Samsung', callback_data='phone_brand_samsung'),
        types.InlineKeyboardButton('Xiaomi', callback_data='phone_brand_xiaomi'),
        types.InlineKeyboardButton('Apple', callback_data='phone_brand_apple'),
        types.InlineKeyboardButton('Huawei', callback_data='phone_brand_huawei'),
        types.InlineKeyboardButton('Oneplus', callback_data='phone_brand_oneplus'),
    )
    bot.send_message(cid, '🔵لطفاً یک برند گوشی را انتخاب کنید:', reply_markup=markup)

def get_products_by_brand(brand):
    conn = mysql.connector.connect(user='root', password='amir83', host='localhost', database='alpha_store')
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product WHERE category = 'phone' AND brand = %s", (brand,))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def generate_phone_product_markup(brand, index, total):
    markup = types.InlineKeyboardMarkup(row_width=3)
    prev_button = types.InlineKeyboardButton('⬅️', callback_data=f'phone_prev_{brand}_{index}')
    next_button = types.InlineKeyboardButton('➡️', callback_data=f'phone_next_{brand}_{index}')
    add_to_cart_button = types.InlineKeyboardButton('افزودن به سبد خرید', callback_data=f'phone_add_{brand}_{index}')
    markup.add(prev_button, types.InlineKeyboardButton(f'{index + 1}/{total}', callback_data='ignore'), next_button)
    markup.add(add_to_cart_button)
    return markup

def show_phone_products(call, brand, index, is_new_message=True):
    products = get_products_by_brand(brand)
    if products:
        product = products[index]
        cid = call.message.chat.id
        if is_new_message:
            bot.send_photo(cid, product['image_file_id'], caption=f"{product['name']}\n\n{product['description']}\nقیمت: {product['price']}", reply_markup=generate_phone_product_markup(brand, index, len(products)))
        else:
            bot.edit_message_media(media=types.InputMediaPhoto(product['image_file_id']), chat_id=cid, message_id=call.message.message_id)
            bot.edit_message_caption(caption=f"{product['name']}\n\n{product['description']}\nقیمت: {product['price']}", chat_id=cid, message_id=call.message.message_id, reply_markup=generate_phone_product_markup(brand, index, len(products)))

@bot.callback_query_handler(func=lambda call: call.data.startswith('phone_brand_'))
def show_brand_phone_products(call):
    brand = call.data.split('_')[-1]
    show_phone_products(call, brand, 0)

@bot.callback_query_handler(func=lambda call: call.data.startswith('phone_prev_') or call.data.startswith('phone_next_'))
def navigate_phone_products(call):
    parts = call.data.split('_')
    brand, index = parts[2], int(parts[3])
    products = get_products_by_brand(brand)
    if call.data.startswith('phone_prev_'):
        index = (index - 1) % len(products)
    elif call.data.startswith('phone_next_'):
        index = (index + 1) % len(products)
    show_phone_products(call, brand, index, is_new_message=False)

@bot.callback_query_handler(func=lambda call: call.data.startswith('phone_add_'))
def add_phone_to_cart(call):
    parts = call.data.split('_')
    brand, index = parts[2], int(parts[3])
    products = get_products_by_brand(brand)
    product = products[index]
    cid = call.message.chat.id
    user_cart = shopping_cart.get(cid, [])
    user_cart.append(product)
    shopping_cart[cid] = user_cart

    conn = mysql.connector.connect(user='root', password='amir83', host='localhost', database='alpha_store')
    cursor = conn.cursor()
    cursor.execute("UPDATE product SET inventory = inventory - 1 WHERE id = %s", (product['id'],))
    conn.commit()
    cursor.close()
    conn.close()

    bot.answer_callback_query(call.id, text=f"{product['name']} به سبد خرید شما افزوده شد.")

@bot.callback_query_handler(func=lambda call: call.data == 'buy_product')
def buy_product_callback(call):
    cid = call.message.chat.id
    bot.send_message(cid, 'شما به فرآیند خرید هدایت می‌شوید...')

#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________        

@bot.message_handler(func=lambda message: message.text == 'لوازم جانبی⌚️')
def show_accessories(message):
    cid = message.chat.id
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton('ساعت هوشمند /watches⌚️', callback_data='accessory_watch_p'),
        InlineKeyboardButton('هندزفری/earphones🎧', callback_data='accessory_earphon_p'),
    )
    bot.send_message(cid, 'لطفا یک دسته بندی را انتخاب کنید:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'accessory_watch_p')
def show_watch_brands(call):
    cid = call.message.chat.id
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton('samsung', callback_data='watch_model_samsung'),
        InlineKeyboardButton('apple', callback_data='watch_model_apple'),
        InlineKeyboardButton('xiaomi', callback_data='watch_model_xiaomi'),
    )
    bot.send_message(cid, '🔵لطفاً یک برند ساعت را انتخاب کنید:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'accessory_earphon_p')
def show_earphon_brands(call):
    cid = call.message.chat.id
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton('qcy', callback_data='earphon_model_qcy'),
        InlineKeyboardButton('apple', callback_data='earphon_model_apple'),
        InlineKeyboardButton('samsung', callback_data='earphon_model_samsung'),
    )
    bot.send_message(cid, '🔵لطفاً یک برند هندزفری را انتخاب کنید:', reply_markup=markup)

def generate_product_markup(products, index, category, brand):  
    markup = InlineKeyboardMarkup(row_width=3)
    prev_button = InlineKeyboardButton('⬅️', callback_data=f'product_prev_{category}_{brand}_{index}')
    next_button = InlineKeyboardButton('➡️', callback_data=f'product_next_{category}_{brand}_{index}')
    add_to_cart_button = InlineKeyboardButton('افزودن به سبد خرید', callback_data=f'product_add_{category}_{brand}_{index}')
    markup.add(prev_button, InlineKeyboardButton(f'{index + 1}/{len(products)}', callback_data='ignore'), next_button)
    markup.add(add_to_cart_button)
    return markup

def show_products(call, products, index, category, brand, is_new_message=True):
    product = products[index]
    cid = call.message.chat.id
    if is_new_message:
        bot.send_photo(cid, product['image_file_id'], caption=f"{product['name']}\n\n{product['description']}\nقیمت: {product['price']}", reply_markup=generate_product_markup(products, index, category, brand))
    else:
        bot.edit_message_media(media=InputMediaPhoto(product['image_file_id']), chat_id=cid, message_id=call.message.message_id)
        bot.edit_message_caption(caption=f"{product['name']}\n\n{product['description']}\nقیمت: {product['price']}", chat_id=cid, message_id=call.message.message_id, reply_markup=generate_product_markup(products, index, category, brand))

@bot.callback_query_handler(func=lambda call: call.data.startswith('watch_model_'))
def show_model_watch_products(call):
    brand = call.data.split('_')[-1]
    products = get_products_by_category('watches')
    products = [p for p in products if p['brand'].lower() == brand.lower()]
    if products:
        show_products(call, products, 0, 'watches', brand)

@bot.callback_query_handler(func=lambda call: call.data.startswith('earphon_model_'))
def show_model_earphon_products(call):
    brand = call.data.split('_')[-1]
    products = get_products_by_category('earphones')
    products = [p for p in products if p['brand'].lower() == brand.lower()]
    if products:
        show_products(call, products, 0, 'earphones', brand)

@bot.callback_query_handler(func=lambda call: call.data.startswith('product_prev_') or call.data.startswith('product_next_'))
def navigate_products(call):
    parts = call.data.split('_')
    category = parts[2]
    brand = parts[3]
    index = int(parts[4])
    products = get_products_by_category(category)
    products = [p for p in products if p['brand'].lower() == brand.lower()]
    if call.data.startswith('product_prev_'):
        index = (index - 1) % len(products)
    elif call.data.startswith('product_next_'):
        index = (index + 1) % len(products)
    show_products(call, products, index, category, brand, is_new_message=False)

@bot.callback_query_handler(func=lambda call: call.data.startswith('product_add_'))
def add_product_to_cart(call):
    parts = call.data.split('_')
    category = parts[2]
    brand = parts[3]
    index = int(parts[4])
    products = get_products_by_category(category)
    products = [p for p in products if p['brand'].lower() == brand.lower()]
    product = products[index]
    cid = call.message.chat.id
    user_cart = shopping_cart.get(cid, [])
    user_cart.append(product)
    shopping_cart[cid] = user_cart
    bot.answer_callback_query(call.id, text=f"{product['name']} به سبد خرید شما افزوده شد.")

#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

user_data={}

@bot.message_handler(func=lambda message: message.text == 'منوی کاربری👤')
def request_profile_info(message):
    cid = message.chat.id
    if cid in user_data:
        send_profile_info(message)
    else:
        ask_for_first_name(message)

@bot.message_handler(commands=['start', 'profile'])
def ask_for_first_name(message):
    cid = message.chat.id
    msg = bot.send_message(cid, '🔵لطفا نام خود را وارد کنید:')
    bot.register_next_step_handler(msg, get_first_name)

def get_first_name(message):
    cid = message.chat.id
    user_data[cid] = {'first_name': message.text}
    msg = bot.send_message(cid, '🔵لطفا نام خانوادگی خود را وارد کنید:')
    bot.register_next_step_handler(msg, get_last_name)

def get_last_name(message):
    cid = message.chat.id
    user_data[cid]['last_name'] = message.text
    msg = bot.send_message(cid, '🔵لطفا شماره تلفن خود را وارد کنید:')
    bot.register_next_step_handler(msg, get_phone_number)

def get_phone_number(message):
    cid = message.chat.id
    user_data[cid]['phone_number'] = message.text
    send_profile_info(message)

def send_profile_info(message):
    cid = message.chat.id
    username = message.chat.username or 'نامشخص'
    first_name = user_data[cid].get('first_name', 'نامشخص')
    last_name = user_data[cid].get('last_name', 'نامشخص')
    phone_number = user_data[cid].get('phone_number', 'نامشخص')

    profile_message = (
        f'👤 پروفایل کاربری شما:\n\n'
        f'یوزرنیم: @{username}\n'
        f'نام: {first_name}\n'
        f'نام خانوادگی: {last_name}\n'
        f'شماره تلفن: {phone_number}'
    )

    bot.send_message(cid, profile_message, reply_markup=keyboard(message))

def keyboard(message):
    cid = message.chat.id
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(
        KeyboardButton('ویرایش نام'),
        KeyboardButton('ویرایش نام خانوادگی'),
        KeyboardButton('ویرایش شماره تلفن'),
        KeyboardButton('صفحه اصلی🏠')
    )
    return markup

@bot.message_handler(func=lambda message: message.text == 'ویرایش نام')
def edit_first_name(message):
    cid = message.chat.id
    msg = bot.send_message(cid, '🔵لطفا نام جدید خود را وارد کنید:')
    bot.register_next_step_handler(msg, update_first_name)

def update_first_name(message):
    cid = message.chat.id
    user_data[cid]['first_name'] = message.text
    bot.send_message(cid, '🔵نام شما با موفقیت به روز رسانی شد!')
    send_profile_info(message)

@bot.message_handler(func=lambda message: message.text == 'ویرایش نام خانوادگی')
def edit_last_name(message):
    cid = message.chat.id
    msg = bot.send_message(cid, '🔵لطفا نام خانوادگی جدید خود را وارد کنید:')
    bot.register_next_step_handler(msg, update_last_name)

def update_last_name(message):
    cid = message.chat.id
    user_data[cid]['last_name'] = message.text
    bot.send_message(cid, '🔵نام خانوادگی شما با موفقیت به روز رسانی شد!')
    send_profile_info(message)

@bot.message_handler(func=lambda message: message.text == 'ویرایش شماره تلفن')
def edit_phone_number(message):
    cid = message.chat.id
    msg = bot.send_message(cid, '🔵لطفا شماره تلفن جدید خود را وارد کنید:')
    bot.register_next_step_handler(msg, update_phone_number)

def update_phone_number(message):
    cid = message.chat.id
    user_data[cid]['phone_number'] = message.text
    bot.send_message(cid, '🔵شماره تلفن شما با موفقیت به روز رسانی شد!')
    send_profile_info(message)

@bot.message_handler(func=lambda message: message.text == 'صفحه اصلی🏠')
def main_menu(message):
    cid = message.chat.id
    markup = keyboard_m(message)
    bot.send_message(cid,'🔵شما به صفحه اصلی بازگشتید',reply_markup=markup)
    
#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________
shopping_cart = {}


@bot.message_handler(func=lambda message: message.text == 'سبد خرید🛒')
def show_cart(message):
    cid = message.chat.id
    username = message.from_user.username or message.from_user.first_name
    user_cart = shopping_cart.get(cid, [])
    if not user_cart:
        bot.send_message(cid, f"{username} عزیز، سبد خرید شما خالی است.")
        return
    
    cart_message = f"🛒 سبد خرید شما، {username} عزیز:\n"
    total_price = 0
    markup = InlineKeyboardMarkup(row_width=1)
    for idx, item in enumerate(user_cart):
        cart_message += f"{idx + 1}. {item['name']} - {item['price']} تومان\n"
        total_price += int(item['price'])
        markup.add(InlineKeyboardButton(f"❌ حذف {item['name']}", callback_data=f'remove_{idx}'))
    
    cart_message += f"\n💰 مجموع قیمت: {total_price} تومان"
    markup.add(InlineKeyboardButton('🗑 خالی کردن سبد خرید', callback_data='empty_cart'))
    markup.add(InlineKeyboardButton('💳 پرداخت', callback_data='pay_cart'))
    bot.send_message(cid, cart_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'empty_cart')
def empty_cart(call):
    cid = call.message.chat.id
    shopping_cart[cid] = []
    bot.answer_callback_query(call.id, text="سبد خرید شما خالی شد.")
    bot.edit_message_text("سبد خرید شما خالی است.", chat_id=cid, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('remove_'))
def remove_from_cart(call):
    cid = call.message.chat.id
    idx = int(call.data.split('_')[1])
    user_cart = shopping_cart.get(cid, [])
    if 0 <= idx < len(user_cart):
        removed_item = user_cart.pop(idx)
        shopping_cart[cid] = user_cart
        bot.answer_callback_query(call.id, text=f"{removed_item['name']} از سبد خرید حذف شد.")
        show_cart(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'pay_cart')
def pay_cart(call):
    cid = call.message.chat.id
    username = call.from_user.username or call.from_user.first_name
    user_cart = shopping_cart.get(cid, [])
    if not user_cart:
        bot.send_message(cid, "سبد خرید شما خالی است.")
        return
    sale_id = create_sale(cid)
    if sale_id is None:
        bot.send_message(cid, "خطایی رخ داده است. لطفا دوباره تلاش کنید.")
        return
    for item in user_cart:
        create_or_update_sale_row(sale_id, item['id'], item.get('quantity', 1))
        update_product_inventory(item['id'], item.get('quantity', 1))

    shopping_cart[cid] = []
    
    bot.send_message(cid, f'{username} عزیز، خرید شما با موفقیت ثبت شد. برای پرداخت به لینک زیر مراجعه کنید:\nhttps://mftplus.com/')

@bot.callback_query_handler(func=lambda call: call.data == 'buy_product')
def buy_product_callback(call):
    cid = call.message.chat.id
    username = call.from_user.username or call.from_user.first_name
    bot.send_message(cid, f'{username} عزیز، شما به فرآیند خرید هدایت می‌شوید...')

#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    cid=message.chat.id
    text=message.text
    bot.send_message(cid,texts['messages_anyone'],reply_to_message_id=message.message_id)
    #bot.reply_to(message, message.text)

bot.infinity_polling()
