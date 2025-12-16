import logging
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config
import time


def extract_plans(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
    include_nested: bool = False,
) -> Iterator[Dict[str, Any]]:
    """
    Extract financial plans from eMoney Advisor API
    
    Uses page-based pagination (page/pageSize) instead of offset-based (skip/limit)
    
    Args:
        api_service: API service instance
        extraction_metadata: Metadata to add to each record
        checkpoint_callback: Function to save checkpoints
        filters: Extraction filters
        resume_from: Resume state from previous run
        check_cancelled_callback: Function to check if cancelled
        check_paused_callback: Function to check if paused
        include_nested: Include nested scenarios and goals
    
    Yields:
        Plan records with normalized field names and extraction metadata
    """
    logger = logging.getLogger(__name__)
    
    job_id = extraction_metadata.get('_scan_id', 'unknown')
    organization_id = extraction_metadata.get('_tenant_id', 'unknown')
    
    # Get configuration values
    config = get_config()
    PLAN_CHECKPOINT_FREQUENCY = getattr(config, 'PLAN_CHECKPOINT_FREQUENCY', 5)
    PLAN_PAUSE_CHECK_FREQUENCY = getattr(config, 'PLAN_PAUSE_CHECK_FREQUENCY', 2)
    PLAN_CANCEL_CHECK_FREQUENCY = getattr(config, 'PLAN_CANCEL_CHECK_FREQUENCY', 2)
    PLAN_MAX_BATCHES = getattr(config, 'PLAN_MAX_BATCHES', 1000)
    
    # Test mode configuration
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Plans for org: {organization_id}")
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
    entity = 'plan'
    batch_counter = 0
    
    # Build API-compatible filters
    api_filters = {}
    if filters:
        if 'client_id' in filters:
            api_filters['clientId'] = filters['client_id']
        if 'status' in filters:
            api_filters['status'] = filters['status']
        if 'plan_type' in filters:
            api_filters['planType'] = filters['plan_type']
    
    include_scenarios = include_nested or filters.get('include_scenarios', False) if filters else False
    include_goals = include_nested or filters.get('include_goals', False) if filters else False
    
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
        return batch_counter % PLAN_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % PLAN_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % PLAN_CHECKPOINT_FREQUENCY == 0
    
    plans_data = []
    
    while True:
        batch_counter += 1

        if test_mode and test_batch_delay > 0:
            logger.info(f"TEST MODE: Adding {test_batch_delay}s delay before batch {batch_counter}")
            time.sleep(test_batch_delay)
        
        if batch_counter > PLAN_MAX_BATCHES:
            logger.warning(f"Extraction of {entity} reached maximum batch limit ({PLAN_MAX_BATCHES})")
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
            logger.info(f"Fetching plans (page: {page}, pageSize: {page_size}) - batch {batch_counter}/{PLAN_MAX_BATCHES}...")
            
            # Call eMoney API with page/page_size
            response = api_service.get_plans(
                page=page,
                page_size=page_size,
                filters=api_filters,
                include_scenarios=include_scenarios,
                include_goals=include_goals
            )
            
            # Handle different response formats
            if isinstance(response, dict):
                # Check if response has data.records structure
                if 'data' in response and isinstance(response['data'], dict):
                    plans = response['data'].get('records', [])
                # Fallback to direct 'plans' key
                else:
                    plans = response.get('plans', [])
            else:
                plans = response if isinstance(response, list) else []
            
            if not plans:
                logger.info("No more plans found")
                break
            
            batch_size = 0
            plans_data = []
            
            for plan in plans:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                if test_mode and batch_size % 5 == 0:
                    if check_cancelled_callback and check_cancelled_callback():
                        logger.info(f"TEST MODE: Extraction cancelled during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="cancelled")
                        for plan_record in plans_data:
                            yield plan_record
                        return
                        
                    if check_paused_callback and check_paused_callback():
                        logger.info(f"TEST MODE: Extraction paused during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="paused")
                        for plan_record in plans_data:
                            yield plan_record
                        return

                try:
                    # CRITICAL: Validate required primary key field
                    plan_id = plan.get('PlanID')
                    if not plan_id:
                        logger.warning(f"Skipping plan record without PlanID at batch {batch_counter}, record {batch_size + 1}")
                        skipped_records += 1
                        continue
                    
                    # Create normalized plan record - convert to snake_case
                    plan_record = {
                        # Basic identification
                        'plan_id': plan_id,
                        'client_id': plan.get('ClientID'),
                        'household_id': plan.get('HouseholdID'),
                        'firm_id': plan.get('FirmID'),
                        'advisor_id': plan.get('AdvisorID'),
                        
                        # Plan details
                        'plan_name': plan.get('PlanName'),
                        'plan_type': plan.get('PlanType'),
                        'status': plan.get('Status'),
                        'plan_description': plan.get('PlanDescription'),
                        
                        # Dates
                        'created_date': plan.get('CreatedDate'),
                        'modified_date': plan.get('ModifiedDate'),
                        'last_reviewed': plan.get('LastReviewed'),
                        'next_review_date': plan.get('NextReviewDate'),
                        
                        # Plan period
                        'start_date': plan.get('StartDate'),
                        'end_date': plan.get('EndDate'),
                        'planning_horizon': plan.get('PlanningHorizon'),
                        'retirement_age': plan.get('RetirementAge'),
                        'life_expectancy': plan.get('LifeExpectancy'),
                        
                        # Financial assumptions
                        'inflation_rate': plan.get('InflationRate'),
                        'tax_rate': plan.get('TaxRate'),
                        'rate_of_return': plan.get('RateOfReturn'),
                        'discount_rate': plan.get('DiscountRate'),
                        
                        # Plan metrics
                        'probability_of_success': plan.get('ProbabilityOfSuccess'),
                        'funded_ratio': plan.get('FundedRatio'),
                        'surplus_deficit': plan.get('SurplusDeficit'),
                        'monte_carlo_iterations': plan.get('MonteCarloIterations'),
                        
                        # Retirement planning
                        'retirement_income': plan.get('RetirementIncome'),
                        'retirement_expenses': plan.get('RetirementExpenses'),
                        'retirement_readiness': plan.get('RetirementReadiness'),
                        'social_security_benefit': plan.get('SocialSecurityBenefit'),
                        'pension_benefit': plan.get('PensionBenefit'),
                        
                        # Client information
                        'created_by': plan.get('CreatedBy'),
                        'client_name': plan.get('ClientName'),
                        'spouse_name': plan.get('SpouseName'),
                        'client_age': plan.get('ClientAge'),
                        'spouse_age': plan.get('SpouseAge'),
                        
                        # Version and tracking
                        'version': plan.get('Version'),
                        'is_active': plan.get('IsActive'),
                        'is_archived': plan.get('IsArchived'),
                        'is_primary_plan': plan.get('IsPrimaryPlan'),
                    }
                    
                    # Handle nested objects with JSON serialization
                    nested_fields = [
                        'Scenarios', 'Goals', 'Assumptions', 'CustomFields',
                        'RiskProfile', 'IncomeStreams', 'ExpenseCategories',
                        'Assets', 'Liabilities', 'Insurance', 'Estate',
                        'TaxStrategies', 'InvestmentPolicy', 'Notes'
                    ]
                    
                    for json_field in nested_fields:
                        if plan.get(json_field):
                            value = plan.get(json_field)
                            if isinstance(value, (dict, list)):
                                plan_record[json_field.lower()] = json.dumps(value)
                            else:
                                plan_record[json_field.lower()] = value

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        plan_record[meta_key] = meta_value
                    
                    plans_data.append(plan_record)
                    total_records += 1
                    batch_size += 1
                    
                except Exception as record_err:
                    logger.error(f"Error processing plan record: {record_err}")
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
            for plan_record in plans_data:
                yield plan_record
                
            logger.info(f"Processed {batch_size} plans (total: {total_records}, skipped: {skipped_records}) - batch {batch_counter}/{PLAN_MAX_BATCHES}")
            
            if should_save_checkpoint():
                save_checkpoint()
            
            # Check if we got fewer records than requested (end of data)
            if len(plans) < page_size:
                logger.info("Received partial page. Assuming end of results.")
                break
                
            # Move to next page
            page += 1
            
        except Exception as e:
            logger.error(f"Error extracting plans at page {page} - batch {batch_counter}: {e}")
            save_checkpoint(status="error")
            for plan_record in plans_data:
                yield plan_record
            raise
    
    logger.info(f"✓ Plans extraction complete: {total_records} records in {batch_counter} batches (skipped {skipped_records} records without PlanID)")
    save_checkpoint(status="completed")