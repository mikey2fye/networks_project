from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def mongo_client():
    """ Set Up MongoDB Client """

    db_username = "canicolas"
    db_password = "BlRvmec6R0JzqXM3"
    uri = f"mongodb+srv://{db_username}:{db_password}@cluster0.8gcptj9.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return client

def create_or_update_node(ip_node, node_collection):
    
    ip = ip_node["ip"]
    links = ip_node["links"]

    node_id = node_collection.find_one({"ip": ip})

    if node_id is not None:

        filter = {"ip": ip}

        update_data = {
            "$addToSet": {
                "links": {
                    "$each": links
                }
            }
        }
        node_collection.update_one(filter, update_data)
    
    else:

        node_id = node_collection.insert_one(ip_node).inserted_id
