from typing import Dict, List, Optional
import asyncpg
from datetime import datetime
import hashlib

class ShardManager:
    def __init__(self):
        self.shard_map = {}
        self.shard_connections = {}
        self.num_shards = 4
        
    async def initialize(self, connection_configs: List[Dict]):
        """Initialize shard connections"""
        for config in connection_configs:
            shard_id = config['shard_id']
            self.shard_connections[shard_id] = await asyncpg.create_pool(
                user=config['user'],
                password=config['password'],
                database=config['database'],
                host=config['host'],
                port=config['port']
            )
            
    def get_shard_id(self, key: str) -> int:
        """Determine shard ID for a given key"""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return hash_value % self.num_shards
    
    async def execute_query(self, shard_key: str, query: str, *args):
        """Execute query on appropriate shard"""
        shard_id = self.get_shard_id(shard_key)
        pool = self.shard_connections.get(shard_id)
        
        if not pool:
            raise ValueError(f"No connection pool for shard {shard_id}")
            
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)
            
    async def execute_cross_shard_query(self, query: str, *args) -> List:
        """Execute query across all shards"""
        results = []
        
        for pool in self.shard_connections.values():
            async with pool.acquire() as conn:
                shard_results = await conn.fetch(query, *args)
                results.extend(shard_results)
                
        return results
