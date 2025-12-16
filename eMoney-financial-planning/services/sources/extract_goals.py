import logging
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config
import time


def extract_goals(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract financial goals from eMoney Advisor API
    
    Uses page-based pagination (page/pageSize) instead of offset-based (skip/limit)
    
    Args:
        api_service: API service instance
        extraction_metadata: Metadata to add to each record
        checkpoint_callback: Function to save checkpoints
        filters: Extraction filters
        resume_from: Resume state from previous run
        check_cancelled_callback: Function to check if cancelled
        check_paused_callback: Function to check if paused
    
    Yields:
        Goal records with normalized field names and extraction metadata
    """
    logger = logging.getLogger(__name__)
    
    job_id = extraction_metadata.get('_scan_id', 'unknown')
    organization_id = extraction_metadata.get('_tenant_id', 'unknown')
    
    # Get configuration values
    config = get_config()
    GOAL_CHECKPOINT_FREQUENCY = getattr(config, 'GOAL_CHECKPOINT_FREQUENCY', 5)
    GOAL_PAUSE_CHECK_FREQUENCY = getattr(config, 'GOAL_PAUSE_CHECK_FREQUENCY', 2)
    GOAL_CANCEL_CHECK_FREQUENCY = getattr(config, 'GOAL_CANCEL_CHECK_FREQUENCY', 2)
    GOAL_MAX_BATCHES = getattr(config, 'GOAL_MAX_BATCHES', 1000)
    
    # Test mode configuration
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Goals for org: {organization_id}")
    logger.info("=" * 60)
    
    if test_mode:
        logger.info(f"Running in TEST MODE with batch delay={test_batch_delay}s, record delay={test_record_delay}s")

    # eMoney uses page-based pagination
    page = 1
    page_size = filters.get('batch_size', 100) if filters else 100
    if page_size > 100:
        page_size = 100  # eMoney API limit
        
    total_records = 0
    skipped_records = 0
    entity = 'goal'
    batch_counter = 0
    
    # Build API-compatible filters
    api_filters = {}
    if filters:
        if 'plan_id' in filters:
            api_filters['planId'] = filters['plan_id']
        if 'goal_type' in filters:
            api_filters['goalType'] = filters['goal_type']
        if 'status' in filters:
            api_filters['status'] = filters['status']
        if 'client_id' in filters:
            api_filters['clientId'] = filters['client_id']
    
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
                
            # Resume from page
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
        return batch_counter % GOAL_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % GOAL_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % GOAL_CHECKPOINT_FREQUENCY == 0
    
    goals_data = []
    
    while True:
        batch_counter += 1

        if test_mode and test_batch_delay > 0:
            logger.info(f"TEST MODE: Adding {test_batch_delay}s delay before batch {batch_counter}")
            time.sleep(test_batch_delay)
        
        if batch_counter > GOAL_MAX_BATCHES:
            logger.warning(f"Extraction of {entity} reached maximum batch limit ({GOAL_MAX_BATCHES})")
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
            logger.info(f"Fetching goals (page: {page}, pageSize: {page_size}) - batch {batch_counter}/{GOAL_MAX_BATCHES}...")
            
            # Call eMoney API with page/page_size
            response = api_service.get_goals(
                page=page,
                page_size=page_size,
                filters=api_filters
            )
            
            # Handle different response formats
            if isinstance(response, dict):
                # Check if response has data.records structure
                if 'data' in response and isinstance(response['data'], dict):
                    goals = response['data'].get('records', [])
                # Fallback to direct 'goals' key
                else:
                    goals = response.get('goals', [])
            else:
                goals = response if isinstance(response, list) else []
            
            if not goals:
                logger.info("No more goals found")
                break
            
            batch_size = 0
            goals_data = []
            
            for goal in goals:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                if test_mode and batch_size % 5 == 0:
                    if check_cancelled_callback and check_cancelled_callback():
                        logger.info(f"TEST MODE: Extraction cancelled during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="cancelled")
                        for goal_record in goals_data:
                            yield goal_record
                        return
                        
                    if check_paused_callback and check_paused_callback():
                        logger.info(f"TEST MODE: Extraction paused during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="paused")
                        for goal_record in goals_data:
                            yield goal_record
                        return

                try:
                    # CRITICAL: Validate required primary key field
                    goal_id = goal.get('GoalID')
                    if not goal_id:
                        logger.warning(f"Skipping goal record without GoalID at batch {batch_counter}, record {batch_size + 1}")
                        skipped_records += 1
                        continue
                    
                    # Create normalized goal record - FIXED FIELD MAPPINGS
                    # Map API fields to your database schema
                    goal_record = {
                        # Basic identification
                        'goal_id': goal_id,
                        'plan_id': goal.get('PlanID'),
                        'client_id': goal.get('ClientID'),
                        'household_id': goal.get('HouseholdID'),
                        'scenario_id': goal.get('ScenarioID'),
                        
                        # Goal details
                        'goal_name': goal.get('GoalName'),
                        'goal_type': goal.get('GoalType'),
                        'goal_category': goal.get('Category'),
                        'goal_description': goal.get('Description'),
                        'goal_status': goal.get('Status'),
                        
                        # Priority and importance
                        'priority': goal.get('Priority'),
                        'importance': goal.get('Importance'),
                        'is_essential': goal.get('IsEssential'),
                        'is_discretionary': goal.get('IsDiscretionary'),
                        
                        # Dates
                        'created_date': goal.get('CreatedDate'),
                        'modified_date': goal.get('ModifiedDate'),
                        'start_date': goal.get('StartDate'),
                        'end_date': goal.get('EndDate'),
                        'target_date': goal.get('TargetDate'),
                        
                        # Financial details
                        'target_amount': goal.get('TargetAmount'),
                        'current_amount': goal.get('CurrentValue'),
                        'required_amount': goal.get('RequiredAmount'),
                        'annual_cost': goal.get('AnnualCost'),
                        'total_cost': goal.get('TotalCost'),
                        'monthly_contribution': goal.get('MonthlyContribution'),
                        'annual_contribution': goal.get('AnnualContribution'),
                        
                        # Progress tracking
                        'percent_complete': goal.get('PercentComplete'),
                        'percent_funded': goal.get('FundingPercentage'),
                        'shortfall': goal.get('Shortfall'),
                        'surplus': goal.get('Surplus'),
                        'is_funded': goal.get('IsFunded'),
                        'is_on_track': goal.get('IsOnTrack'),
                        'projected_value': goal.get('ProjectedValue'),
                        
                        # Retirement-specific fields
                        'retirement_age': goal.get('RetirementAge'),
                        'retirement_income': goal.get('RetirementIncome'),
                        'desired_retirement_income': goal.get('DesiredRetirementIncome'),
                        'replacement_ratio': goal.get('ReplacementRatio'),
                        
                        # Education-specific fields
                        'beneficiary_name': goal.get('BeneficiaryName'),
                        'beneficiary_age': goal.get('BeneficiaryAge'),
                        'institution_type': goal.get('InstitutionType'),
                        'years_of_education': goal.get('YearsOfEducation'),
                        'annual_tuition': goal.get('AnnualTuition'),
                        
                        # Major purchase fields
                        'item_description': goal.get('ItemDescription'),
                        'purchase_year': goal.get('PurchaseYear'),
                        'down_payment': goal.get('DownPayment'),
                        'financed_amount': goal.get('FinancedAmount'),
                        
                        # Investment assumptions
                        'assumed_rate_of_return': goal.get('AssumedRateOfReturn'),
                        'inflation_rate': goal.get('InflationRate'),
                        'tax_rate': goal.get('TaxRate'),
                        'risk_level': goal.get('RiskLevel'),
                        
                        # Account associations
                        'funding_account_i_ds': goal.get('FundingAccountIDs'),
                        'dedicated_account_id': goal.get('DedicatedAccountID'),
                        
                        # Owner information
                        'owner_type': goal.get('OwnerType'),
                        'owner_id': goal.get('OwnerID'),
                        'owner_name': goal.get('OwnerName'),
                        'is_joint_goal': goal.get('IsJointGoal'),
                        
                        # Status flags
                        'is_active': goal.get('IsActive'),
                        'is_archived': goal.get('IsArchived'),
                        'is_achieved': goal.get('IsAchieved'),
                        'is_abandoned': goal.get('IsAbandoned'),
                        
                        # Notes and attachments
                        'notes': goal.get('Notes'),
                        'attachments': goal.get('Attachments'),
                    }
                    
                    # Handle nested objects with JSON serialization
                    nested_fields = [
                        'FundingSources', 'Milestones', 'CustomFields',
                        'Beneficiaries', 'LinkedAccounts', 'Assumptions',
                        'Timeline', 'Strategy', 'Projections', 'History'
                    ]
                    
                    for json_field in nested_fields:
                        if goal.get(json_field):
                            value = goal.get(json_field)
                            if isinstance(value, (dict, list)):
                                goal_record[json_field.lower()] = json.dumps(value)
                            else:
                                goal_record[json_field.lower()] = value

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        goal_record[meta_key] = meta_value
                    
                    goals_data.append(goal_record)
                    total_records += 1
                    batch_size += 1
                    
                except Exception as record_err:
                    logger.error(f"Error processing goal record: {record_err}")
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
            for goal_record in goals_data:
                yield goal_record
                
            logger.info(f"Processed {batch_size} goals (total: {total_records}, skipped: {skipped_records}) - batch {batch_counter}/{GOAL_MAX_BATCHES}")
            
            if should_save_checkpoint():
                save_checkpoint()
            
            # Check if we got fewer records than requested (end of data)
            if len(goals) < page_size:
                logger.info("Received partial page. Assuming end of results.")
                break
                
            # Move to next page
            page += 1
            
        except Exception as e:
            logger.error(f"Error extracting goals at page {page} - batch {batch_counter}: {e}")
            save_checkpoint(status="error")
            for goal_record in goals_data:
                yield goal_record
            raise
    
    logger.info(f"✓ Goals extraction complete: {total_records} records in {batch_counter} batches (skipped {skipped_records} records without GoalID)")
    save_checkpoint(status="completed")