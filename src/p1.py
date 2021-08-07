import datetime
import time


var = datetime.datetime.now()
unix_datetime = time.mktime(var.timetuple())
print(int(unix_datetime))