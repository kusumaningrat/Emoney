# extract_cashflow.py
import logging
import time
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config


def extract_cashflow(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract cash flow data from Financial Planning Core API

    Yields cash flow records with normalized field names,
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
    CASHFLOW_CHECKPOINT_FREQUENCY = config.CASHFLOW_CHECKPOINT_FREQUENCY
    CASHFLOW_PAUSE_CHECK_FREQUENCY = config.CASHFLOW_PAUSE_CHECK_FREQUENCY
    CASHFLOW_CANCEL_CHECK_FREQUENCY = config.CASHFLOW_CANCEL_CHECK_FREQUENCY
    CASHFLOW_MAX_BATCHES = config.CASHFLOW_MAX_BATCHES

    # Check if we're in test mode and get test delay settings
    test_mode = getattr(config, "TESTING", False)
    test_batch_delay = getattr(config, "TEST_BATCH_DELAY_SECONDS", 5)
    test_record_delay = getattr(config, "TEST_RECORD_DELAY_SECONDS", 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Cash Flow for org: {organization_id}")
    logger.info("=" * 60)

    if test_mode:
        logger.info(
            f"Running in TEST MODE with batch delay={test_batch_delay}s, "
            f"record delay={test_record_delay}s"
        )

    skip = 0
    limit = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "cashflow"
    batch_counter = 0

    # Extract plan_id from filters (required for cash flow)
    plan_id = filters.get("plan_id") if filters else None
    if not plan_id:
        logger.error("plan_id is required for cash flow extraction")
        raise ValueError("plan_id is required for cash flow extraction")

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

            # Resume from the last offset
            if checkpoint_data and "offset" in checkpoint_data:
                skip = checkpoint_data["offset"]
                total_records = entity_checkpoint.get("records_processed", 0)
                batch_counter = checkpoint_data.get("batch_counter", 0)
                logger.info(
                    f"Resuming {entity} extraction from offset {skip} "
                    f"(batch {batch_counter})"
                )

    def save_checkpoint(status="in_progress"):
        if checkpoint_callback:
            try:
                checkpoint_data = {
                    "entity": entity,
                    "records_processed": total_records,
                    "checkpoint_data": {
                        "offset": skip,
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
        return batch_counter % CASHFLOW_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % CASHFLOW_PAUSE_CHECK_FREQUENCY == 0

    def should_save_checkpoint():
        return batch_counter % CASHFLOW_CHECKPOINT_FREQUENCY == 0

    cashflow_data = []  # Temporary storage for batched cash flow records

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
        if batch_counter > CASHFLOW_MAX_BATCHES:
            logger.warning(
                f"Extraction of {entity} reached maximum batch limit "
                f"({CASHFLOW_MAX_BATCHES})"
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
                f"Fetching cash flow (skip: {skip}, limit: {limit}) - "
                f"batch {batch_counter}/{CASHFLOW_MAX_BATCHES}..."
            )

            response = api_service.get_cashflow(
                plan_id=plan_id, skip=skip, limit=limit, filters=filters
            )

            # Handle different response formats
            if isinstance(response, dict):
                if "cashflow" in response:
                    cashflows = response.get("cashflow", [])
                elif "Data" in response:
                    cashflows = response.get("Data", [])
                elif "results" in response:
                    cashflows = response.get("results", [])
                else:
                    cashflows = []
            else:
                cashflows = response if isinstance(response, list) else []

            if not cashflows:
                logger.info("No more cash flow records found")
                break

            batch_size = 0
            cashflow_data = []  # Clear the temporary storage for this batch

            for cashflow in cashflows:
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
                        for cf_record in cashflow_data:
                            yield cf_record
                        return

                    if check_paused_callback and check_paused_callback():
                        logger.info(
                            f"TEST MODE: Extraction paused during record processing "
                            f"at batch {batch_counter}, record {batch_size}"
                        )
                        save_checkpoint(status="paused")
                        for cf_record in cashflow_data:
                            yield cf_record
                        return

                try:
                    # Create normalized record for cash flow
                    cf_record = {
                        "id": cashflow.get("id"),
                        "plan_id": cashflow.get("planId") or cashflow.get("plan_id"),
                        "scenario_id": cashflow.get("scenarioId") or cashflow.get("scenario_id"),
                        "year": cashflow.get("year"),
                        "month": cashflow.get("month"),
                        "period": cashflow.get("period"),
                        "income_total": cashflow.get("incomeTotal") or cashflow.get("income_total"),
                        "expense_total": cashflow.get("expenseTotal") or cashflow.get("expense_total"),
                        "net_cashflow": cashflow.get("netCashflow") or cashflow.get("net_cashflow"),
                        "beginning_balance": cashflow.get("beginningBalance") or cashflow.get("beginning_balance"),
                        "ending_balance": cashflow.get("endingBalance") or cashflow.get("ending_balance"),
                        "investment_contribution": cashflow.get("investmentContribution") or cashflow.get("investment_contribution"),
                        "investment_withdrawal": cashflow.get("investmentWithdrawal") or cashflow.get("investment_withdrawal"),
                        "debt_payment": cashflow.get("debtPayment") or cashflow.get("debt_payment"),
                        "tax_amount": cashflow.get("taxAmount") or cashflow.get("tax_amount"),
                        "created_date": cashflow.get("createdDate") or cashflow.get("created_date"),
                    }

                    # Handle nested/complex fields
                    if cashflow.get("income_breakdown"):
                        cf_record["income_breakdown"] = json.dumps(
                            cashflow.get("income_breakdown")
                        )

                    if cashflow.get("expense_breakdown"):
                        cf_record["expense_breakdown"] = json.dumps(
                            cashflow.get("expense_breakdown")
                        )

                    if cashflow.get("metadata"):
                        cf_record["metadata"] = json.dumps(cashflow.get("metadata"))

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        cf_record[meta_key] = meta_value

                    cashflow_data.append(cf_record)
                    total_records += 1
                    batch_size += 1

                except Exception as record_err:
                    logger.error(f"Error processing cash flow record: {record_err}")
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
            for cf_record in cashflow_data:
                yield cf_record

            logger.info(
                f"Processed {batch_size} cash flow records (total: {total_records}) - "
                f"batch {batch_counter}/{CASHFLOW_MAX_BATCHES}"
            )

            # Save checkpoint based on batch counter
            if should_save_checkpoint():
                save_checkpoint()

            if len(cashflows) < limit:
                break

            skip += len(cashflows)

        except Exception as e:
            logger.error(
                f"Error extracting cash flow at offset {skip} - "
                f"batch {batch_counter}: {e}"
            )
            save_checkpoint(status="error")
            # Yield any processed records before raising the exception
            for cf_record in cashflow_data:
                yield cf_record
            raise

    logger.info(
        f"✓ Cash Flow extraction complete: {total_records} records in "
        f"{batch_counter} batches"
    )
    save_checkpoint(status="completed")