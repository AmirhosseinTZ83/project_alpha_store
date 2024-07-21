import mysql.connector
from config import *

def get_db_connection():
    return mysql.connector.connect(
        user=db_username,
        password=db_password,
        host='localhost',
        database='alpha_store'
    )

def insert_user_info(cid, first_name, last_name,phone_number, username=None, email=None, privilage='user'):
    conn=mysql.connector.connect(user=db_username,password=db_password,host='localhost',database='alpha_store')
    cursor=conn.cursor()
    SQL_QUARY="""INSERT INTO user (cid, first_name, last_name, username, phone_number, email, privilage)
    VALUES (%s,%s,%s,%s,%s,%s,%s);"""
    cursor.execute(SQL_QUARY,(cid, first_name, last_name, username, phone_number, email, privilage))
    conn.commit()
    cursor.close()
    conn.close()
    print('value inserted to user table')


def insert_product_info(name, brand ,description, image_file_id, price, inventory, category):
    conn=mysql.connector.connect(user=db_username,password=db_password,host='localhost',database='alpha_store')
    cursor=conn.cursor()
    SQL_QUARY="""INSERT INTO product (name, brand ,description, image_file_id, price, inventory, category)
    VALUES (%s,%s,%s,%s,%s,%s,%s);"""
    cursor.execute(SQL_QUARY,(name, brand ,description, image_file_id, price, inventory, category))
    conn.commit()
    cursor.close()
    conn.close()
    print('value inserted to product table')


def create_sale(user_cid):
    conn = mysql.connector.connect(user=db_username, password=db_password, host='localhost', database='alpha_store')
    cursor = conn.cursor()
    SQL_QUERY = "INSERT INTO sale (user_cid) VALUES (%s)"
    cursor.execute(SQL_QUERY, (user_cid,))
    sale_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return sale_id

def create_sale_row(sale_id, product_id, quantity):
    conn = mysql.connector.connect(user=db_username, password=db_password, host='localhost', database='alpha_store')
    cursor = conn.cursor()
    SQL_QUERY = "INSERT INTO sale_row (sale_id, product_id, quantity) VALUES (%s, %s, %s)"
    cursor.execute(SQL_QUERY, (sale_id, product_id, quantity))
    conn.commit()
    cursor.close()
    conn.close()

