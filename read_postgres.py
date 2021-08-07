
from sqlalchemy import create_engine
import psycopg2

import datetime
import time 
import pandas as pd


import requests

import configparser

from src.withings_api_example import config

import json



CLIENT_ID = config.get('withings_api_example', 'client_id')
CUSTOMER_SECRET = config.get('withings_api_example', 'customer_secret')
STATE = config.get('withings_api_example', 'state')
ACCOUNT_URL = config.get('withings_api_example', 'account_withings_url')
WBSAPI_URL = config.get('withings_api_example', 'wbsapi_withings_url')
CALLBACK_URI = config.get('withings_api_example', 'callback_uri')





def get_refresh_token_from_postgres():

    # Setup connection to Postgres
    engine = create_engine("postgresql+psycopg2://postgres:mysecretpassword@192.168.4.143/withings")
    postgresSQLConnection = engine.connect()


    # Define SQL select statement for most recent item 
    sql = """select a.*
        FROM withings_cred a
        INNER JOIN (
        select max(time_stamp) as max_ts from withings_cred ) b
        ON a.time_stamp = b.max_ts
        """


    # Get value back and store in a variable
    cred_df = pd.read_sql(sql, postgresSQLConnection)


    # Assign to variable
    refresh_token = cred_df.iloc[0]['refresh_token']

    # Test that the variable works (status code?)

    # Close the connection
    postgresSQLConnection.close()

    print(f'Refresh Token:  {refresh_token}')

    #return variable
    return refresh_token



def get_measure_data_json(access_token):

    # Setup variables for urls
    # print(ACCOUNT_URL)
    # Send a request to go get the response
    
    headers_val = {'Authorization': 'Bearer ' + access_token}
    
    measure_payload = {
        "action":"getmeas"
        # "meastypes":[1,76],
        # "category":1,
    }

    r_getmeasure = requests.get(f'{WBSAPI_URL}/measure',
                               headers=headers_val,
                               params=measure_payload).json()
    

    return r_getmeasure





# For parsing JSON Files from Quicktype.io
############################################################################################################################
# imports from quicktype.io

from enum import Enum
from typing import Optional, Any, List, TypeVar, Callable, Type, cast


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


class Deviceid(Enum):
    F21604_BF3051_B109832_A7000_D5_EF8266_F51853_EA = "f21604bf3051b109832a7000d5ef8266f51853ea"
    THE_635_C2_EA718_C7_EF17_D89_F3874_AAF97_D8_B62642_C73 = "635c2ea718c7ef17d89f3874aaf97d8b62642c73"


class Measure:
    algo: Optional[int]
    fm: Optional[int]
    type: int
    unit: int
    value: int
    appliver: Optional[int]
    apppfmid: Optional[int]

    def __init__(self, algo: Optional[int], fm: Optional[int], type: int, unit: int, value: int, appliver: Optional[int], apppfmid: Optional[int]) -> None:
        self.algo = algo
        self.fm = fm
        self.type = type
        self.unit = unit
        self.value = value
        self.appliver = appliver
        self.apppfmid = apppfmid

    @staticmethod
    def from_dict(obj: Any) -> 'Measure':
        assert isinstance(obj, dict)
        algo = from_union([from_int, from_none], obj.get("algo"))
        fm = from_union([from_int, from_none], obj.get("fm"))
        type = from_int(obj.get("type"))
        unit = from_int(obj.get("unit"))
        value = from_int(obj.get("value"))
        appliver = from_union([from_int, from_none], obj.get("appliver"))
        apppfmid = from_union([from_int, from_none], obj.get("apppfmid"))
        return Measure(algo, fm, type, unit, value, appliver, apppfmid)

    def to_dict(self) -> dict:
        result: dict = {}
        result["algo"] = from_union([from_int, from_none], self.algo)
        result["fm"] = from_union([from_int, from_none], self.fm)
        result["type"] = from_int(self.type)
        result["unit"] = from_int(self.unit)
        result["value"] = from_int(self.value)
        result["appliver"] = from_union([from_int, from_none], self.appliver)
        result["apppfmid"] = from_union([from_int, from_none], self.apppfmid)
        return result


class Measuregrp:
    attrib: int
    category: int
    comment: None
    created: int
    date: int
    deviceid: Optional[Deviceid]
    grpid: int
    hash_deviceid: Optional[Deviceid]
    measures: List[Measure]

    def __init__(self, attrib: int, category: int, comment: None, created: int, date: int, deviceid: Optional[Deviceid], grpid: int, hash_deviceid: Optional[Deviceid], measures: List[Measure]) -> None:
        self.attrib = attrib
        self.category = category
        self.comment = comment
        self.created = created
        self.date = date
        self.deviceid = deviceid
        self.grpid = grpid
        self.hash_deviceid = hash_deviceid
        self.measures = measures

    @staticmethod
    def from_dict(obj: Any) -> 'Measuregrp':
        assert isinstance(obj, dict)
        attrib = from_int(obj.get("attrib"))
        category = from_int(obj.get("category"))
        comment = from_none(obj.get("comment"))
        created = from_int(obj.get("created"))
        date = from_int(obj.get("date"))
        deviceid = from_union([from_none, Deviceid], obj.get("deviceid"))
        grpid = from_int(obj.get("grpid"))
        hash_deviceid = from_union([from_none, Deviceid], obj.get("hash_deviceid"))
        measures = from_list(Measure.from_dict, obj.get("measures"))
        return Measuregrp(attrib, category, comment, created, date, deviceid, grpid, hash_deviceid, measures)

    def to_dict(self) -> dict:
        result: dict = {}
        result["attrib"] = from_int(self.attrib)
        result["category"] = from_int(self.category)
        result["comment"] = from_none(self.comment)
        result["created"] = from_int(self.created)
        result["date"] = from_int(self.date)
        result["deviceid"] = from_union([from_none, lambda x: to_enum(Deviceid, x)], self.deviceid)
        result["grpid"] = from_int(self.grpid)
        result["hash_deviceid"] = from_union([from_none, lambda x: to_enum(Deviceid, x)], self.hash_deviceid)
        result["measures"] = from_list(lambda x: to_class(Measure, x), self.measures)
        return result


class Body:
    measuregrps: List[Measuregrp]
    timezone: str
    updatetime: int

    def __init__(self, measuregrps: List[Measuregrp], timezone: str, updatetime: int) -> None:
        self.measuregrps = measuregrps
        self.timezone = timezone
        self.updatetime = updatetime

    @staticmethod
    def from_dict(obj: Any) -> 'Body':
        assert isinstance(obj, dict)
        measuregrps = from_list(Measuregrp.from_dict, obj.get("measuregrps"))
        timezone = from_str(obj.get("timezone"))
        updatetime = from_int(obj.get("updatetime"))
        return Body(measuregrps, timezone, updatetime)

    def to_dict(self) -> dict:
        result: dict = {}
        result["measuregrps"] = from_list(lambda x: to_class(Measuregrp, x), self.measuregrps)
        result["timezone"] = from_str(self.timezone)
        result["updatetime"] = from_int(self.updatetime)
        return result


class Welcome:
    body: Body
    status: int

    def __init__(self, body: Body, status: int) -> None:
        self.body = body
        self.status = status

    @staticmethod
    def from_dict(obj: Any) -> 'Welcome':
        assert isinstance(obj, dict)
        body = Body.from_dict(obj.get("body"))
        status = from_int(obj.get("status"))
        return Welcome(body, status)

    def to_dict(self) -> dict:
        result: dict = {}
        result["body"] = to_class(Body, self.body)
        result["status"] = from_int(self.status)
        return result


def welcome_from_dict(s: Any) -> Welcome:
    return Welcome.from_dict(s)


def welcome_to_dict(x: Welcome) -> Any:
    return to_class(Welcome, x)


############################################################################################################################
############################################################################################################################
# End of Quicktype.io 
############################################################################################################################



def write_df_to_postgres(data_frame, table_name):

    engine = create_engine("postgresql+psycopg2://postgres:mysecretpassword@192.168.4.143/withings")
    postgresSQLConnection = engine.connect()

    try:
        data_frame.to_sql(table_name, postgresSQLConnection, if_exists='append')

    except ValueError as vx:

        print(vx)

    except Exception as ex:  

        print(ex)

    else:
        print("PostgreSQL Table %s has been created successfully."%table_name)

    finally:
        postgresSQLConnection.close()




def parse_measure_data_to_df(measure_json):

    # Parse logic
    result = welcome_from_dict(measure_json)
    # result = welcome_from_dict(json.loads(measure_json))

    full_getmeasurse_dict = welcome_to_dict(result)

    measure_df = pd.DataFrame(full_getmeasurse_dict['body']['measuregrps'])

        
    temp_df = pd.DataFrame()
    line_df = pd.DataFrame()


    for index, row in measure_df.iterrows():
        
        # Get values of header
        attrib = row['attrib']
        category = row['category']
        comment = row['comment']
        created = row['created']
        date =  row['date']
        deviceid = row['deviceid']
        grpid = row['grpid']
        hash_deviceid = row['hash_deviceid']
        
        

        temp_df = pd.DataFrame(measure_df.loc[index]['measures'])
        
        temp_df['grpid'] = grpid
        temp_df['attrib'] = row['attrib']
        
        temp_df['category'] = row['category']
        temp_df['comment'] = row['comment']
        temp_df['created'] = row['created']
        temp_df['date'] =  row['date']
        temp_df['deviceid'] = row['deviceid']
        temp_df['hash_deviceid'] = row['hash_deviceid']
        
        
        line_df = line_df.append(temp_df)

    line_df['updatetime'] = full_getmeasurse_dict['body']['updatetime']
    line_df['timezone'] = full_getmeasurse_dict['body']['timezone']

    return line_df



def get_sleep_data_json(access_token):
    
    headers_val = {'Authorization': 'Bearer ' + access_token}



    startdate = time.mktime(datetime.datetime(2021,8,1,0,0).timetuple())
    enddate = time.mktime(datetime.datetime.now().timetuple())


    sleep_payload = {
        "action":"get",
        "startdate": startdate,
        "enddate": enddate,
        "data_fields":"hr,rr,snoring"
    }

    r_sleep = requests.post(f'{WBSAPI_URL}/v2/sleep', 
                               headers=headers_val,
                               params=sleep_payload).json()
    
    return r_sleep




def get_sleep_summary_data_json(access_token):
    
    headers_val = {'Authorization': 'Bearer ' + access_token}



    startdate = datetime.datetime(2021,8,1)
    enddate = datetime.datetime.now().date()


    sleep_payload = {
        "action":"getsummary",
        "startdateymd": str(startdate),
        "enddateymd": str(enddate)
        # "data_fields":"hr,rr,snoring"
    }

    r_sleep_summary = requests.post(f'{WBSAPI_URL}/v2/sleep', 
                               headers=headers_val,
                               params=sleep_payload).json()
    
    return r_sleep_summary



def refresh_access_token(refresh_token):

    params = {"action":"requesttoken",
            "client_id":CLIENT_ID,
            "client_secret":CUSTOMER_SECRET,
            "grant_type":"refresh_token",
            "refresh_token": refresh_token}

    print(f'Old Access Token used: {refresh_token}')
    r_new_access_token = requests.post(f'{WBSAPI_URL}/v2/oauth2', params=params).json()


    refresh_dict = {
        "grant_type":params["grant_type"],
        "client_id":params["client_id"],
        "client_secret":params["client_secret"],
        "code":"N/A",
        "redirect_uri":"N/A",
        "auth_code":"N/A",
        "state":"N/A",
        "access_token":r_new_access_token['body']['access_token'],
        "refresh_token":r_new_access_token['body']['refresh_token'],
        "userid":r_new_access_token['body']['userid'],
        "scope":r_new_access_token['body']['scope'],
        "time_stamp":datetime.datetime.now()
    }

    withings_cred_df = pd.DataFrame(refresh_dict,index=[0])

    write_df_to_postgres(withings_cred_df, 'withings_cred')

    return r_new_access_token['body']['access_token']
















def get_measure_data_json(access_token):

    # Setup variables for urls
    # print(ACCOUNT_URL)
    # Send a request to go get the response
    
    headers_val = {'Authorization': 'Bearer ' + access_token}
    



    measure_payload = {
        "action":"getmeas"
        # "meastypes":[1,76],
        # "category":1,
    }

    r_getmeasure = requests.get(f'{WBSAPI_URL}/measure',
                               headers=headers_val,
                               params=measure_payload).json()
    

    return r_getmeasure










if __name__ == "__main__":

    refresh_token = get_refresh_token_from_postgres()

    new_access_token = refresh_access_token(refresh_token)
    
    print(new_access_token)

    # Get the measure data and write to postgres
    r_measure = get_measure_data_json(new_access_token)
    
    # print(type(r_measure))
    # r_measure_str = str(r_measure)
        
    # # test = json.loads(r_measure)
    # r_measure_str = r_measure_str.replace("\'", "\"")
    # # print(type(test))


    measure_df = parse_measure_data_to_df(r_measure)

    write_df_to_postgres(measure_df, 'measures')

    r_sleep_summary = get_sleep_summary_data_json(new_access_token)
    print(r_sleep_summary)

    r_sleep = get_sleep_data_json(new_access_token)
    # print(r_sleep)    







    # try:
    #     data_frame.to_sql(table_name, postgresSQLConnection, if_exists='append')

    # except ValueError as vx:

    #     print(vx)

    # except Exception as ex:  

    #     print(ex)

    # else:
    #     print("PostgreSQL Table %s has been created successfully."%table_name)

    # finally:
    #     postgresSQLConnection.close()

