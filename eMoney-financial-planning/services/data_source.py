import dlt
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from loki_logger import get_logger, log_business_event, log_security_event

from config import get_config

# Import extraction functions from sources folder
from .sources.extract_plans import extract_plans
from .sources.extract_goals import extract_goals
from .sources.extract_scenarios import extract_scenarios
from .sources.extract_cashflow import extract_cashflow
from .sources.extract_networth import extract_networth
from .api_service import APIService


def create_data_source(
    job_config: Dict[str, Any],
    auth_config: Dict[str, Any],
    filters: Dict[str, Any],
    checkpoint_callback: Optional[Callable] = None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_paused_callback: Optional[Callable] = None,
    check_cancelled_callback: Optional[Callable] = None,
):
    """
    Create DLT source for eMoney Financial Plan extraction - processes one entity at a time

    Args:
        job_config: Job configuration containing entity type to extract
        auth_config: Authentication config
        filters: Extraction filters and configuration
        checkpoint_callback: Function to save checkpoints during extraction
        resume_from: Resume state from previous checkpoint
        check_paused_callback: Function to check if job is paused
        check_cancelled_callback: Function to check if job is cancelled
    """
    logger = get_logger(__name__)
    config = get_config()
    api_service = APIService(base_url=config.EMONEY_API_BASE_URL)

    # Get the single entity type to extract
    entity_type = job_config.get("type")[0]  # Expecting a list with one entity type

    logging.info(f"Creating data source for entity type: {entity_type}")

    # Get job_id and organization_id from filters
    job_id = filters.get("scan_id", "unknown")
    organization_id = filters.get("organization_id", "unknown")

    # Common metadata for all extractions
    extraction_metadata = {
        "_extracted_at": datetime.now(timezone.utc).isoformat(),
        "_scan_id": job_id,
        "_tenant_id": organization_id,
    }

    # Authenticate with eMoney API using OAuth2
    # api_service.authenticate(auth_config)

    # Check if entity was already completed in a previous run
    if resume_from:
        entity_data = resume_from.get(entity_type, {})
        checkpoint_data = entity_data.get("checkpoint_data", {})

        if checkpoint_data.get("status") == "completed":
            logger.info(f"Entity '{entity_type}' was already completed in previous run")
            return []

    # Extract function mapping - all lowercase for consistency
    extractors = {
        "plan": (extract_plans, "plan_id"),
        "goal": (extract_goals, "goal_id"),
        "scenario": (extract_scenarios, "scenario_id"),
        "cashflow": (extract_cashflow, "cashflow_id"),
        "networth": (extract_networth, "networth_id"),
    }

    # Normalize entity_type to lowercase
    entity_type_normalized = entity_type.lower()

    # Use "plan" as default for unknown entity types
    if entity_type_normalized not in extractors:
        logger.warning(f"Unknown entity type: {entity_type}, defaulting to 'plan'")
        entity_type_normalized = "plan"

    # Get the appropriate extractor function and primary key
    extractor_func, primary_key = extractors[entity_type_normalized]

    # Log security event for beginning extraction
    log_security_event(
        logger,
        "DATA_EXTRACTION_STARTED",
        entity_type=entity_type_normalized,
        job_id=job_id,
        organization_id=organization_id,
    )

    # Define column hints to ensure primary key is recognized correctly
    column_hints = {
        primary_key: {
            "name": primary_key,
            "data_type": "text",
            "nullable": False,
            "primary_key": True
        }
    }

    # Create and return the resource
    @dlt.resource(
        name=entity_type_normalized,
        write_disposition="replace",
        primary_key=primary_key,
        columns=column_hints
    )
    def extract_resource():
        """Extract the specified entity type"""
        try:
            # Log business event for extraction
            log_business_event(
                logger,
                "EXTRACTION_IN_PROGRESS",
                entity_type=entity_type_normalized,
                job_id=job_id,
            )

            return extractor_func(
                api_service=api_service,
                extraction_metadata=extraction_metadata,
                checkpoint_callback=checkpoint_callback,
                filters=filters,
                resume_from=resume_from,
                check_cancelled_callback=check_cancelled_callback,
                check_paused_callback=check_paused_callback,
            )
        except Exception as e:
            logger.error(f"Error extracting {entity_type_normalized}: {str(e)}")

            # Log error event
            log_business_event(
                logger,
                "EXTRACTION_ERROR",
                entity_type=entity_type_normalized,
                error=str(e),
                job_id=job_id,
            )

            raise

    return [extract_resource()]