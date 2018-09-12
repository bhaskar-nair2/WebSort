from openpyxl import load_workbook
import sqlite3 as sql
from queue import Queue

db = 'static/data/SearchDB'
waste_list = ['inj', 'tab', 'cap', 'inhaler', 'respules', 'rotacaps', 'syp', 'eye', 'drop', 'lotion', 'oint', 'alpha',
              'tap', '/', '%', '(', ')', '-']


def cleaner(val):
    for _ in waste_list:
        val = val.replace(_, '').strip()
    return val


class IdDataMaker:
    def __init__(self, file, queue):
        self.file = load_workbook(file)
        try:
            con = sql.connect(db, isolation_level=None)
            self.cur = con.cursor()
        except sql.OperationalError as e:
            print(self.__class__, f"Error {e}")

        self.tbl_name = 'indentList'
        self.status = queue

    def data_gen(self):
        self.status.put('Sorting Starts!!!')
        self.clear_db()
        self.file._active_sheet_index = 0
        sheet = self.file.active
        name_lst = sheet['C'][1:]
        qty_lst = sheet['F'][1:]
        for _ in range(len(name_lst)):
            if _ % 50 == 0 or _ == len(name_lst):
                self.status.put(f'Done about {round(_/len(name_lst)*100)}%')
            if name_lst[_].value is None:
                break
            value = [str(name_lst[_].value.lower().strip()),
                     cleaner(str(name_lst[_].value).lower().strip()).replace(' ', ''), qty_lst[_].value]
            self.insert(value)
        self.status.put('Insertion Done!!')
        self.status.put('Sorting Done!!')

    def clear_db(self):
        que = f"delete from {self.tbl_name}"
        try:
            self.cur.execute(que)
        except sql.OperationalError:
            pass

    def insert(self, values):
        que = f"insert into {self.tbl_name} (name, alias, qty) values(?,?,?)"
        try:
            self.cur.execute(que, values)
        except sql.OperationalError as e:
            print(self.__class__, f"Error{e}")
            q = f"""create table {self.tbl_name} (name varchar(200), alias varchar(200),qty int)"""
            self.cur.execute(q)
            self.cur.execute(que, values)
            pass


class ReDataMaker:
    def __init__(self, file, queue, *args):
        self.file = load_workbook(file)
        try:
            con = sql.connect(db, isolation_level=None)
            self.cur = con.cursor()
        except sql.OperationalError as e:
            print(f'Error in init: {e}')
        self.pa_count = args
        self.tblN = ['gpaSearchList', 'spaSearchList', 'rcSearchList']
        self.status = queue

    def refresh(self):
        self.status.put(f"Refresh Starts!")
        tbl_set = 0
        self.clear_db()
        for sheet_index in range(0, len(self.file.sheetnames)):
            self.file._active_sheet_index = sheet_index
            self.status.put(f"Now Inserting {self.file.sheetnames[self.file._active_sheet_index]} into Database")
            sheet = self.file.active
            if not sheet_index < self.pa_count[tbl_set]:
                tbl_set += 1
            contract_lst = sheet['B'][1:]
            name_lst = sheet['C'][1:]
            unit_lst = sheet['D'][1:]
            coy_lst = sheet['E'][1:]
            rate_lst = sheet['F'][1:]
            gst_lst = sheet['G'][1:]
            supplier_lst = sheet['H'][1:]
            for _ in range(len(contract_lst)):
                if contract_lst[_].value is None:
                    break
                value = [contract_lst[_].value, cleaner(str(name_lst[_].value).lower().strip()).replace(' ', ''),
                         unit_lst[_].value,
                         coy_lst[_].value,
                         rate_lst[_].value, gst_lst[_].value, supplier_lst[_].value]
                self.insert(self.tblN[tbl_set], value)
        self.status.put('Refresh Done!!')

    def clear_db(self):
        try:
            for _ in self.tblN:
                que = f"Delete from {_}"
                self.cur.execute(que)
        except sql.OperationalError:
            print('Error IN deletion')

    def insert(self, tbl, values):
        try:
            que = f"insert into {tbl} (contract, name, unit, coy, rate, gst, supplier) values (?,?,?,?,?,?,?)"
            try:
                self.cur.execute(que, values)
                print(f"Inserting into {tbl} with {values[0]},{values[1]},{values[6]}")
            except sql.IntegrityError as e:
                print(e, f"Error In {values[0]},{values[1]},{values[6]}")
                pass
        except sql.OperationalError:
            que = f"""create table {tbl} (
                        contract varchar(20),
                        name     varchar(200) not null,
                        unit     varchar(20),
                        coy      varchar(30),
                        rate     int default 0,
                        gst      int default 12,
                        supplier varchar(50),
                        primary key (contract,supplier)
                        )"""
            self.cur.execute(que)
            que = f"insert into {tbl} (contract, name, unit, coy, rate, gst, supplier) values (?,?,?,?,?,?,?)"
            self.cur.execute(que, values)
