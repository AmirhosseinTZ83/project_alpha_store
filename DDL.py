import mysql.connector
from config import *

def create_alpha_store_database():
    conn = mysql.connector.connect(user=db_username, password=db_password, host='localhost')
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS alpha_store")
    cursor.close()
    conn.close()
    print('alpha_store database created')

def create_user_table():
    conn = mysql.connector.connect(user=db_username, password=db_password, host='localhost', database='alpha_store')
    cursor = conn.cursor()
    SQL_QUERY = """
    CREATE TABLE IF NOT EXISTS user(
    cid           BIGINT PRIMARY KEY NOT NULL,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50),
    username      VARCHAR(32),
    phone_number  VARCHAR(15),
    date          DATETIME DEFAULT CURRENT_TIMESTAMP,
    email         VARCHAR(100),
    privilage     ENUM('user', 'admin')
    );
    """
    cursor.execute(SQL_QUERY)
    cursor.close()
    conn.close()
    print('user table created')

def create_product_table():
    conn = mysql.connector.connect(user=db_username, password=db_password, host='localhost', database='alpha_store')
    cursor = conn.cursor()
    SQL_QUERY = """
    CREATE TABLE IF NOT EXISTS product(
    id              INT NOT NULL AUTO_INCREMENT,
    name            VARCHAR(50) NOT NULL,
    brand           VARCHAR(50) NOT NULL,
    description     VARCHAR(300), 
    image_file_id   VARCHAR(200),
    price           DOUBLE NOT NULL,
    inventory       INT NOT NULL DEFAULT 0,
    category        ENUM('phone','watches','earphones'),
    PRIMARY KEY (id)
    );
    """
    cursor.execute(SQL_QUERY)
    cursor.close()
    conn.close()
    print('product table created')


def create_sale_table():
    conn = mysql.connector.connect(user=db_username, password=db_password, host='localhost', database='alpha_store')
    cursor = conn.cursor()
    SQL_QUERY = """
    CREATE TABLE IF NOT EXISTS sale(
    id              INT NOT NULL AUTO_INCREMENT,
    user_cid        BIGINT NOT NULL,
    date            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_cid) REFERENCES user(cid)
    );  
    """
    cursor.execute(SQL_QUERY)
    cursor.close()
    conn.close()
    print('sale table created')

def create_sale_row_table():
    conn = mysql.connector.connect(user=db_username, password=db_password, host='localhost', database='alpha_store')
    cursor = conn.cursor()
    SQL_QUERY = """
    CREATE TABLE IF NOT EXISTS sale_row(
    sale_id       INT NOT NULL,
    product_id    INT NOT NULL,
    quantity      SMALLINT NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sale(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
    );  
    """
    cursor.execute(SQL_QUERY)
    cursor.close()
    conn.close()
    print('sale_row table created')