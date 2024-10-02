from decouple import config

USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")
HOST = config("HOST")
DATABASE = config("DATABASE")


config_dict: dict[str, str] = {
    "user": USERNAME,
    "password": PASSWORD,
    "host": HOST,
    "database": DATABASE,
}
