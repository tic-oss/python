from fastapi import HTTPException
from core.rabbitmq.producer import RabbitMQProducer

import logging
logger = logging.getLogger(__name__)

def handle_note_not_found(id: int):
    raise HTTPException(status_code=404, detail=f"The id: {id} does not exist")
    
def handle_invalid_note_id(id: int):
    raise HTTPException(status_code=400, detail=f"The id: {id} you requested for does not exist")
    
async def publish_message_to_queue(message: dict):
       producer = RabbitMQProducer(exchange_name='direct_logs')  # Create an instance of RabbitMQProducer
       producer.publish_message(routing_key='pro_queue', message=message)
   