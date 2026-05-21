# create_tables.py
from models.user_model import User
from models.pembelajaran_model import Pembelajaran
from models.tanggapan_model import Tanggapan
from models.pembayaran_model import Pembayaran

def create_all_tables():
    User.create_table()
    Pembelajaran.create_table()
    Tanggapan.create_table()
    Pembayaran.create_table()

if __name__ == '__main__':
    create_all_tables()