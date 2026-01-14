# extract_networth.py
import logging
import time
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config


def extract_networth(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract net worth data from Financial Planning Core API

    Yields net worth records with normalized field names,
    with extraction metadata added.

    Args:
        api_service: API service client instance
        extraction_metadata: Metadata to attach to all records
        checkpoint_callback: Function to call for saving extraction progress
        filters: Extraction filters and configuration
        resume_from: Resume state from previous extraction checkpoint
        check_cancelled_callback: Function to check if job was cancelled
        check_paused_callback: Function to check if job was paused
    """
    logger = logging.getLogger(__name__)

    job_id = extraction_metadata.get("_scan_id", "unknown")
    organization_id = extraction_metadata.get("_tenant_id", "unknown")

    config = get_config()
    NETWORTH_CHECKPOINT_FREQUENCY = config.NETWORTH_CHECKPOINT_FREQUENCY
    NETWORTH_PAUSE_CHECK_FREQUENCY = config.NETWORTH_PAUSE_CHECK_FREQUENCY
    NETWORTH_CANCEL_CHECK_FREQUENCY = config.NETWORTH_CANCEL_CHECK_FREQUENCY
    NETWORTH_MAX_BATCHES = config.NETWORTH_MAX_BATCHES

    # Check if we're in test mode and get test delay settings
    test_mode = getattr(config, "TESTING", False)
    test_batch_delay = getattr(config, "TEST_BATCH_DELAY_SECONDS", 5)
    test_record_delay = getattr(config, "TEST_RECORD_DELAY_SECONDS", 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Net Worth for org: {organization_id}")
    logger.info("=" * 60)

    if test_mode:
        logger.info(
            f"Running in TEST MODE with batch delay={test_batch_delay}s, "
            f"record delay={test_record_delay}s"
        )

    page = 1
    page_size = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "networth"
    batch_counter = 0

    # Prepare API filters (plan_id, scenario_id, year, etc.)
    api_filters = {}
    if filters:
        # Copy filters that should be passed to the API
        for key in ["plan_id", "scenario_id", "year", "month", "date"]:
            if key in filters:
                api_filters[key] = filters[key]

    # Log filter information
    if api_filters:
        logger.info(f"Applying filters: {api_filters}")
    else:
        logger.info("No filters applied - fetching all networth records")

    # Check if resuming from a previous state
    if resume_from and isinstance(resume_from, dict):
        entity_checkpoint = resume_from.get(entity)
        if entity_checkpoint:
            checkpoint_data = entity_checkpoint.get("checkpoint_data", {})

            # Check if the job was completed in a previous run
            if checkpoint_data and checkpoint_data.get("status") == "completed":
                logger.info(
                    f"Entity '{entity}' was already completed in previous run"
                )
                return

            # Check if the job was paused in a previous run
            if checkpoint_data and checkpoint_data.get("status") == "paused":
                logger.info(f"Resuming {entity} extraction from paused state")

            # Resume from the last page
            if checkpoint_data and "page" in checkpoint_data:
                page = checkpoint_data["page"]
                total_records = entity_checkpoint.get("records_processed", 0)
                batch_counter = checkpoint_data.get("batch_counter", 0)
                logger.info(
                    f"Resuming {entity} extraction from page {page} "
                    f"(batch {batch_counter})"
                )

    def save_checkpoint(status="in_progress"):
        if checkpoint_callback:
            try:
                checkpoint_data = {
                    "entity": entity,
                    "records_processed": total_records,
                    "checkpoint_data": {
                        "page": page,
                        "status": status,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "batch_counter": batch_counter,
                    },
                }
                checkpoint_callback(job_id, checkpoint_data)
                logger.info(
                    f"Checkpoint saved: {total_records} {entity} with status "
                    f"'{status}' at batch {batch_counter}"
                )
            except Exception as e:
                logger.warning(f"Failed to save checkpoint: {e}")

    def should_check_cancelled():
        return batch_counter % NETWORTH_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % NETWORTH_PAUSE_CHECK_FREQUENCY == 0

    def should_save_checkpoint():
        return batch_counter % NETWORTH_CHECKPOINT_FREQUENCY == 0

    networth_data = []  # Temporary storage for batched net worth records

    while True:
        batch_counter += 1

        # Add delay at batch level in test mode
        if test_mode and test_batch_delay > 0:
            logger.info(
                f"TEST MODE: Adding {test_batch_delay}s delay before batch "
                f"{batch_counter}"
            )
            time.sleep(test_batch_delay)

        # Safety cap to prevent infinite loops
        if batch_counter > NETWORTH_MAX_BATCHES:
            logger.warning(
                f"Extraction of {entity} reached maximum batch limit "
                f"({NETWORTH_MAX_BATCHES})"
            )
            save_checkpoint(status="max_batches_reached")
            break

        # Check for cancellation based on batch frequency
        if (
            should_check_cancelled()
            and check_cancelled_callback
            and check_cancelled_callback()
        ):
            logger.info(
                f"Extraction of {entity} cancelled by user at batch {batch_counter}"
            )
            save_checkpoint(status="cancelled")
            break

        # Check for pause based on batch frequency
        if (
            should_check_paused()
            and check_paused_callback
            and check_paused_callback()
        ):
            logger.info(
                f"Extraction of {entity} paused by user at batch {batch_counter}"
            )
            save_checkpoint(status="paused")
            break

        try:
            logger.info(
                f"Fetching networth (page: {page}, pageSize: {page_size}) - "
                f"batch {batch_counter}/{NETWORTH_MAX_BATCHES}..."
            )

            # Call the updated API method
            response = api_service.get_networths(
                page=page, 
                page_size=page_size, 
                filters=api_filters if api_filters else None
            )

            # Handle different response formats
            if isinstance(response, dict):
                if "networth" in response:
                    networths = response.get("networth", [])
                elif "networths" in response:
                    networths = response.get("networths", [])
                elif "Data" in response:
                    networths = response.get("Data", [])
                elif "results" in response:
                    networths = response.get("results", [])
                else:
                    networths = []
            else:
                networths = response if isinstance(response, list) else []

            if not networths:
                logger.info("No more net worth records found")
                break

            batch_size = 0
            networth_data = []  # Clear the temporary storage for this batch

            for networth in networths:
                # Add delay at record level in test mode
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)

                # More frequent check for cancellation in test mode
                if test_mode and batch_size % 5 == 0:
                    if check_cancelled_callback and check_cancelled_callback():
                        logger.info(
                            f"TEST MODE: Extraction cancelled during record "
                            f"processing at batch {batch_counter}, record {batch_size}"
                        )
                        save_checkpoint(status="cancelled")
                        for nw_record in networth_data:
                            yield nw_record
                        return

                    if check_paused_callback and check_paused_callback():
                        logger.info(
                            f"TEST MODE: Extraction paused during record processing "
                            f"at batch {batch_counter}, record {batch_size}"
                        )
                        save_checkpoint(status="paused")
                        for nw_record in networth_data:
                            yield nw_record
                        return

                try:
                    # Create normalized record for net worth
                    nw_record = {
                        "networth_id": networth.get("NetWorthID") or networth.get("networth_id") or networth.get("netWorthId") or networth.get("id") or networth.get("ID"),
                        "plan_id": networth.get("PlanID") or networth.get("planId") or networth.get("plan_id"),
                        "scenario_id": networth.get("ScenarioID") or networth.get("scenarioId") or networth.get("scenario_id"),
                        "date": networth.get("Date") or networth.get("date"),
                        "year": networth.get("Year") or networth.get("year"),
                        "month": networth.get("Month") or networth.get("month"),
                        "total_assets": networth.get("TotalAssets") or networth.get("totalAssets") or networth.get("total_assets"),
                        "total_liabilities": networth.get("TotalLiabilities") or networth.get("totalLiabilities") or networth.get("total_liabilities"),
                        "net_worth": networth.get("NetWorth") or networth.get("netWorth") or networth.get("net_worth"),
                        "liquid_assets": networth.get("LiquidAssets") or networth.get("liquidAssets") or networth.get("liquid_assets"),
                        "investment_assets": networth.get("InvestmentAssets") or networth.get("investmentAssets") or networth.get("investment_assets"),
                        "real_estate_assets": networth.get("RealEstateAssets") or networth.get("realEstateAssets") or networth.get("real_estate_assets"),
                        "retirement_assets": networth.get("RetirementAssets") or networth.get("retirementAssets") or networth.get("retirement_assets"),
                        "other_assets": networth.get("OtherAssets") or networth.get("otherAssets") or networth.get("other_assets"),
                        "mortgage_liabilities": networth.get("MortgageLiabilities") or networth.get("mortgageLiabilities") or networth.get("mortgage_liabilities"),
                        "loan_liabilities": networth.get("LoanLiabilities") or networth.get("loanLiabilities") or networth.get("loan_liabilities"),
                        "credit_card_liabilities": networth.get("CreditCardLiabilities") or networth.get("creditCardLiabilities") or networth.get("credit_card_liabilities"),
                        "other_liabilities": networth.get("OtherLiabilities") or networth.get("otherLiabilities") or networth.get("other_liabilities"),
                        "created_date": networth.get("CreatedDate") or networth.get("createdDate") or networth.get("created_date"),
                    }

                    # Handle nested/complex fields
                    if networth.get("asset_breakdown") or networth.get("AssetBreakdown") or networth.get("assetBreakdown"):
                        nw_record["asset_breakdown"] = json.dumps(
                            networth.get("asset_breakdown") or networth.get("AssetBreakdown") or networth.get("assetBreakdown")
                        )

                    if networth.get("liability_breakdown") or networth.get("LiabilityBreakdown") or networth.get("liabilityBreakdown"):
                        nw_record["liability_breakdown"] = json.dumps(
                            networth.get("liability_breakdown") or networth.get("LiabilityBreakdown") or networth.get("liabilityBreakdown")
                        )

                    if networth.get("metadata") or networth.get("Metadata"):
                        nw_record["metadata"] = json.dumps(
                            networth.get("metadata") or networth.get("Metadata")
                        )

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        nw_record[meta_key] = meta_value

                    networth_data.append(nw_record)
                    total_records += 1
                    batch_size += 1

                except Exception as record_err:
                    logger.error(f"Error processing net worth record: {record_err}")
                    continue

            # Add delay after processing batch in test mode
            if test_mode and test_batch_delay > 0:
                logger.info(
                    f"TEST MODE: Adding {test_batch_delay/2}s delay after "
                    f"processing batch {batch_counter}"
                )
                time.sleep(test_batch_delay / 2)

                # Check again for cancellation/pause
                if check_cancelled_callback and check_cancelled_callback():
                    logger.info(
                        f"TEST MODE: Extraction cancelled after batch processing "
                        f"at batch {batch_counter}"
                    )
                    save_checkpoint(status="cancelled")
                    break

                if check_paused_callback and check_paused_callback():
                    logger.info(
                        f"TEST MODE: Extraction paused after batch processing "
                        f"at batch {batch_counter}"
                    )
                    save_checkpoint(status="paused")
                    break

            # Yield the processed records
            for nw_record in networth_data:
                yield nw_record

            logger.info(
                f"Processed {batch_size} net worth records (total: {total_records}) - "
                f"batch {batch_counter}/{NETWORTH_MAX_BATCHES}"
            )

            # Save checkpoint based on batch counter
            if should_save_checkpoint():
                save_checkpoint()

            # Check if we received a partial page (end of results)
            if len(networths) < page_size:
                logger.info("Received partial page. Assuming end of results.")
                break

            # Move to next page
            page += 1

        except Exception as e:
            logger.error(
                f"Error extracting net worth at page {page} - "
                f"batch {batch_counter}: {e}"
            )
            save_checkpoint(status="error")
            # Yield any processed records before raising the exception
            for nw_record in networth_data:
                yield nw_record
            raise

    logger.info(
        f"✓ Net Worth extraction complete: {total_records} records in "
        f"{batch_counter} batches"
    )
    save_checkpoint(status="completed")