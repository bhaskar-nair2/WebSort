from openpyxl import load_workbook, Workbook
import sqlite3 as sql
from re import sub
from datetime import date
from queue import Queue

db = 'static/data/SearchDB'
waste_list = ['tab', 'mg']


def cleaner(val):
    val = val.lower().strip()
    for _ in waste_list:
        val = val.replace(_, '').strip()
        val = sub(r'[(\[].+?[)\]]', '', val)
    return val.replace(' ', '')


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
        self.columns = ['Indent No', 'Contract No', "Nomenclature",
                        "Unit", "Company", "Rate", "Quantity", "Amount", "Supplier", 'from_date', "to_date"]

    def createData(self):
        pass

    def data_gen(self):
        self.status.put('Sorting Starts!!!')
        self.clear_db()
        self.file._active_sheet_index = 0
        sheet = self.file.active
        indref_lst = sheet['B'][1:]
        name_lst = sheet['C'][1:]
        qty_lst = sheet['E'][1:]
        for _ in range(len(name_lst)):
            if _ % 50 == 0 or _ == len(name_lst):
                self.status.put(f"Done about {round(_/len(name_lst)*100)}%")
            if name_lst[_].value is None:
                break
            value = [indref_lst[_].value, str(name_lst[_].value).lower().strip(),
                     cleaner(str(name_lst[_].value)),
                     qty_lst[_].value,
                     ]
            self.insert(value)
        self.status.put('Insertion Done!!')
        self.create_views()
        return self.file_gen()

    def file_gen(self):
        today = date.today()
        wb = Workbook()
        views = [{'ref': 'mrc_view', 'table': 'rc'},
                 {'ref': 'gpa_view', 'table': 'gpa'},
                 {'ref': 'spa_view', 'table': 'spa'}]
        try:
            for view in views:
                ws = wb.create_sheet(f"{view['table']}-{today}", 0)
                rs_found = self.cur.execute(
                    f"select * from {view['ref']} order by name")
                ws.append(self.columns)
                for _ in rs_found.fetchall():
                    ws.append(_)
        except sql.OperationalError as e:
            print(self.__class__, f"Error{e}")

        # Not found
        ws = wb.create_sheet("Not Found", 0)
        ws.append(['', 'ITEMS NOT FOUND', ''])
        ws.append(self.columns)
        rs_not_found = self.cur.execute('select indref,name from not_found;')
        for _ in rs_not_found:
            ws.append(_)

        # Create File
        filename = f"created{date.today()}.xlsx"
        filepath = './static/uploads/' + filename
        wb.save(filepath)
        self.status.put(f':{filepath}:')
        self.status.put('File Created!')
        return filepath

    def clear_db(self):
        que = f"delete from {self.tbl_name}"
        try:
            self.cur.execute(que)
        except sql.OperationalError:
            pass

    def insert(self, values):
        que = f"insert into {self.tbl_name} (indref, name, alias, qty) values(?,?,?,?)"
        try:
            self.cur.execute(que, values)
        except sql.OperationalError as e:
            print(self.__class__, f"Error{e}")
            q = f"""create table {self.tbl_name} (indref varchar(200),name varchar(200), alias varchar(200),qty int)"""
            self.cur.execute(q)
            self.cur.execute(que, values)
            pass

    def create_views(self):
        self.status.put('Creating Views')
        views = [
            {'ref': 'mrc_view', 'table': 'rc', 'extra': True},
            {'ref': 'gpa_view', 'table': 'gpa', 'extra': False},
            {'ref': 'spa_view', 'table': 'spa', 'extra': False}
        ]
        for view in views:
            cols = "i.indref, g.contract, i.name, g.unit, g.coy, g.rate, i.qty, g.gst, g.supplier"
            if(view['extra'] == True):
                cols += ", g.to_date, g.from_date "
            que = f"""CREATE view {view['ref']} as
            select {cols}
            from {view['table']}SearchList g, indentList i
            WHERE g.name like "%"||i.name||"%" 
            or g.alias like "%"||i.alias||"%" 
            or i.name like "%"||g.name||"%" 
            or i.alias like "%"||g.alias||"%";"""
            try:
                print(que)
                self.cur.execute(que)
                self.status.put('Views Ready')
            except sql.OperationalError as e:
                print(self.__class__, f"Error: {e}")
                self.drop(view['ref'], 'view')
                self.cur.execute(que)
                pass
            self.status.put('Views Ready')
            # Not Found
        self.not_found_view()

    def not_found_view(self):
        self.status.put('Making Not Found')
        try:
            que = f"""CREATE view not_found as 
                select i.indref, i.name  
                from indentList i 
                WHERE indref not in (select indref from mrc_view) 
                and indref not in (select indref from spa_view) 
                and indref not in (select indref from gpa_view);"""
            self.cur.execute(que)
        except sql.OperationalError as e:
            self.cur.execute(f"drop view not_found")
            self.cur.execute(que)
        self.status.put('Not Found Ready')

    def drop(self, name, type):
        try:
            self.cur.execute(f"drop {type} {name}")
        except sql.OperationalError as e:
            print(f"Delete Error: {e}")
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
        rcTab = False
        for sheet_index in range(0, len(self.file.sheetnames)):
            self.file._active_sheet_index = sheet_index
            self.status.put(
                f"Now Inserting {self.file.sheetnames[self.file._active_sheet_index]} into Database")
            sheet = self.file.active
            if not sheet_index < self.pa_count[tbl_set]:
                tbl_set += 1
            if(self.tblN[tbl_set] == 'rcSearchList'):
                rcTab = True
            contract_lst = sheet['C'][1:]
            name_lst = sheet['D'][1:]
            unit_lst = sheet['E'][1:]
            coy_lst = sheet['F'][1:]
            rate_lst = sheet['G'][1:]
            gst_lst = sheet['J'][1:]
            supplier_lst = sheet['L'][1:]
            if(rcTab):
                to_lst = sheet['M'][1:]
                fr_lst = sheet['N'][1:]
            for _ in range(len(contract_lst)):
                if contract_lst[_].value is None:
                    break
                value = [contract_lst[_].value,
                         str(name_lst[_].value).lower().strip(),
                         cleaner(str(name_lst[_].value)),
                         unit_lst[_].value,
                         coy_lst[_].value,
                         rate_lst[_].value,
                         gst_lst[_].value,
                         str(supplier_lst[_].value).replace('\n', '')]
                if(rcTab):
                    value.append(to_lst[_].value)
                    value.append(fr_lst[_].value)
                self.insert(self.tblN[tbl_set], value, rcTab)
        self.status.put('Refresh Done!!')

    def clear_db(self):
        try:
            for _ in self.tblN:
                que = f"Delete from {_}"
                self.cur.execute(que)
        except sql.OperationalError:
            print('Error IN deletion')

    def insert(self, tbl, values, rcTab):
        if(rcTab):
            que = f"insert into {tbl} (contract, name, alias, unit, coy, rate, gst, supplier, to_date, from_date) values (?,?,?,?,?,?,?,?,?,?)"
        else:
            que = f"insert into {tbl} (contract, name, alias, unit, coy, rate, gst, supplier) values (?,?,?,?,?,?,?,?)"
        try:
            self.cur.execute(que, values)
            print(
                f"Inserting into {tbl} with {values[0]},{values[1]},{values[6]}")
        except sql.OperationalError as e:
            print(e)
            if(rcTab):
                re = f"""create table {tbl} (
                            contract varchar(20),
                            name     varchar(200) not null,
                            alias    varchar(200) not null,
                            unit     varchar(20),
                            coy      varchar(30),
                            rate     int default 0,
                            gst      int default 12,
                            supplier varchar(50),
                            to_date varchar(50),
                            from_date varchar(50),
                            primary key (contract,supplier)
                            )"""
            else:
                re = f"""create table {tbl} (
                            contract varchar(20),
                            name     varchar(200) not null,
                            alias    varchar(200) not null,
                            unit     varchar(20),
                            coy      varchar(30),
                            rate     int default 0,
                            gst      int default 12,
                            supplier varchar(50),
                            primary key (contract,supplier)
                            )"""
            self.cur.execute(re)
            self.cur.execute(que, values)
        except Exception as e:
            print(self.__class__, f"Error{e}")
            pass
