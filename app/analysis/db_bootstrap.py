from app.DataBase import micro_msg_db, msg_db


def init_local_db():
    msg_db.init_database(path='../DataBase/Msg/MSG.db')
    micro_msg_db.init_database(path="../DataBase/Msg/MicroMsg.db")