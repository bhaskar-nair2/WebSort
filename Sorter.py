from openpyxl import load_workbook
import sqlite3 as sql

db = 'static/data/SearchDB'


class Sort:
    def __init__(self, file):
        self.file = load_workbook(file)


# noinspection SqlResolve
class ReDataMaker:
    def __init__(self, file, pa_count, updater):
        self.file = load_workbook(file)
        try:
            con = sql.connect(db, isolation_level=None)
            self.cur = con.cursor()
        except sql.OperationalError as e:
            print(f'Error in init: {e}')
        self.pa_count = pa_count
        self.tblN = ['paSearchList', 'rcSearchList']
        self.updater = updater

    def refresh(self):
        tbl_set = 0
        self.clear_db(self.tblN)
        for sheet_index in range(len(self.file.sheetnames)):
            self.file._active_sheet_index = sheet_index
            sheet = self.file.active
            if not sheet_index < self.pa_count:
                tbl_set = 1
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
                value = [contract_lst[_].value, name_lst[_].value, unit_lst[_].value, coy_lst[_].value,
                         rate_lst[_].value, gst_lst[_].value, supplier_lst[_].value]
                self.insert(self.tblN[tbl_set], value)
            self.updater.put(sheet_index / len(self.file.sheetnames))

    def clear_db(self, tbl):
        try:
            for _ in tbl:
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
