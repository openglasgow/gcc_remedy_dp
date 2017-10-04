from util import *
import logging
import subprocess
from orm.models import *
import argparse
# Configure loggin
setup_logger('replication_logger', 'logs/replication.log', logging.INFO)
replication_logger = logging.getLogger('replication_logger')


### get results from db1
def batch_gen(start_n, end_n, batch_size=1000):
    remainder = (end_n -start_n) % batch_size
    diff_list = [batch_size for i in range(0, int((end_n-start_n-remainder)/batch_size))]
    batch_list = [((start_n + diff_list[i]*i), (start_n + diff_list[i]*i+batch_size-1)) for i in range(0, len(diff_list))]
    if remainder > 0:
        batch_list.append((batch_list[-1][1]+1, batch_list[-1][1]+remainder+1))
    else:
        batch_list[-1] = (batch_list[-1][0], batch_list[-1][1]+1)
    return(batch_list)


def replicate(start_n = 1, end_n = 10, batch_size = 1000, table=ArchiveCase):
    ### Get list of ids from db
    replication_logger.info("starting replication from local to remote db for table %s" % (table.__name__))
    ls = gen_session('local')
    rs = gen_session('remote')
    # generate slice indexes
    slice_indices = batch_gen(start_n, end_n, batch_size)
    # iterate through slice indices
    try:
        for batch_slice in slice_indices:
            replication_logger.info("replicating %s to %s of %s" % (batch_slice[0], batch_slice[1], end_n))
            # move slice index back to 0 if it starts at 1
            if batch_slice[0] == 1:
                batch_slice = (1, batch_slice[1])
            # query rows from slice
            rows = ls.query(table).order_by(table.id.asc()).slice(batch_slice[0], batch_slice[1]+1).all()
            # convert rows to dictionaries for persistence
            rows_dict = [row.__dict__ for row in rows]
            # generate remote session and add objects to it
            for row in rows_dict:
                for k in ['id', '_sa_instance_state']:
                    row.pop(k, None)
                replication_logger.debug(row['call_id'])
                rs.add(ArchiveCase(**row))
            rs.commit()
            replication_logger.info("successfully added %s to %s to remote db" % (batch_slice[0], batch_slice[1]))
    except: 
        e = sys.exc_info()[0]
        replication_logger.error(str(e))
    finally:
        replication_logger.info('*** all records replicated to remote db ***')
        ls.close()
        rs.close()
        return(True) 


if __name__ == "__main__":
    ### Open up tunnel
    try:
        pass
        #subprocess.call("./tunnel.sh")
    except:
        pass
        #replication_logger.error(str(sys.exc_info()[0]))

    print("Replicating from local to remote databse")
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", dest="start_n", required=True)
    parser.add_argument("-e", "--end", dest="end_n", required=True)
    parser.add_argument("-b", "--batchsize", dest="batch_size", required=True)
    parser.add_argument("-t", "--table", dest="table_name", required=True)
    args = parser.parse_args()
    ### update to handle many tables
    if args.table_name == "archive_cases":
        table = ArchiveCase
    print("Replicating... this may take a while...")
    replicate(int(args.start_n), int(args.end_n), int(args.batch_size), table)

