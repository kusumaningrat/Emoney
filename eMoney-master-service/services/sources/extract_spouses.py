import logging
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config
import time


def extract_spouses(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract spouses from eMoney Service API
    
    Uses page-based pagination (page/pageSize) instead of offset-based (skip/limit)
    
    Yields spouse records with normalized field names,
    with extraction metadata added.
    """
    logger = logging.getLogger(__name__)
    
    job_id = extraction_metadata.get('_scan_id', 'unknown')
    organization_id = extraction_metadata.get('_tenant_id', 'unknown')
    
    # Get configuration values
    config = get_config()
    SPOUSE_CHECKPOINT_FREQUENCY = getattr(config, 'SPOUSE_CHECKPOINT_FREQUENCY', 1)
    SPOUSE_PAUSE_CHECK_FREQUENCY = getattr(config, 'SPOUSE_PAUSE_CHECK_FREQUENCY', 1)
    SPOUSE_CANCEL_CHECK_FREQUENCY = getattr(config, 'SPOUSE_CANCEL_CHECK_FREQUENCY', 1)
    SPOUSE_MAX_BATCHES = getattr(config, 'SPOUSE_MAX_BATCHES', 1000)
    
    # Test mode configuration
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Spouses for org: {organization_id}")
    logger.info("=" * 60)
    
    if test_mode:
        logger.info(f"Running in TEST MODE with batch delay={test_batch_delay}s, record delay={test_record_delay}s")

    # eMoney uses page-based pagination
    page = 1
    page_size = filters.get('batch_size', 100) if filters else 100
    if page_size > 100:
        page_size = 100  # eMoney API limit
        
    total_records = 0
    entity = 'spouse'
    batch_counter = 0
    
    # Build API-compatible filters
    api_filters = {}
    if filters:
        if 'status' in filters:
            api_filters['status'] = filters['status']
    
    # Check if resuming from a previous state
    if resume_from and isinstance(resume_from, dict):
        entity_checkpoint = resume_from.get(entity)
        if entity_checkpoint:
            checkpoint_data = entity_checkpoint.get('checkpoint_data', {})
            
            if checkpoint_data and checkpoint_data.get("status") == "completed":
                logger.info(f"Entity '{entity}' was already completed in previous run")
                return
                
            if checkpoint_data and checkpoint_data.get("status") == "paused":
                logger.info(f"Resuming {entity} extraction from paused state")
                
            # Resume from page (not offset)
            if checkpoint_data and "page" in checkpoint_data:
                page = checkpoint_data["page"]
                total_records = entity_checkpoint.get("records_processed", 0)
                batch_counter = checkpoint_data.get("batch_counter", 0)
                logger.info(f"Resuming {entity} extraction from page {page} (batch {batch_counter})")
    
    def save_checkpoint(status='in_progress'):
        if checkpoint_callback:
            try:
                checkpoint_data = {
                    'entity': entity,
                    'records_processed': total_records,
                    'checkpoint_data': {
                        'page': page,
                        'status': status,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'batch_counter': batch_counter
                    },
                }
                checkpoint_callback(job_id, checkpoint_data)
                logger.info(f"Checkpoint saved: {total_records} {entity} with status '{status}' at batch {batch_counter}")
            except Exception as e:
                logger.warning(f"Failed to save checkpoint: {e}")
    
    def should_check_cancelled():
        return batch_counter % SPOUSE_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % SPOUSE_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % SPOUSE_CHECKPOINT_FREQUENCY == 0
    
    spouses_data = []
    
    while True:
        batch_counter += 1

        if test_mode and test_batch_delay > 0:
            logger.info(f"TEST MODE: Adding {test_batch_delay}s delay before batch {batch_counter}")
            time.sleep(test_batch_delay)
        
        if batch_counter > SPOUSE_MAX_BATCHES:
            logger.warning(f"Extraction of {entity} reached maximum batch limit ({SPOUSE_MAX_BATCHES})")
            save_checkpoint(status="max_batches_reached")
            break
        
        if should_check_cancelled() and check_cancelled_callback and check_cancelled_callback():
            logger.info(f"Extraction of {entity} cancelled by user at batch {batch_counter}")
            save_checkpoint(status="cancelled")
            return
            
        if should_check_paused() and check_paused_callback and check_paused_callback():
            logger.info(f"Extraction of {entity} paused by user at batch {batch_counter}")
            save_checkpoint(status="paused")
            return
        
        try:
            logger.info(f"Fetching spouses (page: {page}, pageSize: {page_size}) - batch {batch_counter}/{SPOUSE_MAX_BATCHES}...")
            
            # Call eMoney API with page/page_size (not skip/limit)
            response = api_service.get_spouses(
                page=page,
                page_size=page_size,
                filters=api_filters
            )
            
            # Handle different response formats
            if isinstance(response, dict):
                spouses = (response.get('spouses') or 
                          response.get('items') or 
                          response.get('data') or 
                          response.get('results') or 
                          response.get('Data') or [])
            else:
                spouses = response if isinstance(response, list) else []
            
            if not spouses:
                logger.info("No more spouses found")
                break
            
            batch_size = 0
            spouses_data = []
            
            for spouse in spouses:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                if test_mode and batch_size % 5 == 0:
                    if check_cancelled_callback and check_cancelled_callback():
                        logger.info(f"TEST MODE: Extraction cancelled during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="cancelled")
                        for spouse_record in spouses_data:
                            yield spouse_record
                        return
                        
                    if check_paused_callback and check_paused_callback():
                        logger.info(f"TEST MODE: Extraction paused during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="paused")
                        for spouse_record in spouses_data:
                            yield spouse_record
                        return

                try:
                    # Create normalized spouse record (eMoney uses PascalCase)
                    spouse_record = {
                        # Basic identification
                        'SpouseID': spouse.get('SpouseID'),
                        'ClientID': spouse.get('ClientID'),
                        'HouseholdID': spouse.get('HouseholdID'),
                        'FirmID': spouse.get('FirmID'),
                        
                        # Personal information
                        'FirstName': spouse.get('FirstName'),
                        'MiddleName': spouse.get('MiddleName'),
                        'LastName': spouse.get('LastName'),
                        'PreferredName': spouse.get('PreferredName'),
                        'Suffix': spouse.get('Suffix'),
                        'Gender': spouse.get('Gender'),
                        'DateOfBirth': spouse.get('DateOfBirth'),
                        'Age': spouse.get('Age'),
                        'SSN': spouse.get('SSN'),
                        
                        # Contact details
                        'Email': spouse.get('Email'),
                        'Phone': spouse.get('Phone'),
                        'MobilePhone': spouse.get('MobilePhone'),
                        'WorkPhone': spouse.get('WorkPhone'),
                        
                        # Employment
                        'Employer': spouse.get('Employer'),
                        'Occupation': spouse.get('Occupation'),
                        'EmploymentStatus': spouse.get('EmploymentStatus'),
                        'AnnualIncome': spouse.get('AnnualIncome'),
                        
                        # Status and dates
                        'Status': spouse.get('Status'),
                        'MaritalStatus': spouse.get('MaritalStatus'),
                        'CreatedDate': spouse.get('CreatedDate'),
                        'ModifiedDate': spouse.get('ModifiedDate'),
                        
                        # Financial
                        'NetWorth': spouse.get('NetWorth'),
                        'RiskTolerance': spouse.get('RiskTolerance'),
                    }
                    
                    # Handle nested objects with JSON serialization
                    for json_field in ['Address', 'MailingAddress', 'CustomFields', 
                                      'Accounts', 'Goals']:
                        if spouse.get(json_field):
                            value = spouse.get(json_field)
                            if isinstance(value, (dict, list)):
                                spouse_record[json_field] = json.dumps(value)
                            else:
                                spouse_record[json_field] = value

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        spouse_record[meta_key] = meta_value
                    
                    spouses_data.append(spouse_record)
                    total_records += 1
                    batch_size += 1
                    
                except Exception as record_err:
                    logger.error(f"Error processing spouse record: {record_err}")
                    continue
            
            if test_mode and test_batch_delay > 0:
                logger.info(f"TEST MODE: Adding {test_batch_delay/2}s delay after processing batch {batch_counter}")
                time.sleep(test_batch_delay/2)
                
                if check_cancelled_callback and check_cancelled_callback():
                    logger.info(f"TEST MODE: Extraction cancelled after batch processing at batch {batch_counter}")
                    save_checkpoint(status="cancelled")
                    break
                    
                if check_paused_callback and check_paused_callback():
                    logger.info(f"TEST MODE: Extraction paused after batch processing at batch {batch_counter}")
                    save_checkpoint(status="paused")
                    break
            
            # Yield the processed records
            for spouse_record in spouses_data:
                yield spouse_record
                
            logger.info(f"Processed {batch_size} spouses (total: {total_records}) - batch {batch_counter}/{SPOUSE_MAX_BATCHES}")
            
            if should_save_checkpoint():
                save_checkpoint()
            
            # Check if we got fewer records than requested (end of data)
            if len(spouses) < page_size:
                logger.info("Received partial page. Assuming end of results.")
                break
                
            # Move to next page
            page += 1
            
        except Exception as e:
            logger.error(f"Error extracting spouses at page {page} - batch {batch_counter}: {e}")
            save_checkpoint(status="error")
            for spouse_record in spouses_data:
                yield spouse_record
            raise
    
    logger.info(f"✓ Spouses extraction complete: {total_records} records in {batch_counter} batches")
    save_checkpoint(status="completed")