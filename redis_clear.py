from database.redis_db import r
r.set('table1_last_num', 0)
r.set('table1_trash_last_num', 0)
r.set('table2_last_num', 0)
