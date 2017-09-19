from orm.models import *
from orm.orm import db_connect, create_tables
from sqlalchemy.orm import sessionmaker
#import datetime

## Set up metadata
md = Base.metadata

def write_schema(md):
    with open('../schema.txt', 'w') as f:
        f.write("*** WB Schema at {0} \n------------------------\n\n".format(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")))
        for table in md.sorted_tables:
            f.write("{0}:\n".format(table))
            for column in table.c:
                fk = ", {0}".format(list(column.foreign_keys)[0]) if len(column.foreign_keys) > 0 else ""
                pk = ", primary_key" if column.primary_key == True else ""
                f.write("\t{0}, :{1}{2}{3}\n".format(column.name, column.type,fk,pk))



