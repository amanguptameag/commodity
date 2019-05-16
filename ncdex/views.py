from django.shortcuts import render
import pymongo
import json
import time
import datetime
from pytz import timezone
from bson import json_util, ObjectId
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.core import serializers
from bson import ObjectId
from django.http import Http404

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["commodity_insights"]
mycol = mydb["ncdex"]


def index(request):
    #print(request.GET)

    commodity = request.GET.get('commodity')
    commodity = commodity.upper()
    loc = request.GET.get('city')
    loc = loc[0].upper() + loc[1:]
    day = request.GET.get('days')
    day = int(day)

    myquery = {"commodity": commodity, "location": loc }

    list = mycol.find(myquery).sort("date", -1).limit(day)

    # for object in list:
    #     a = object
    #     print('_id',a.get('_id'))
    #     print('commodity',a.get('commodity'))
    #     print('date',a.get('date'))
    #     print('location',a.get('location'))
    #     print('num_readings',a.get('num_readings'))
    #     print('prices',a.get('prices'))
    #     print()

    json_doc = []
    prices_dic = {}

    for doc in list:
        ####################################################################
        #For updatation of timestamp
        date = doc.get("date")
        date = date.split("-")
        start_time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))

        prices = doc.get("prices")
        num_readings = doc.get("num_readings")
        min = 0

        #for storing the time into the list
        time = []
        for key in prices:
            time.append(int(key))

        for key in time:
            new_time = start_time + datetime.timedelta(minutes = key)
            new_timestamp = int(new_time.timestamp())
            prices[str(new_timestamp)] = prices[str(key)]
            del prices[str(key)]

        for i in prices:
            prices_dic[i] = prices[i]
        #print(prices_dic)

        # json_doc.append(doc)
        #
        # #Changing the key name
        # doc['id'] = doc['_id']
        # del doc['_id']
        #
        # #Changing the value format of id
        # id = doc.get("id")
        # doc["id"] = str(id)

    data_dict = {}
    data_dict["commodity"] = commodity
    data_dict["location"] = loc
    data_dict["prices"] = prices_dic
    #print(data_dict)

    json_docs = {"data":data_dict}
    data = json.loads(json_util.dumps(json_docs))

    # india = timezone('Asia/Kolkata')
    # now = datetime.datetime.now(india)
    # print(now)
    # start_time = datetime.datetime(2020, 5, 17)
    # print(start_time)
    # nextTime = start_time + datetime.timedelta(minutes = 15)
    # print(nextTime)

    return JsonResponse(data)
