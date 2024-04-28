import pymongo
from results import result1,result2,result3
print("WELCOME TO PYMONGO")
client= pymongo.MongoClient("mongodb://localhost:27017")
print(client)
db = client["COMPANY_NAME_KEYWORD_RESULTS_DATABASE"]
collection = db["initial_collection"]
list1=["jasper.ai","copy.ai","anyword.com"]
list2=["flipkart.com","amazon.in","snapdeal.com"]
list3=["flipkart.com","amazon.in","snapdeal.com","meesho.com","myntra.com"]
sorted_list1 = sorted(list1)
sorted_list2 = sorted(list2)
sorted_list3 = sorted(list3)

initial_dict = [
    {"companynames": ", ".join(sorted_list1),
     "keywords": "", "results": result1},
    {"companynames": ", ".join(sorted_list2),
     "keywords": "", "results": result2},
    {"companynames": ", ".join(sorted_list3),
     "keywords": "", "results": result3}
]
collection.insert_many(initial_dict)

