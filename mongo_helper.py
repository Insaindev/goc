#Operations guide https://www.w3schools.com/python/python_mongodb_insert.asp
#Installation https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x-tarball/
#mongoDb commands https://docs.mongodb.com/manual/reference/mongo-shell/
import pymongo
from bson.json_util import dumps
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://192.168.101.145:27017/")
mydb = myclient["braindb"]
goc_dev_coll = mydb["goc_dev"]
oracimg_test_coll = mydb["goc_img_test"]


def insertRow(row):
	#create one record into collection
# 	{
# 	"_id" : ObjectId("5f3cf9572ac7a83419cfce62"),
# 	"createdOn" : ISODate("2020-08-19T12:05:11.821Z"),
# 	"images" : [
# 		{
# 			"frameId" : ObjectId("5f3cf9572ac7a83419cfce5b"),
# 			"frameCounter" : "6",
# 			"class" : "person",
# 			"roi" : "[437, 82, 35, 86]",
# 			"hog" : "34020"
# 		},
# 		{
# 			"frameId" : ObjectId("5f3cf9572ac7a83419cfce5b"),
# 			"frameCounter" : "6",
# 			"class" : "person",
# 			"roi" : "[495, 78, 28, 84]",
# 			"hog" : "34020"
# 		},
# 		{
# 			"frameId" : ObjectId("5f3cf9572ac7a83419cfce5b"),
# 			"frameCounter" : "6",
# 			"class" : "person",
# 			"roi" : "[194, 102, 36, 89]",
# 			"hog" : "34020"
# 		},
# 		{
# 			"frameId" : ObjectId("5f3cf9572ac7a83419cfce5b"),
# 			"frameCounter" : "6",
# 			"class" : "person",
# 			"roi" : "[313, 107, 32, 78]",
# 			"hog" : "34020"
# 		},
# 		{
# 			"frameId" : ObjectId("5f3cf9572ac7a83419cfce5b"),
# 			"frameCounter" : "6",
# 			"class" : "person",
# 			"roi" : "[741, 123, 30, 63]",
# 			"hog" : "34020"
# 		},
# 		{
# 			"frameId" : ObjectId("5f3cf9572ac7a83419cfce5b"),
# 			"frameCounter" : "6",
# 			"class" : "person",
# 			"roi" : "[361, 254, 62, 153]",
# 			"hog" : "34020"
# 		},
# 		{
# 			"frameId" : ObjectId("5f3cf9572ac7a83419cfce5b"),
# 			"frameCounter" : "6",
# 			"class" : "person",
# 			"roi" : "[151, 269, 75, 167]",
# 			"hog" : "34020"
# 		},
# 		{
# 			"frameId" : ObjectId("5f3cf9572ac7a83419cfce5b"),
# 			"frameCounter" : "6",
# 			"class" : "person",
# 			"roi" : "[366, 262, 59, 163]",
# 			"hog" : "34020"
# 		}
# 	]
# }

	ins_row = goc_dev_coll.insert_one(row)
	return ins_row

def insertImgRow(imgRow):
	insimg_row = oracimg_test_coll.insert_one(imgRow)
	return insimg_row

def insertMany(rows):
	ins_manyrows = goc_dev_coll.insert_many(rows)
	return ins_manyrows

def insertImgMany(imgRows):
	ins_manyrows = oracimg_test_coll.insert_many(rows)
	return ins_manyrows
#create list of records into collection
# mylist = [
#   { "name": "Amy", "address": "Apple st 652"},
#   { "name": "Hannah", "address": "Mountain 21"},
#   { "name": "Michael", "address": "Valley 345"},
#   { "name": "Sandy", "address": "Ocean blvd 2"},
#   { "name": "Betty", "address": "Green Grass 1"},
#   { "name": "Richard", "address": "Sky st 331"},
#   { "name": "Susan", "address": "One way 98"},
#   { "name": "Vicky", "address": "Yellow Garden 2"},
#   { "name": "Ben", "address": "Park Lane 38"},
#   { "name": "William", "address": "Central st 954"},
#   { "name": "Chuck", "address": "Main Road 989"},
#   { "name": "Viola", "address": "Sideway 1633"}
# ]

	


def search_fulltext(searchQuery):
	myquery = { "$text": { "$search": searchQuery }}
	#searchResult = orac_test_coll.find(myquery,{"_id":0, "frameCounter":1})
	searchResult = goc_dev_coll.find(myquery,{"_id":0})
	return searchResult

def searchOne_fulltext(searchQuery):
	myquery = { "$text": { "$search": searchQuery }}
	#searchResult = orac_test_coll.find(myquery,{"_id":0, "frameCounter":1})
	searchResult = goc_dev_coll.find_one(myquery,{"_id":0})
	return searchResult

def search_regex(columnName, searchQuery):
	myquery = { columnName: { "$regex": searchQuery } }
	print(myquery)
	searchResult = goc_dev_coll.find(myquery)
	return searchResult

def searchimg_fulltext(searchQuery):
	myquery = { "$text": { "$search": searchQuery } }
	searchResult = oracimg_test_coll.find(myquery,{"_id":0, "imageID":1})
	return searchResult

def searchimg_fulltext_diskUse(searchQuery):
	#myquery = {'$text':{'$search': searchQuery}}, {'score': {'$meta': "textScore"}}
	#print('qqqqqq' + str(myquery))
	searchResult = goc_dev_coll.find({'$text':{'$search': searchQuery}}, {'score': {'$meta': 'textScore'}}).limit(10)#.sort(str({'score': {'$meta': 'textScore'}}),pymongo.ASCENDING)

	#searchResult.sort([("score",{"$meta": "textScore"})])
	return searchResult

def searchimg_regex(columnName, searchQuery):
	myquery = { columnName: { "$regex": searchQuery } }
	searchResult = oracimg_test_coll.find(myquery)
	return searchResult

def searching_within(arrayName, itemName, itemValue):
	myquery = { arrayName : {"$elemMatch":{itemName:itemValue} } }
	print(myquery)
	file1 = open("myquery.txt","w")
	file1.write(str(myquery))
	file1.close() 
		 
	searchResult = goc_dev_coll.find(myquery).limit(1)

	# Converting cursor to the list 
	# of dictionaries 
	list_cur = list(searchResult) 

	# Converting to the JSON 
	json_data = dumps(list_cur, indent = 2) 

	# Writing data to file data.json 
	with open('searchResult.json', 'w') as file: 
		file.write(json_data) 
	
	return searchResult

def searchingregx_within(arrayName, itemName, itemValue):
	myquery = { arrayName : {"$elemMatch":{itemName:{ "$regex": itemValue } } } }
	print(myquery)
	# file1 = open("myfile.txt","w")
	# file1.write(str(myquery))
	# file1.close() 
	searchResult = goc_dev_coll.find(myquery)
	return dumps(searchResult)

def searchingOne_within(arrayName, itemName, itemValue):
	myquery = { arrayName : {"$elemMatch":{itemName:itemValue} } }
	print(myquery)
	searchResult = goc_dev_coll.find_one(myquery)
	return searchResult

# goc functions

def getNotProcessedFrames(items_count):
    not_processed_frames = goc_dev_coll.find({"processed_flag":False}).limit(items_count)
    return not_processed_frames

def getbyframeid(image_id):
    objInstance = ObjectId(image_id)
    not_processed_frames = goc_dev_coll.find({"meta.fs_image_id": objInstance})
    return not_processed_frames

def setProcessed(image_id):
    objInstance = ObjectId(image_id)
    filter = {"meta.fs_image_id": objInstance}
    newvalues = { "$set": { "processed_flag": True } }
    
    goc_dev_coll.update_one(filter, newvalues)
    
