
import datetime

class Psi_Message:

    def __init__(self):
        self.num_mess = 0
        self.date_fmt = "%a %b %d %Y:%I:%M:%S %p"

        return

    def debug(self, id_str: str, msg: str):
        date_time = datetime.datetime.now().strftime(self.date_fmt)
        print(f'{date_time} : DEBUG : {id_str} : {msg}')

        return

    def error(self, id_str: str, msg: str):
        date_time = datetime.datetime.now().strftime(self.date_fmt)
        print(f'{date_time} : ERROR : {id_str} : {msg}')

        return















