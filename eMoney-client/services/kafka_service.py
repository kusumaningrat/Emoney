"""
Kafka Stream Service - Identity entities only mapping
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List

from kafka import KafkaProducer
from config import get_config

class KafkaStreamService:
    """Service for streaming data to Kafka topics in batches"""

    def __init__(self, extraction_service):
        """
        Initialize the Kafka stream service
        
        Args:
            extraction_service: The extraction service instance to use
        """
        self.logger = logging.getLogger(__name__)
        self.extraction_service = extraction_service
        self.config = get_config()
        
        # Get Kafka config
        self.bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

        # Set default status
        self.producer_available = False
        
        # Client Core Entities only topic mapping
        self.topics = {
            # Client Core Entities
            'client': os.environ.get('KAFKA_TOPIC_CLIENT', 'emoney_client_client'),
            'contact': os.environ.get('KAFKA_TOPIC_CONTACT', 'emoney_client_contact'),
            'household': os.environ.get('KAFKA_TOPIC_HOUSEHOLD', 'emoney_client_household'),
            'spouse': os.environ.get('KAFKA_TOPIC_SPOUSE', 'emoney_client_spouse'),
            'relationship': os.environ.get('KAFKA_TOPIC_RELATIONSHIP', 'emoney_client_relationship'),
            
            # Keep legacy topics for backward compatibility
            'topic_1': os.environ.get('KAFKA_TOPIC_1', 'kafka_topic_1'),
            'topic_2': os.environ.get('KAFKA_TOPIC_2', 'kafka_topic_2'),
            'topic_3': os.environ.get('KAFKA_TOPIC_3', 'kafka_topic_3'),
        }
        
        self.kafka_enabled = os.environ.get('KAFKA_ENABLED', 'false').lower() == 'true'

        if self.kafka_enabled:
            self._initialize_producer()
        else:
            self.logger.info("Kafka streaming is disabled via configuration.")
    
    def _initialize_producer(self) -> None:
        """Initialize the Kafka producer with graceful fallback"""
        import time
        
        # Set default status
        self.producer_available = False
        
        max_retries = 5
        retry_interval = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Initializing Kafka producer (attempt {attempt+1}/{max_retries})")
                
                # Use explicit API version to avoid broker version check
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                    key_serializer=lambda x: x.encode('utf-8') if x else None,
                    api_version=(2, 5, 0),  # Explicitly set API version 
                    request_timeout_ms=30000,  # 30 seconds timeout
                    reconnect_backoff_ms=1000,
                    reconnect_backoff_max_ms=10000,
                    # Auto-create topics if they don't exist
                    acks='all'
                )
                
                self.logger.info(f"Successfully connected to Kafka at {self.bootstrap_servers}")
                self.producer_available = True
                return
                
            except Exception as e:
                self.logger.warning(f"Kafka connection failed (attempt {attempt+1}/{max_retries}): {str(e)}")
                
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
                else:
                    self.logger.error("Maximum retries reached. Kafka streaming will be disabled.")
                    # Don't raise exception, just log the error
                    self.producer_available = False
    
    def _get_scan_status(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan status information"""
        try:
            status_result = self.extraction_service.get_scan_status(scan_id)
            if not status_result or not isinstance(status_result, dict):
                self.logger.warning(f"Failed to get scan status for {scan_id}")
                return None
            
            return status_result
        except Exception as e:
            self.logger.error(f"Error getting scan status: {str(e)}")
            return None
    
    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a record by removing unnecessary fields
        
        Args:
            record: The record to transform
            
        Returns:
            Transformed record
        """
        # Make a copy to avoid modifying the original
        transformed = record.copy()
        
        # Remove DLT-specific metadata fields that aren't needed by consumers
        fields_to_remove = [
            '_dlt_load_id',
            '_dlt_id',
            '_extracted_at',
            '_scan_id',  # Redundant since scan_id is in the batch metadata
            '_tenant_id'  # Redundant since glynac_organization_id is in the batch metadata
        ]
        
        # Remove fields
        for field in fields_to_remove:
            if field in transformed:
                del transformed[field]
                
        return transformed
    
    def _transform_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of records
        
        Args:
            records: List of records to transform
            
        Returns:
            List of transformed records
        """
        return [self._transform_record(record) for record in records]
    
    def get_available_topics(self) -> Dict[str, str]:
        """
        Get list of available topics for debugging
        
        Returns:
            Dictionary of entity_type -> topic_name mappings
        """
        return self.topics.copy()
    
    def is_entity_type_supported(self, entity_type: str) -> bool:
        """
        Check if an entity type is supported (has a Kafka topic mapping)
        
        Args:
            entity_type: The entity type to check
            
        Returns:
            True if supported, False otherwise
        """
        return entity_type.lower() in self.topics
    
    def stream_scan_data(self, scan_id: str, batch_size: int = 100, offset: int = 0) -> Dict:
        """
        Stream scan data of specific entity type to Kafka with improved error handling
        
        Args:
            scan_id: ID of the scan
            batch_size: Number of records per batch
            offset: Starting offset for data retrieval
            
        Returns:
            Response dict
        """
        # Get scan status first
        scan_status = self._get_scan_status(scan_id)
    
        if not scan_status:
            return {
                "success": False,
                "message": f"Failed to get scan status for {scan_id}"
            }, 404
        
        # Check if scan is completed
        if scan_status.get('status') != 'completed':
            return {
                "success": False,
                "message": f"Scan is not completed. Current status: {scan_status.get('status')}"
            }, 400
        
        # Auto-detect entity type from scan status
        entity_type = scan_status.get('type')
        
        # If not found or invalid, return error
        if not entity_type or not isinstance(entity_type, str):
            return {
                "success": False,
                "message": f"Could not detect entity type from scan status for {scan_id}"
            }, 400
        
        entity_type = entity_type.lower()
        
        # IMPROVED: Better error message with available types
        if entity_type not in self.topics:
            available_types = ", ".join(sorted(self.topics.keys()))
            self.logger.error(f"Entity type '{entity_type}' not found. Available types: {available_types}")
            return {
                "success": False,
                "message": f"Invalid entity type: {entity_type}. Available types: {available_types}"
            }, 400
        
        # Get organization ID
        organization_id = scan_status.get('organizationId')
        
        # Start streaming
        topic = self.topics[entity_type]
        current_offset = offset
        total_count = 0
        total_batches = 0
        total_records = None  # Will be set from pagination info
        
        self.logger.info(f"Streaming {entity_type} data from scan {scan_id} to topic {topic}")
        
        try:
            # Check if Kafka is available
            if not self.producer_available:
                return {
                    "success": False,
                    "message": "Kafka producer is not available"
                }, 503
            
            # Send initial message
            init_message = {
                'scan_id': scan_id,
                'entity_type': entity_type,
                'glynac_organization_id': organization_id,
                'timestamp': datetime.now().isoformat(),
                'status': scan_status.get('status'),
                'message_type': 'stream_init',
                'stream_info': {
                    'batch_size': batch_size,
                    'start_time': datetime.now().isoformat(),
                    'scan_start_time': scan_status.get('startTime'),
                    'scan_end_time': scan_status.get('endTime'),
                    'starting_offset': offset
                }
            }
            
            # Send with special key to mark beginning
            init_key = f"{scan_id}_{entity_type}_init_{current_offset}"
            self.producer.send(topic, key=init_key, value=init_message)
            self.producer.flush()
            
            # Loop until we've processed all records
            has_more = True
            while has_more:
                # Get batch of records
                result = self.extraction_service.get_scan_results(scan_id, entity_type, batch_size, current_offset)
                
                if not result.get('success', False):
                    if total_count == 0:
                        error_msg = result.get('message', 'Unknown error')
                        return {
                            "success": False, 
                            "message": error_msg
                        }, 404 if "not found" in error_msg.lower() else 400
                    else:
                        break
                
                data = result.get('data', {})
                records = data.get('records', [])
                
                if not records:
                    break
                
                # Get pagination info if available
                pagination = data.get('pagination', {})
                if pagination and total_records is None:
                    total_records = pagination.get('total', 0)
                    self.logger.info(f"Total records for {scan_id}: {total_records}")
                
                has_more = pagination.get('hasMore', False) if pagination else False
                
                # Transform records to remove unnecessary fields
                transformed_records = self._transform_records(records)
                
                # Prepare batch data with transformed records
                batch_data = {
                    'scan_id': scan_id,
                    'entity_type': entity_type,
                    'glynac_organization_id': organization_id, 
                    'batch_offset': current_offset,
                    'batch_size': len(transformed_records),
                    'batch_number': total_batches + 1,
                    'timestamp': datetime.now().isoformat(),
                    'status': scan_status.get('status'),
                    'message_type': 'batch_data',
                    'records': transformed_records,  # Use transformed records here
                    'pagination': {
                        'total': pagination.get('total', 0) if pagination else len(records),
                        'offset': current_offset,
                        'limit': batch_size,
                        'has_more': has_more
                    }
                }
                
                # Send batch
                batch_key = f"{scan_id}_{entity_type}_{current_offset}"
                self.producer.send(topic, key=batch_key, value=batch_data)
                self.producer.flush()
                
                # Update counters
                batch_count = len(records)
                total_count += batch_count
                total_batches += 1
                
                # Update offset based on pagination
                if pagination and pagination.get('offset') is not None and pagination.get('limit') is not None:
                    # If API returns specific pagination info, use it
                    current_offset = pagination.get('offset') + pagination.get('limit')
                else:
                    # Otherwise increment by batch size
                    current_offset += batch_count
                
                if batch_count < batch_size:
                    # We received fewer records than requested, likely at the end
                    has_more = False
            
            # Send completion message
            completion_message = {
                'scan_id': scan_id,
                'entity_type': entity_type,
                'glynac_organization_id': organization_id,
                'timestamp': datetime.now().isoformat(),
                'status': scan_status.get('status'),
                'message_type': 'stream_complete',
                'stream_summary': {
                    'total_records': total_records if total_records is not None else total_count,
                    'total_batches': total_batches,
                    'end_time': datetime.now().isoformat(),
                    'scan_info': {
                        'scan_id': scan_id,
                        'organization_id': organization_id,
                        'status': scan_status.get('status'),
                        'start_time': scan_status.get('startTime'),
                        'end_time': scan_status.get('endTime'),
                        'duration': scan_status.get('duration')
                    }
                }
            }
            
            # Send with special key to mark completion
            completion_key = f"{scan_id}_{entity_type}_complete"
            self.producer.send(topic, key=completion_key, value=completion_message)
            self.producer.flush()
            
            self.logger.info(f"Successfully streamed {total_count} {entity_type} records in {total_batches} batches to {topic}")
            
            # Return success
            return {
                "success": True,
                "message": f"Streamed {total_count} {entity_type} records in {total_batches} batches to {topic}",
                "data": {
                    "total_count": total_records if total_records is not None else total_count,
                    "total_batches": total_batches,
                    "topic": topic,
                    "entity_type": entity_type,
                    "organization_id": organization_id,
                    "scan_id": scan_id
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error streaming {entity_type}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to stream: {str(e)}"
            }, 500
    
    def close(self):
        """Close the Kafka producer"""
        if hasattr(self, 'producer'):
            self.producer.close()