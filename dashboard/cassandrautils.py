import datetime
import gzip
import os
import re
import sys

import pandas as pd
from cassandra.cluster import BatchStatement, Cluster, ConsistencyLevel
from cassandra.query import dict_factory

weathertable = os.getenv("weather.table", "weatherreport")
fakertable = os.getenv("faker.table", "fakerdata")
binancetable = os.getenv("binance.table", "binancedata")


CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get("CASSANDRA_HOST") else 'localhost'
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get("CASSANDRA_KEYSPACE") else 'kafkapipeline'

WEATHER_TABLE = os.environ.get("WEATHER_TABLE") if os.environ.get("WEATHER_TABLE") else 'weather'
FAKER_TABLE = os.environ.get("FAKER_TABLE") if os.environ.get("FAKER_TABLE") else 'faker'
BINANCE_TABLE = os.environ.get("BINANCE_TABLE") if os.environ.get("BINANCE_TABLE") else 'binance'

def saveFakerDf(dfrecords):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    session = cluster.connect(CASSANDRA_KEYSPACE)

    counter = 0
    totalcount = 0

    cqlsentence = "INSERT INTO " + fakertable + " (username, name, email, phone_number, address, company, job, license_plate, year, safe_color_name) \
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    insert = session.prepare(cqlsentence)
    batches = []
    for idx, val in dfrecords.iterrows():
        batch.add(insert, (val['username'], val['name'], val['email'],val['phone_number'],
                           val['address'], val['company'], val['job'],
                           val['license_plate'], val['year'], val['safe_color_name']))
        counter += 1
        if counter >= 100:
            print('inserting ' + str(counter) + ' records')
            totalcount += counter
            counter = 0
            batches.append(batch)
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    if counter != 0:
        batches.append(batch)
        totalcount += counter
    rs = [session.execute(b, trace=True) for b in batches]

    print('Inserted ' + str(totalcount) + ' rows in total')

def saveWeatherreport(dfrecords):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    session = cluster.connect(CASSANDRA_KEYSPACE)

    counter = 0
    totalcount = 0

    cqlsentence = "INSERT INTO " + weathertable + " (forecastdate, location, description, temp, feels_like, temp_min, temp_max, pressure, humidity, wind, sunrise, sunset) \
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    insert = session.prepare(cqlsentence)
    batches = []
    for idx, val in dfrecords.iterrows():
        batch.add(insert, (val['report_time'], val['location'], val['description'],
                           val['temp'], val['feels_like'], val['temp_min'], val['temp_max'],
                           val['pressure'], val['humidity'], val['wind'], val['sunrise'], val['sunset']))
        counter += 1
        if counter >= 100:
            print('inserting ' + str(counter) + ' records')
            totalcount += counter
            counter = 0
            batches.append(batch)
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    if counter != 0:
        batches.append(batch)
        totalcount += counter
    rs = [session.execute(b, trace=True) for b in batches]

    print('Inserted ' + str(totalcount) + ' rows in total')


def saveBinanceDf(dfrecords):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    session = cluster.connect(CASSANDRA_KEYSPACE)

    counter = 0
    totalcount = 0

    cqlsentence = "INSERT INTO " + binancetable + " (datetime, pair, open_price, close_price, high_price, low_price, volume, trades) \
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    insert = session.prepare(cqlsentence)
    batches = []
    for idx, val in dfrecords.iterrows():
        batch.add(insert, (val['datetime'], val['pair'], val['open_price'],
                           val['close_price'], val['high_price'], val['low_price'], val['volume'], val['trades']))
        counter += 1
        if counter >= 100:
            print('inserting ' + str(counter) + ' records')
            totalcount += counter
            counter = 0
            batches.append(batch)
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    if counter != 0:
        batches.append(batch)
        totalcount += counter
    rs = [session.execute(b, trace=True) for b in batches]

    print('Inserted ' + str(totalcount) + ' rows in total')

def loadDF(targetfile, target):
    if target == 'weather':
        colsnames = ['description', 'temp', 'feels_like', 'temp_min', 'temp_max',
                     'pressure', 'humidity', 'wind', 'sunrise', 'sunset', 'location', 'report_time']
        dfData = pd.read_csv(targetfile, header=None,
                             parse_dates=True, names=colsnames)
        dfData['report_time'] = pd.to_datetime(dfData['report_time'])
        saveWeatherreport(dfData)
    elif target == 'faker':
        colsnames = ['username', 'name', 'email', 'phone_number', 'address',
                     'company', 'job', 'license_plate', 'year', 'safe_color_name']
        dfData = pd.read_csv(targetfile, header=None,
                             parse_dates=True, names=colsnames)
        saveFakerDf(dfData)
    elif target == 'binance':
        colsnames = ['datetime', 'pair', 'open_price', 'close_price',
                     'high_price', 'low_price', 'volume', 'trades']
        dfData = pd.read_csv(targetfile, header=None,
                             parse_dates=True, names=colsnames)
        dfData['datetime'] = pd.to_datetime(dfData['datetime'])
        saveBinanceDf(dfData)


def getWeatherDF():
    return getDF(WEATHER_TABLE)
def getFakerDF():
    return getDF(FAKER_TABLE)
def getBinanceDF():
    return getDF(BINANCE_TABLE)

def getDF(source_table):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    if source_table not in (WEATHER_TABLE, FAKER_TABLE, BINANCE_TABLE):
        return None

    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory
    cqlquery = "SELECT * FROM " + source_table + ";"
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    action = sys.argv[1]
    target = sys.argv[2]
    targetfile = sys.argv[3]
    if action == "save":
        loadDF(targetfile, target)
    elif action == "get":
        getDF(target)