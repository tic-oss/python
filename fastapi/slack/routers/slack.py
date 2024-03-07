from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import MongoClient
from typing import List
from services.keycloak import oauth2_scheme
from backend.database import MSG_COLLECTION, DB
from models.models import Message
import services.eureka as eureka

from services.consumer import RabbitMQConsumer
import logging
from dotenv import load_dotenv
import os
import asyncio

# async def main():
#     consumer = RabbitMQConsumer('direct_logs', 'data_queue', ['pro_queue'])
#     await consumer.start_consuming()

# if __name__ == "__main__":
#     asyncio.run(main())

# async def consume_messages():
#     consumer = RabbitMQConsumer('direct_logs', 'data_queue', ['pro_queue'])
#     await consumer.start_consuming()

# # Run the consuming process asynchronously
# async def main():
#     await consume_messages()

# Start the asyncio event loop
# if __name__ == "__main__":
#     asyncio.run(main())
 
load_dotenv()

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/slack',
    tags=['slack']
)

MONGO_URI = os.getenv("MONGO_URI")
SLACK_PORT= os.getenv("POST_PORT")

# consumer = RabbitMQConsumer('direct_logs', 'data_queue', ['pro_queue'])

# # Call the start_consuming method on the instance
# consumer.start_consuming()

Mongo_uri = MONGO_URI


@router.get("/status")
async def get_status(token: str = Depends(oauth2_scheme)):
    """Get status of messaging server."""
    logger.info(f"request / endpoint!")
    return {"status": "running"}

@router.get("/channels", response_model=List[str])
async def get_channels(token: str = Depends(oauth2_scheme)):
    """Get all channels in list form."""
    logger.info(f"request / endpoint!")
    with MongoClient() as client:
        msg_collection = client[DB][MSG_COLLECTION]
        distinct_channel_list = msg_collection.distinct("channel")
        logger.info(f"request / endpoint!")
        return distinct_channel_list

@router.get("/messages/{channel}", response_model=List[Message])
async def get_messages(channel: str, token: str = Depends(oauth2_scheme)):
    logger.info(f"request / endpoint!")
    """Get all messages for the specified channel."""
    with MongoClient(MONGO_URI) as client:
        msg_collection = client[DB][MSG_COLLECTION]
        msg_list = msg_collection.find({"channel": channel})
        response_msg_list = []
        for msg in msg_list:
            response_msg_list.append(Message(**msg))

        return response_msg_list


@router.post("/post_message", status_code=status.HTTP_201_CREATED)
async def post_message(message: Message, token: str = Depends(oauth2_scheme)):
    """Post a new message to the specified channel."""
    
    with MongoClient(Mongo_uri) as client:
        msg_collection = client[DB][MSG_COLLECTION]
        result = msg_collection.insert_one(message.dict())
        ack = result.acknowledged

        logger.info(f"request / endpoint!")

        message_to_publish = message.dict()
        # producer.publish_message(routing_key='pro_queue', message=message_to_publish)
        
        return {"insertion": ack}


@router.put("/update_message/{message_id}", status_code=status.HTTP_200_OK)
async def update_message(message_id: str, updated_message: Message, token: str = Depends(oauth2_scheme)):
    """Update an existing message with the specified ID."""
    logger.info(f"request / endpoint!")
    with MongoClient(Mongo_uri) as client:
        msg_collection = client[DB][MSG_COLLECTION]
        result = msg_collection.update_one({"_id": ObjectId(message_id)}, {"$set": updated_message.dict()})
        
        if result.modified_count == 1:
            return {"message": "Update successful"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        
@router.delete("/delete_message/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: str, token: str = Depends(oauth2_scheme)):
    """Delete a message with the specified ID."""
    logger.info(f"request / endpoint!")
    with MongoClient(Mongo_uri) as client:
        msg_collection = client[DB][MSG_COLLECTION]
        result = msg_collection.delete_one({"_id": ObjectId(message_id)})
        
        if result.deleted_count == 1:
            return {"message": "Deletion successful"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        

   