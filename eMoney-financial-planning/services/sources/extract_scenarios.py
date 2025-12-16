import logging
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config
import time


def extract_scenarios(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
    include_projections: bool = False,
) -> Iterator[Dict[str, Any]]:
    """
    Extract planning scenarios from eMoney Advisor API
    
    Uses page-based pagination (page/pageSize) instead of offset-based (skip/limit)
    
    Args:
        api_service: API service instance
        extraction_metadata: Metadata to add to each record
        checkpoint_callback: Function to save checkpoints
        filters: Extraction filters
        resume_from: Resume state from previous run
        check_cancelled_callback: Function to check if cancelled
        check_paused_callback: Function to check if paused
        include_projections: Include cashflow and networth projections
    
    Yields:
        Scenario records with normalized field names and extraction metadata
    """
    logger = logging.getLogger(__name__)
    
    job_id = extraction_metadata.get('_scan_id', 'unknown')
    organization_id = extraction_metadata.get('_tenant_id', 'unknown')
    
    # Get configuration values
    config = get_config()
    SCENARIO_CHECKPOINT_FREQUENCY = getattr(config, 'SCENARIO_CHECKPOINT_FREQUENCY', 5)
    SCENARIO_PAUSE_CHECK_FREQUENCY = getattr(config, 'SCENARIO_PAUSE_CHECK_FREQUENCY', 2)
    SCENARIO_CANCEL_CHECK_FREQUENCY = getattr(config, 'SCENARIO_CANCEL_CHECK_FREQUENCY', 2)
    SCENARIO_MAX_BATCHES = getattr(config, 'SCENARIO_MAX_BATCHES', 1000)
    
    # Test mode configuration
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Scenarios for org: {organization_id}")
    logger.info("=" * 60)
    
    if test_mode:
        logger.info(f"Running in TEST MODE with batch delay={test_batch_delay}s, record delay={test_record_delay}s")

    # eMoney uses page-based pagination
    page = 1
    page_size = filters.get('batch_size', 100) if filters else 100
    if page_size > 100:
        page_size = 100  # eMoney API limit
        
    total_records = 0
    entity = 'scenario'
    batch_counter = 0
    
    # Build API-compatible filters
    api_filters = {}
    if filters:
        if 'plan_id' in filters:
            api_filters['planId'] = filters['plan_id']
        if 'scenario_type' in filters:
            api_filters['scenarioType'] = filters['scenario_type']
        if 'status' in filters:
            api_filters['status'] = filters['status']
    
    include_cashflow = include_projections or filters.get('include_cashflow', False) if filters else False
    include_networth = include_projections or filters.get('include_networth', False) if filters else False
    
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
        return batch_counter % SCENARIO_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % SCENARIO_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % SCENARIO_CHECKPOINT_FREQUENCY == 0
    
    scenarios_data = []
    
    while True:
        batch_counter += 1

        if test_mode and test_batch_delay > 0:
            logger.info(f"TEST MODE: Adding {test_batch_delay}s delay before batch {batch_counter}")
            time.sleep(test_batch_delay)
        
        if batch_counter > SCENARIO_MAX_BATCHES:
            logger.warning(f"Extraction of {entity} reached maximum batch limit ({SCENARIO_MAX_BATCHES})")
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
            logger.info(f"Fetching scenarios (page: {page}, pageSize: {page_size}) - batch {batch_counter}/{SCENARIO_MAX_BATCHES}...")
            
            # Call eMoney API with page/page_size
            response = api_service.get_scenarios(
                page=page,
                page_size=page_size,
                filters=api_filters
            )
            
            # Handle different response formats
            if isinstance(response, dict):
                scenarios = (response.get('scenarios') or 
                           response.get('items') or 
                           response.get('data') or 
                           response.get('results') or 
                           response.get('Data') or [])
            else:
                scenarios = response if isinstance(response, list) else []
            
            if not scenarios:
                logger.info("No more scenarios found")
                break
            
            batch_size = 0
            scenarios_data = []
            
            for scenario in scenarios:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                if test_mode and batch_size % 5 == 0:
                    if check_cancelled_callback and check_cancelled_callback():
                        logger.info(f"TEST MODE: Extraction cancelled during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="cancelled")
                        for scenario_record in scenarios_data:
                            yield scenario_record
                        return
                        
                    if check_paused_callback and check_paused_callback():
                        logger.info(f"TEST MODE: Extraction paused during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="paused")
                        for scenario_record in scenarios_data:
                            yield scenario_record
                        return

                try:
                    # Create normalized scenario record (eMoney uses PascalCase)
                    scenario_record = {
                        # Basic identification
                        'ScenarioID': scenario.get('ScenarioID'),
                        'PlanID': scenario.get('PlanID'),
                        'ClientID': scenario.get('ClientID'),
                        'HouseholdID': scenario.get('HouseholdID'),
                        
                        # Scenario details
                        'ScenarioName': scenario.get('ScenarioName'),
                        'ScenarioType': scenario.get('ScenarioType'),
                        'ScenarioDescription': scenario.get('ScenarioDescription'),
                        'ScenarioStatus': scenario.get('ScenarioStatus'),
                        
                        # Scenario classification
                        'IsBaseCase': scenario.get('IsBaseCase'),
                        'IsWhatIf': scenario.get('IsWhatIf'),
                        'IsCurrent': scenario.get('IsCurrent'),
                        'IsComparison': scenario.get('IsComparison'),
                        'ParentScenarioID': scenario.get('ParentScenarioID'),
                        
                        # Dates
                        'CreatedDate': scenario.get('CreatedDate'),
                        'ModifiedDate': scenario.get('ModifiedDate'),
                        'LastRunDate': scenario.get('LastRunDate'),
                        'EffectiveDate': scenario.get('EffectiveDate'),
                        
                        # Planning parameters
                        'StartYear': scenario.get('StartYear'),
                        'EndYear': scenario.get('EndYear'),
                        'PlanningHorizon': scenario.get('PlanningHorizon'),
                        'RetirementYear': scenario.get('RetirementYear'),
                        'ClientRetirementAge': scenario.get('ClientRetirementAge'),
                        'SpouseRetirementAge': scenario.get('SpouseRetirementAge'),
                        
                        # Life expectancy assumptions
                        'ClientLifeExpectancy': scenario.get('ClientLifeExpectancy'),
                        'SpouseLifeExpectancy': scenario.get('SpouseLifeExpectancy'),
                        'JointLifeExpectancy': scenario.get('JointLifeExpectancy'),
                        
                        # Economic assumptions
                        'InflationRate': scenario.get('InflationRate'),
                        'TaxRate': scenario.get('TaxRate'),
                        'FederalTaxRate': scenario.get('FederalTaxRate'),
                        'StateTaxRate': scenario.get('StateTaxRate'),
                        'CapitalGainsTaxRate': scenario.get('CapitalGainsTaxRate'),
                        
                        # Investment assumptions
                        'PreRetirementReturn': scenario.get('PreRetirementReturn'),
                        'PostRetirementReturn': scenario.get('PostRetirementReturn'),
                        'AssumedRateOfReturn': scenario.get('AssumedRateOfReturn'),
                        'StandardDeviation': scenario.get('StandardDeviation'),
                        'DownsideDeviation': scenario.get('DownsideDeviation'),
                        
                        # Monte Carlo simulation
                        'MonteCarloEnabled': scenario.get('MonteCarloEnabled'),
                        'MonteCarloIterations': scenario.get('MonteCarloIterations'),
                        'SuccessRate': scenario.get('SuccessRate'),
                        'ProbabilityOfSuccess': scenario.get('ProbabilityOfSuccess'),
                        'MedianOutcome': scenario.get('MedianOutcome'),
                        'WorstCaseOutcome': scenario.get('WorstCaseOutcome'),
                        'BestCaseOutcome': scenario.get('BestCaseOutcome'),
                        
                        # Financial outcomes
                        'ProjectedNetWorth': scenario.get('ProjectedNetWorth'),
                        'FinalNetWorth': scenario.get('FinalNetWorth'),
                        'EstateValue': scenario.get('EstateValue'),
                        'TotalAssets': scenario.get('TotalAssets'),
                        'TotalLiabilities': scenario.get('TotalLiabilities'),
                        'LiquidAssets': scenario.get('LiquidAssets'),
                        
                        # Cash flow analysis
                        'TotalIncome': scenario.get('TotalIncome'),
                        'TotalExpenses': scenario.get('TotalExpenses'),
                        'NetCashFlow': scenario.get('NetCashFlow'),
                        'AnnualSurplusDeficit': scenario.get('AnnualSurplusDeficit'),
                        'CumulativeSurplusDeficit': scenario.get('CumulativeSurplusDeficit'),
                        
                        # Retirement income
                        'RetirementIncome': scenario.get('RetirementIncome'),
                        'SocialSecurityIncome': scenario.get('SocialSecurityIncome'),
                        'PensionIncome': scenario.get('PensionIncome'),
                        'PortfolioIncome': scenario.get('PortfolioIncome'),
                        'RentalIncome': scenario.get('RentalIncome'),
                        'OtherIncome': scenario.get('OtherIncome'),
                        
                        # Goal funding
                        'GoalsFunded': scenario.get('GoalsFunded'),
                        'GoalsNotFunded': scenario.get('GoalsNotFunded'),
                        'TotalGoalCost': scenario.get('TotalGoalCost'),
                        'FundedGoalCost': scenario.get('FundedGoalCost'),
                        'UnfundedGoalCost': scenario.get('UnfundedGoalCost'),
                        
                        # Comparison to base case
                        'DifferenceFromBase': scenario.get('DifferenceFromBase'),
                        'NetWorthChange': scenario.get('NetWorthChange'),
                        'SuccessRateChange': scenario.get('SuccessRateChange'),
                        
                        # Version and status
                        'Version': scenario.get('Version'),
                        'IsActive': scenario.get('IsActive'),
                        'IsArchived': scenario.get('IsArchived'),
                        'IsPublished': scenario.get('IsPublished'),
                        'IsLocked': scenario.get('IsLocked'),
                        
                        # Calculation metadata
                        'CalculationEngine': scenario.get('CalculationEngine'),
                        'EngineVersion': scenario.get('EngineVersion'),
                        'CalculationDuration': scenario.get('CalculationDuration'),
                        'LastCalculatedBy': scenario.get('LastCalculatedBy'),
                    }
                    
                    # Handle nested objects with JSON serialization
                    nested_fields = [
                        'CashFlowProjections', 'NetWorthProjections', 'Assumptions',
                        'Goals', 'IncomeStreams', 'ExpenseCategories', 'Accounts',
                        'TaxStrategies', 'WithdrawalStrategies', 'SavingsStrategies',
                        'CustomFields', 'Adjustments', 'Overrides', 'Notes',
                        'MonteCarloResults', 'SensitivityAnalysis', 'StressTests',
                        'ComparativeAnalysis', 'RiskMetrics', 'Timeline'
                    ]
                    
                    for json_field in nested_fields:
                        if scenario.get(json_field):
                            value = scenario.get(json_field)
                            if isinstance(value, (dict, list)):
                                scenario_record[json_field] = json.dumps(value)
                            else:
                                scenario_record[json_field] = value
                    
                    # Optionally fetch detailed projections
                    if include_cashflow or include_networth:
                        scenario_id = scenario.get('ScenarioID')
                        if scenario_id:
                            try:
                                detailed_scenario = api_service.get_scenario(
                                    scenario_id=scenario_id,
                                    include_cashflow=include_cashflow,
                                    include_networth=include_networth
                                )
                                
                                if include_cashflow and detailed_scenario.get('CashFlowProjections'):
                                    scenario_record['CashFlowProjections'] = json.dumps(
                                        detailed_scenario['CashFlowProjections']
                                    )
                                    
                                if include_networth and detailed_scenario.get('NetWorthProjections'):
                                    scenario_record['NetWorthProjections'] = json.dumps(
                                        detailed_scenario['NetWorthProjections']
                                    )
                            except Exception as detail_err:
                                logger.warning(f"Failed to fetch detailed projections for scenario {scenario_id}: {detail_err}")

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        scenario_record[meta_key] = meta_value
                    
                    scenarios_data.append(scenario_record)
                    total_records += 1
                    batch_size += 1
                    
                except Exception as record_err:
                    logger.error(f"Error processing scenario record: {record_err}")
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
            for scenario_record in scenarios_data:
                yield scenario_record
                
            logger.info(f"Processed {batch_size} scenarios (total: {total_records}) - batch {batch_counter}/{SCENARIO_MAX_BATCHES}")
            
            if should_save_checkpoint():
                save_checkpoint()
            
            # Check if we got fewer records than requested (end of data)
            if len(scenarios) < page_size:
                logger.info("Received partial page. Assuming end of results.")
                break
                
            # Move to next page
            page += 1
            
        except Exception as e:
            logger.error(f"Error extracting scenarios at page {page} - batch {batch_counter}: {e}")
            save_checkpoint(status="error")
            for scenario_record in scenarios_data:
                yield scenario_record
            raise
    
    logger.info(f"✓ Scenarios extraction complete: {total_records} records in {batch_counter} batches")
    save_checkpoint(status="completed")