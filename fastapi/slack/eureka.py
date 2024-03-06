from py_eureka_client import eureka_client
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import os
import requests
import xml.etree.ElementTree as ET
from slack.keycloak import oauth2_scheme
from fastapi import Depends
import json
import xmltodict 
from py_eureka_client.eureka_client import EurekaClient
import logging
 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 
 
load_dotenv()

EUREKA_SERVER = os.getenv("EUREKA_SERVER")
APP_NAME = os.getenv("APP_NAME")
SLACK_PORT= os.getenv("SLACK_PORT")
OTHER_SERVICE_NAME = os.getenv("OTHER_SERVICE_NAME")
EUREKA_SERVER_INSTANCES = os.getenv("EUREKA_SERVER_INSTANCES")
PUBLIC_IP = os.getenv("PUBLIC_IP", "0.0.0.0") 
OTHER_SERVICE_URL=os.getenv("OTHER_SERVICE_URL")
router = APIRouter(
    prefix='/slack',
    tags=['slack']
)

client = None

async def startup_event():
    global client
    try:
        client = EurekaClient(
            eureka_server=EUREKA_SERVER,
            app_name=APP_NAME,
            instance_port=int(SLACK_PORT),
            instance_ip=PUBLIC_IP
        )
        await client.start()
    except Exception as e:
        # Handle initialization errors
        print(f"Error during startup: {e}")

async def shutdown_event():
    if client:
        try:
            await client.stop()
        except Exception as e:
            # Handle shutdown errors
            print(f"Error during shutdown: {e}")



@router.get("/get_other")
async def get_other(token: str = Depends(oauth2_scheme)):
    try:
        # Check if the client has been initialized
        if client is None:
            raise HTTPException(status_code=500, detail="Client not initialized")
        
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'} 
        res = await client.do_service(OTHER_SERVICE_NAME, OTHER_SERVICE_URL, headers=headers)
        json_res = json.loads(res)
        return {"Response of other microservice": json_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



















# async def startup_event():
#     await eureka_client.init_async(eureka_server=EUREKA_SERVER,
#                                    app_name=APP_NAME,
#                                    instance_port=int(SLACK_PORT),
#                                    instance_ip=PUBLIC_IP
#                                     )
    
# async def shutdown_event():
#     await eureka_client.fini_async()

# @router.on_event("startup")
# async def startup():
#     await startup_event()


# @router.on_event("shutdown")
# async def shutdown():
#     await shutdown_event()


# # Endpoint to provide POSTS URL

# @router.get("/get_other")
# def get_other(token: str = Depends(oauth2_scheme)):
#     headers = {'Accept': 'application/json'} 
#     response = requests.get(EUREKA_SERVER_INSTANCES, headers=headers)
#     # print(json_data)
#     # Check if the request was successful
#     if response.ok:
#         app_name = OTHER_SERVICE_NAME
#         json_data = response.json()
#         # print(json_data)
#         response_posts_url = get_service_url(json_data, app_name, token)
        
#         return {"response_posts_url": response_posts_url}
#     else:
#         raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from Eureka server")

# def get_service_url(json_data, app_name, token):
#     applications = json_data.get("applications", {}).get("application", [])
   
#     for application in applications:
#         if application.get("name") == app_name:
#             instances = application.get("instance", [])
#             if not isinstance(instances, list):
#                 instances = [instances]
#             for instance in instances:
#                 ip_address = instance.get("ipAddr", "")
#                 port = instance.get("port", {}).get("$", "")
#                 base_url = f"http://{ip_address}:{port}"
#                 response_slack_url = f"{base_url}{OTHER_SERVICE_URL}"
#                 print(response_slack_url)
#                 response = requests.get(response_slack_url, headers={"Authorization": f"Bearer {token}"})
                
#                 if response.ok:
#                     return response.json()
#                 else:
#                     raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from other service")
           
#     raise HTTPException(status_code=404, detail="No instance found for the given app name")
