import sqlite3 as sql


con = sql.connect('static/data/SearchDB', isolation_level=None)
cur = con.cursor()


cur.execute("drop view final_list")

cur.execute("create view IF NOT EXISTS final_list \
  [] as \
   select * from indentList i, gpaSearchList p \
      where i.alias = p.name")

rs = cur.execute("select * from final_list")

for r in rs:
    print(r)


COP_FORMAT = ["S NO", "INDENT S NO", "NOMENCLATURE", "A/U",	"DEMAND"]
