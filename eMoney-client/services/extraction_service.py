import dlt
import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from models.models import JobStatus
from models.database import check_database_health
from utils import (
    deep_serialize,
    build_dataset_name,
    enhance_filters_with_metadata,
    build_dlt_env_vars,
    create_isolated_pipeline,
    run_pipeline_with_organization_lock,
    cleanup_pipeline_working_dir,
)
from .database_service import DatabaseService
from .data_source import create_data_source

from .job_service import JobService
from loki_logger import get_logger, log_business_event, log_security_event


class ExtractionService:
    """Service for orchestrating data extraction pipelines using DLT"""

    def __init__(self, config: Dict[str, Any], source_type: str = "emoney"):
        self.config = config
        self.source_type = source_type
        self.job_service = JobService()
        self.logger = get_logger(__name__)

        self._setup_dlt_environment()

        self.pipeline_name = f"{source_type}_extraction"
        self.destination = dlt.destinations.postgres()
        self.db_service = DatabaseService(self.pipeline_name, self.destination, self.config)

        self.logger.debug(
            "Extraction service initialized",
            extra={
                "operation": "service_init",
                "source_type": source_type,
                "pipeline_name": self.pipeline_name,
            },
        )

    def _setup_dlt_environment(self):
        """Set DLT environment variables from configuration"""
        try:
            dlt_env_vars = build_dlt_env_vars(self.config)

            for key, value in dlt_env_vars.items():
                if not os.environ.get(key):
                    os.environ[key] = value

            self.logger.debug(
                "DLT environment configured",
                extra={"operation": "dlt_env_setup", "vars_count": len(dlt_env_vars)},
            )

        except Exception as e:
            self.logger.error(
                "Failed to setup DLT environment",
                extra={"operation": "dlt_env_setup", "error": str(e)},
                exc_info=True,
            )

    def create_source_with_checkpoints(
        self,
        auth_config: Dict[str, Any],
        job_config: Dict[str, Any],
        filters: Dict[str, Any],
        job_id: str,
    ):
        """Create DLT data source with checkpointing support"""
        try:
            # Check for existing checkpoint
            resume_from = None
            latest_checkpoint = self.job_service.get_latest_checkpoint(job_id)

            if latest_checkpoint:
                # Transform checkpoint data to match the format expected by extraction functions
                entity_type = job_config.get("type")
                if isinstance(entity_type, list) and len(entity_type) > 0:
                    entity_type = entity_type[0]

                # Normalize entity_type to lowercase
                entity_type = entity_type.lower() if entity_type else "client"

                # Create the resume_from structure expected by extraction functions
                if latest_checkpoint.get("checkpoint_data"):
                    resume_from = {
                        entity_type: {
                            "records_processed": latest_checkpoint.get(
                                "records_processed", 0
                            ),
                            "checkpoint_data": latest_checkpoint.get(
                                "checkpoint_data", {}
                            ),
                        }
                    }
                    self.logger.info(
                        "Resuming from checkpoint",
                        extra={
                            "operation": "create_source",
                            "job_id": job_id,
                            "entity": entity_type,
                            "records_processed": latest_checkpoint.get(
                                "records_processed", 0
                            ),
                        },
                    )

            def checkpoint_callback(job_id_param: str, entity_data: Dict[str, Any]):
                """Save checkpoint during extraction"""
                try:
                    if not entity_data:
                        return

                    # entity_data structure: {'entity': 'clients', 'records_processed': 100, 'checkpoint_data': {...}}
                    checkpoint_data = {
                        "phase": entity_data.get("entity"),
                        "records_processed": entity_data.get("records_processed", 0),
                        "checkpoint_data": entity_data.get("checkpoint_data", {}),
                    }

                    self.job_service.save_checkpoint(job_id_param, checkpoint_data)
                    self.job_service.update_job_heartbeat(job_id_param)

                except Exception as e:
                    self.logger.warning(
                        "Checkpoint callback failed",
                        extra={"job_id": job_id_param, "error": str(e)},
                    )

            def check_paused_callback():
                """Check if the job has been paused"""
                job_status = self.job_service.get_job_status(job_id)
                if job_status and job_status.get("status") == JobStatus.PAUSED.value:
                    self.logger.info(
                        "Job pause detected during extraction",
                        extra={"operation": "create_source", "job_id": job_id},
                    )
                    return True
                return False

            def check_cancelled_callback():
                """Check if the job has been cancelled"""
                job_status = self.job_service.get_job_status(job_id)
                if job_status and job_status.get("status") == JobStatus.CANCELLED.value:
                    self.logger.info(
                        "Job cancellation detected during extraction",
                        extra={"operation": "create_source", "job_id": job_id},
                    )
                    return True
                return False

            # Create the data source with checkpoint support
            return create_data_source(
                job_config=job_config,
                auth_config=auth_config,
                filters=filters,
                checkpoint_callback=checkpoint_callback,
                resume_from=resume_from,
                check_paused_callback=check_paused_callback,
                check_cancelled_callback=check_cancelled_callback,
            )

        except Exception as e:
            self.logger.error(
                "Failed to create data source",
                extra={
                    "operation": "create_source",
                    "job_id": job_id,
                    "error": str(e),
                    "exception": {
                        "type": type(e).__name__,
                        "message": str(e),
                    },
                },
            )
            raise

    async def start_scan(self, request_config: Dict[str, Any]) -> Dict[str, Any]:
        """Start new data extraction scan"""
        scan_id = request_config.get("scanId", "unknown")

        try:
            self.logger.info(
                "Scan initiation requested",
                extra={
                    "operation": "start_scan",
                    "scan_id": scan_id,
                    "organization_id": request_config.get("organizationId"),
                },
            )

            # Start background task
            asyncio.create_task(self._execute_scan_with_setup(request_config))

            log_business_event(
                self.logger,
                "scan_initiated",
                scan_id=scan_id,
                organization_id=request_config.get("organizationId"),
            )

            return {
                "success": True,
                "scanId": scan_id,
                "status": "initializing",
                "message": f"{self.source_type} extraction scan initiated successfully",
            }

        except Exception as e:
            self.logger.error(
                "Failed to initiate scan",
                extra={"operation": "start_scan", "scan_id": scan_id, "error": str(e)},
                exc_info=True,
            )
            return {
                "success": False,
                "scanId": scan_id,
                "error": str(e),
                "message": "Failed to initiate scan",
            }

    async def _execute_scan_with_setup(self, request_config: Dict[str, Any]):
        """Handle setup validation and execution in background"""
        scan_id = request_config.get("scanId", "unknown")

        try:
            self.logger.info(
                "Starting scan setup",
                extra={"operation": "scan_setup", "scan_id": scan_id},
            )

            # Database health check
            if not check_database_health():
                error_msg = "Database is not available"
                self.logger.error(
                    "Database health check failed",
                    extra={"operation": "scan_setup", "scan_id": scan_id},
                )
                try:
                    job = self.job_service.create_job(request_config)
                    self.job_service.fail_job(scan_id, error_msg)
                except Exception:
                    pass
                return

            # Check for existing job
            existing_job = self.job_service.get_job(scan_id)
            if existing_job:
                if existing_job["status"] == JobStatus.CRASHED.value:
                    self.job_service.update_job_status(scan_id, JobStatus.RESUMING)
                    self.logger.info(
                        "Resuming crashed job",
                        extra={"operation": "scan_setup", "scan_id": scan_id},
                    )
                else:
                    self.logger.warning(
                        "Job already exists",
                        extra={
                            "operation": "scan_setup",
                            "scan_id": scan_id,
                            "existing_status": existing_job["status"],
                        },
                    )
                    return
            else:
                # Create job entry
                existing_job = self.job_service.create_job(request_config)
                self.logger.info(
                    "Job created successfully",
                    extra={"operation": "scan_setup", "scan_id": scan_id},
                )

            # Update status and start execution
            self.job_service.update_job_status(scan_id, JobStatus.RUNNING)
            self.job_service.update_job_heartbeat(scan_id)

            self.logger.info(
                "Setup completed, starting extraction",
                extra={"operation": "scan_setup", "scan_id": scan_id},
            )

            await self._execute_scan(scan_id)

        except Exception as e:
            self.logger.error(
                "Setup failed",
                extra={"operation": "scan_setup", "scan_id": scan_id, "error": str(e)},
                exc_info=True,
            )

            try:
                if not self.job_service.get_job(scan_id):
                    self.job_service.create_job(request_config)

                error_metadata = {
                    "error_details": {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "failed_at": datetime.now(timezone.utc).isoformat(),
                        "failure_stage": "setup",
                    }
                }
                self.job_service.fail_job(scan_id, str(e), error_metadata)
            except Exception:
                pass

    async def _execute_scan(self, job_id: str):
        """Execute the data extraction pipeline with isolated pipeline to prevent race conditions"""
        working_dir = None
        try:
            job = self.job_service.get_job(job_id, decrypt=True)
            if not job:
                self.logger.error(
                    "Job not found for execution",
                    extra={"operation": "execute_scan", "job_id": job_id},
                )
                return

            self.logger.info(
                "Starting pipeline execution",
                extra={"operation": "execute_scan", "job_id": job_id},
            )

            job_config = job["config"] or {}
            auth_config = job_config.get("auth", {})
            filters = job_config.get("filters", {})

            # Add organizationId and scanId to filters for data source
            filters["organization_id"] = job["organizationId"]
            filters["scan_id"] = job["scanId"]

            # Create source functions
            source_functions = self.create_source_with_checkpoints(
                auth_config=auth_config,
                job_config=job_config,
                filters=filters,
                job_id=job["scanId"],
            )

            # Create isolated pipeline to prevent race conditions
            pipeline, working_dir = create_isolated_pipeline(
                scan_id=job["scanId"],
                organization_id=job["organizationId"],
                config=self.config
            )

            self.job_service.update_job_heartbeat(job_id)

            # Run pipeline with organization-level lock to prevent database conflicts
            self.logger.info(
                "DLT pipeline started with isolated configuration",
                extra={
                    "operation": "execute_scan", 
                    "job_id": job_id,
                    "pipeline_name": pipeline.pipeline_name,
                    "working_dir": str(working_dir)
                },
            )

            run_pipeline_with_organization_lock(
                pipeline=pipeline,
                source_functions=source_functions,
                organization_id=job["organizationId"]
            )

            # Check job status after pipeline completion
            current_job = self.job_service.get_job(job_id)
            if not current_job:
                self.logger.error(
                    "Job disappeared during execution",
                    extra={"operation": "execute_scan", "job_id": job_id},
                )
                return

            current_status = current_job.get("status")

            # Don't mark as completed if job was cancelled
            if current_status == JobStatus.CANCELLED.value:
                self.logger.info(
                    "Job was cancelled during execution, keeping cancelled status",
                    extra={"operation": "execute_scan", "job_id": job_id},
                )
                return

            # Don't mark as completed if job was paused
            if current_status == JobStatus.PAUSED.value:
                self.logger.info(
                    "Job was paused during execution, keeping paused status",
                    extra={"operation": "execute_scan", "job_id": job_id},
                )
                return

            # Check if the latest checkpoint indicates a pause
            latest_checkpoint = self.job_service.get_latest_checkpoint(job_id)
            if latest_checkpoint:
                checkpoint_phase = latest_checkpoint.get("phase", "")
                if "paused" in checkpoint_phase.lower():
                    self.logger.info(
                        "Pipeline stopped due to pause, keeping paused status",
                        extra={
                            "operation": "execute_scan",
                            "job_id": job_id,
                            "checkpoint_phase": checkpoint_phase,
                        },
                    )
                    # Ensure job status is paused
                    self.job_service.update_job_status(job_id, JobStatus.PAUSED)
                    return

            # Get final record count
            records_extracted = (
                latest_checkpoint.get("recordsProcessed", 0)
                if latest_checkpoint
                else 0
            )

            # Build completion metadata
            metadata = {
                "pipeline_name": pipeline.pipeline_name,
                "destination": "postgres",
                "dataset_name": pipeline.dataset_name,
                "source_type": self.source_type,
                "extraction_summary": {"total_records": records_extracted},
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }

            # Only complete if pipeline actually finished normally
            self.job_service.complete_job(job_id, records_extracted, metadata)

            self.logger.info(
                "Scan completed successfully",
                extra={
                    "operation": "execute_scan",
                    "job_id": job_id,
                    "records_extracted": records_extracted,
                },
            )

            log_business_event(
                self.logger,
                "scan_completed",
                job_id=job_id,
                records_extracted=records_extracted,
            )

        except Exception as e:
            self.logger.error(
                "Scan execution failed",
                extra={"operation": "execute_scan", "job_id": job_id, "error": str(e)},
                exc_info=True,
            )

            error_metadata = {
                "error_details": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                }
            }
            self.job_service.fail_job(job_id, str(e), error_metadata)

            log_business_event(self.logger, "scan_failed", job_id=job_id, error=str(e))

        finally:
            # Always cleanup pipeline working directory
            if working_dir:
                cleanup_pipeline_working_dir(working_dir)

    def pause_scan(self, scan_id: str) -> Dict[str, Any]:
        return self.job_service.pause_job(scan_id)

    async def resume_scan(self, scan_id: str) -> Dict[str, Any]:
        result = self.job_service.resume_job(scan_id)
        if result.get("success"):
            # Start background execution task
            asyncio.create_task(self._execute_scan(scan_id))
        return result

    def get_scan_status(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan status"""
        return self.job_service.get_job_status(scan_id)

    def cancel_scan(self, scan_id: str) -> Dict[str, Any]:
        """Cancel a running scan"""
        result = self.job_service.cancel_job(scan_id)

        if result.get("success"):
            self.logger.info(
                "Scan cancelled", extra={"operation": "cancel_scan", "scan_id": scan_id}
            )
            log_business_event(self.logger, "scan_cancelled", scan_id=scan_id)

        return result

    def list_scans(
        self, organization_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List scans with optional filtering"""
        try:
            scans = self.job_service.list_jobs(organization_id, limit, offset)

            self.logger.debug(
                "Scans listed",
                extra={
                    "operation": "list_scans",
                    "count": len(scans),
                    "organization_id": organization_id,
                },
            )

            return scans

        except Exception as e:
            self.logger.error(
                "Error listing scans",
                extra={"operation": "list_scans", "error": str(e)},
                exc_info=True,
            )
            return []

    def detect_crashed_jobs(self, timeout_minutes: int = 10) -> List[str]:
        """Detect crashed jobs"""
        try:
            crashed_jobs = self.job_service.detect_crashed_jobs(timeout_minutes)

            if crashed_jobs:
                self.logger.warning(
                    "Crashed jobs detected",
                    extra={
                        "operation": "detect_crashed_jobs",
                        "crashed_count": len(crashed_jobs),
                        "timeout_minutes": timeout_minutes,
                    },
                )

                log_security_event(
                    self.logger,
                    "crashed_jobs_detected",
                    severity="WARNING",
                    crashed_count=len(crashed_jobs),
                )

            return [job.get("scanId") for job in crashed_jobs]

        except Exception as e:
            self.logger.error(
                "Error detecting crashed jobs",
                extra={"operation": "detect_crashed_jobs", "error": str(e)},
                exc_info=True,
            )
            return []

    def cleanup_old_scans(self, days_old: int = 7) -> int:
        """Remove old scan results"""
        try:
            result = self.job_service.cleanup_old_jobs(days_old)
            deleted_count = result.get("deleted_jobs", 0)

            self.logger.info(
                "Old scans cleaned up",
                extra={
                    "operation": "cleanup_old_scans",
                    "deleted_count": deleted_count,
                    "days_old": days_old,
                },
            )

            log_security_event(
                self.logger,
                "scans_cleanup_performed",
                deleted_count=deleted_count,
                days_old=days_old,
            )

            return deleted_count

        except Exception as e:
            self.logger.error(
                "Error during cleanup",
                extra={"operation": "cleanup_old_scans", "error": str(e)},
                exc_info=True,
            )
            return 0

    def get_scan_statistics(
        self, organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get scan statistics"""
        return self.job_service.get_job_statistics(organization_id)

    def get_scan_results(
        self, scan_id: str, table_name: str = "client", limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """Get scan results with pagination"""
        try:
            job = self.job_service.get_job(scan_id)
            if not job:
                return {"success": False, "message": "Scan not found"}

            if job["status"] != JobStatus.COMPLETED.value:
                return {
                    "success": False,
                    "message": f"Scan not completed. Current status: {job['status']}",
                }

            metadata = job.get("metadata", {})
            dataset_name = metadata.get("dataset_name")

            if not dataset_name:
                return {
                    "success": False,
                    "message": "Dataset name not found in scan metadata",
                }

            result = self.db_service.get_scan_data(
                dataset_name, table_name, limit, offset, config=self.config
            )

            if result["success"]:
                result["data"]["scanId"] = scan_id
                result["data"] = deep_serialize(result["data"])

                self.logger.debug(
                    "Scan results retrieved",
                    extra={
                        "operation": "get_scan_results",
                        "scan_id": scan_id,
                        "table_name": table_name,
                        "records_returned": len(result["data"].get("results", [])),
                    },
                )

            return result

        except Exception as e:
            self.logger.error(
                "Error getting scan results",
                extra={
                    "operation": "get_scan_results",
                    "scan_id": scan_id,
                    "table_name": table_name,
                    "error": str(e),
                },
                exc_info=True,
            )
            return {
                "success": False,
                "message": f"Failed to retrieve scan results: {str(e)}",
            }

    def get_available_tables(self, scan_id: str) -> Dict[str, Any]:
        """Get available tables for a completed scan"""
        try:
            job = self.job_service.get_job(scan_id)
            if not job:
                return {"success": False, "message": "Scan not found"}

            if job["status"] != JobStatus.COMPLETED.value:
                return {
                    "success": False,
                    "message": f"Scan not completed. Current status: {job['status']}",
                }

            metadata = job.get("metadata", {})
            dataset_name = metadata.get("dataset_name")
            table_info = metadata.get("table_record_counts", {})

            if not dataset_name:
                return {
                    "success": False,
                    "message": "Dataset name not found in scan metadata",
                }

            tables = self.db_service.get_tables_with_counts(dataset_name, table_info, config=self.config)

            self.logger.debug(
                "Available tables retrieved",
                extra={
                    "operation": "get_available_tables",
                    "scan_id": scan_id,
                    "table_count": len(tables),
                },
            )

            return {
                "success": True,
                "data": deep_serialize(
                    {
                        "scanId": scan_id,
                        "datasetName": dataset_name,
                        "tables": tables,
                        "totalTables": len(tables),
                    }
                ),
            }

        except Exception as e:
            self.logger.error(
                "Error getting available tables",
                extra={
                    "operation": "get_available_tables",
                    "scan_id": scan_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            return {
                "success": False,
                "message": f"Failed to retrieve available tables: {str(e)}",
            }

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get DLT pipeline configuration info"""
        try:
            pipeline = dlt.pipeline(
                pipeline_name=self.pipeline_name, destination=self.destination
            )

            return deep_serialize(
                {
                    "pipeline_name": pipeline.pipeline_name,
                    "destination_type": "postgres",
                    "source_type": self.source_type,
                    "database_health": check_database_health(),
                    "supports_checkpoints": True,
                    "isolation_enabled": True,
                }
            )

        except Exception as e:
            self.logger.warning(
                "Pipeline info retrieval failed",
                extra={"operation": "get_pipeline_info", "error": str(e)},
            )
            return {
                "error": str(e),
                "pipeline_name": self.pipeline_name,
                "destination_type": "postgres",
                "source_type": self.source_type,
                "database_health": check_database_health(),
                "isolation_enabled": True,
            }

    def remove_scan(self, scan_id: str) -> Dict[str, Any]:
        """Remove scan and associated data"""
        try:
            job = self.job_service.get_job(scan_id)
            if not job:
                return {"success": False, "message": "Scan not found"}

            if job["status"] in ["running", "pending"]:
                return {
                    "success": False,
                    "message": "Cannot remove active scan. Please cancel first.",
                }

            # Get dataset for cleanup
            metadata = job.get("metadata", {})
            dataset_name = metadata.get("dataset_name")

            tables_removed = 0
            if dataset_name:
                tables_removed = self.db_service.remove_dataset_tables(
                    dataset_name, scan_id, config=self.config
                )

            # Remove job record
            removed = self.job_service.remove_job(scan_id)

            if removed:
                self.logger.info(
                    "Scan removed successfully",
                    extra={
                        "operation": "remove_scan",
                        "scan_id": scan_id,
                        "tables_removed": tables_removed,
                    },
                )

                log_business_event(self.logger, "scan_removed", scan_id=scan_id)

                return {
                    "success": True,
                    "message": f"Scan {scan_id} successfully removed",
                    "data": {
                        "scanId": scan_id,
                        "tablesRemoved": tables_removed,
                        "metadataRemoved": True,
                    },
                }
            else:
                return {"success": False, "message": "Failed to remove scan metadata"}

        except Exception as e:
            self.logger.error(
                "Error removing scan",
                extra={"operation": "remove_scan", "scan_id": scan_id, "error": str(e)},
                exc_info=True,
            )
            return {"success": False, "message": f"Failed to remove scan: {str(e)}"}

    def get_service_statistics(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        try:
            job_stats = self.job_service.get_job_statistics()
            db_info = self.db_service.get_database_info(config=self.config)

            stats = {
                "service": {
                    "name": "emoney_extraction_service",
                    "source_type": self.source_type,
                    "uptime": datetime.now(timezone.utc).isoformat(),
                    "race_condition_fix_enabled": True,
                },
                "jobs": job_stats,
                "database": db_info,
                "performance": {
                    "total_records_extracted": job_stats.get(
                        "total_records_extracted", 0
                    )
                },
            }

            self.logger.debug(
                "Service statistics retrieved",
                extra={
                    "operation": "get_service_statistics",
                    "total_jobs": job_stats.get("total_jobs", 0),
                },
            )

            return deep_serialize(stats)

        except Exception as e:
            self.logger.error(
                "Error getting service statistics",
                extra={"operation": "get_service_statistics", "error": str(e)},
                exc_info=True,
            )
            return {
                "error": str(e),
                "service": {
                    "name": "emoney_extraction_service",
                    "status": "error",
                },
            }