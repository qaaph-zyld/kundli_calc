from typing import Any, Dict, Optional
import aio_pika
import asyncio
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class QueueMessage:
    message_type: str
    payload: Dict[str, Any]
    priority: int
    timestamp: datetime
    retry_count: int = 0

class MessageQueue:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queues = {
            'calculations': 'kundli_calculations',
            'research': 'research_analysis',
            'reports': 'report_generation'
        }
        
    async def initialize(self, connection_url: str):
        """Initialize queue connection"""
        self.connection = await aio_pika.connect_robust(connection_url)
        self.channel = await self.connection.channel()
        
        # Declare queues with proper configurations
        for queue_name in self.queues.values():
            await self.channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    'x-max-priority': 10,
                    'x-message-ttl': 3600000,  # 1 hour
                    'x-dead-letter-exchange': 'dlx'
                }
            )

    async def publish_message(self, queue_type: str, message: QueueMessage):
        """Publish message to queue"""
        queue_name = self.queues.get(queue_type)
        if not queue_name:
            raise ValueError(f"Invalid queue type: {queue_type}")
            
        message_body = json.dumps({
            'type': message.message_type,
            'payload': message.payload,
            'timestamp': message.timestamp.isoformat(),
            'retry_count': message.retry_count
        }).encode()
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                priority=message.priority,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )
