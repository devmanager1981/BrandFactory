"""
Batch Processor for Global Brand Localizer

Manages batch generation of images for multiple regions with:
- Job queue management (sequential or parallel processing)
- Error isolation (one region failure doesn't stop others)
- Progress tracking
- Result aggregation
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import traceback

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Status of a batch job."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BatchJob:
    """Represents a single batch job for a region."""
    job_id: str
    region_id: str
    region_json: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return {
            "job_id": self.job_id,
            "region_id": self.region_id,
            "status": self.status.value,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class BatchResult:
    """Results from batch processing."""
    total_jobs: int
    completed: int
    failed: int
    jobs: List[BatchJob] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_jobs == 0:
            return 0.0
        return self.completed / self.total_jobs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "total_jobs": self.total_jobs,
            "completed": self.completed,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "jobs": [job.to_dict() for job in self.jobs]
        }


class BatchProcessor:
    """
    Manages batch processing of region-specific image generation.
    
    Key features:
    - Error isolation: One region failure doesn't stop others
    - Progress tracking: Monitor job status in real-time
    - Flexible processing: Sequential or parallel execution
    """
    
    def __init__(self, max_concurrent: int = 3):
        """
        Initialize Batch Processor.
        
        Args:
            max_concurrent: Maximum number of concurrent jobs (for parallel processing)
        """
        self.max_concurrent = max_concurrent
        self.jobs: List[BatchJob] = []
        logger.info(f"Batch Processor initialized (max_concurrent={max_concurrent})")
    
    def create_jobs(
        self,
        region_jsons: List[Dict[str, Any]]
    ) -> List[BatchJob]:
        """
        Create batch jobs from region JSONs.
        
        Args:
            region_jsons: List of region-specific JSONs
        
        Returns:
            List of BatchJob objects
        """
        jobs = []
        
        for idx, region_json in enumerate(region_jsons):
            region_id = region_json.get("metadata", {}).get("region_id", f"region_{idx}")
            
            job = BatchJob(
                job_id=f"job_{region_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                region_id=region_id,
                region_json=region_json
            )
            
            jobs.append(job)
        
        self.jobs = jobs
        logger.info(f"Created {len(jobs)} batch jobs")
        return jobs
    
    def process_batch_sequential(
        self,
        region_jsons: List[Dict[str, Any]],
        processor_func: Callable[[Dict[str, Any]], Any],
        progress_callback: Optional[Callable[[BatchJob], None]] = None
    ) -> BatchResult:
        """
        Process batch jobs sequentially (one at a time).
        
        Args:
            region_jsons: List of region-specific JSONs
            processor_func: Function to process each region JSON
            progress_callback: Optional callback for progress updates
        
        Returns:
            BatchResult with processing results
        """
        logger.info(f"Starting sequential batch processing ({len(region_jsons)} jobs)...")
        
        # Create jobs
        jobs = self.create_jobs(region_jsons)
        
        # Initialize result
        result = BatchResult(
            total_jobs=len(jobs),
            completed=0,
            failed=0,
            jobs=jobs,
            started_at=datetime.now()
        )
        
        # Process each job
        for job in jobs:
            try:
                logger.info(f"Processing job: {job.job_id} (region: {job.region_id})")
                
                # Update status
                job.status = JobStatus.IN_PROGRESS
                job.started_at = datetime.now()
                
                if progress_callback:
                    progress_callback(job)
                
                # Process the job
                job.result = processor_func(job.region_json)
                
                # Mark as completed
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()
                result.completed += 1
                
                logger.info(f"✓ Job completed: {job.job_id}")
                
            except Exception as e:
                # Error isolation: Log error but continue with other jobs
                logger.error(f"✗ Job failed: {job.job_id} - {str(e)}")
                logger.debug(traceback.format_exc())
                
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = datetime.now()
                result.failed += 1
                
                # Continue processing other jobs (implements Property 9: Batch Processing Isolation)
                continue
        
        result.completed_at = datetime.now()
        
        logger.info(f"✓ Batch processing complete: {result.completed}/{result.total_jobs} succeeded")
        return result
    
    async def process_batch_parallel(
        self,
        region_jsons: List[Dict[str, Any]],
        processor_func: Callable[[Dict[str, Any]], Any],
        progress_callback: Optional[Callable[[BatchJob], None]] = None
    ) -> BatchResult:
        """
        Process batch jobs in parallel (with concurrency limit).
        
        Args:
            region_jsons: List of region-specific JSONs
            processor_func: Function to process each region JSON
            progress_callback: Optional callback for progress updates
        
        Returns:
            BatchResult with processing results
        """
        logger.info(f"Starting parallel batch processing ({len(region_jsons)} jobs, max_concurrent={self.max_concurrent})...")
        
        # Create jobs
        jobs = self.create_jobs(region_jsons)
        
        # Initialize result
        result = BatchResult(
            total_jobs=len(jobs),
            completed=0,
            failed=0,
            jobs=jobs,
            started_at=datetime.now()
        )
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_job(job: BatchJob):
            """Process a single job with semaphore."""
            async with semaphore:
                try:
                    logger.info(f"Processing job: {job.job_id} (region: {job.region_id})")
                    
                    # Update status
                    job.status = JobStatus.IN_PROGRESS
                    job.started_at = datetime.now()
                    
                    if progress_callback:
                        progress_callback(job)
                    
                    # Process the job (run in executor if sync function)
                    loop = asyncio.get_event_loop()
                    job.result = await loop.run_in_executor(None, processor_func, job.region_json)
                    
                    # Mark as completed
                    job.status = JobStatus.COMPLETED
                    job.completed_at = datetime.now()
                    result.completed += 1
                    
                    logger.info(f"✓ Job completed: {job.job_id}")
                    
                except Exception as e:
                    # Error isolation: Log error but continue with other jobs
                    logger.error(f"✗ Job failed: {job.job_id} - {str(e)}")
                    logger.debug(traceback.format_exc())
                    
                    job.status = JobStatus.FAILED
                    job.error = str(e)
                    job.completed_at = datetime.now()
                    result.failed += 1
        
        # Process all jobs in parallel
        await asyncio.gather(*[process_job(job) for job in jobs])
        
        result.completed_at = datetime.now()
        
        logger.info(f"✓ Batch processing complete: {result.completed}/{result.total_jobs} succeeded")
        return result
    
    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """
        Get status of a specific job.
        
        Args:
            job_id: Job identifier
        
        Returns:
            BatchJob if found, None otherwise
        """
        for job in self.jobs:
            if job.job_id == job_id:
                return job
        return None
    
    def get_all_jobs(self) -> List[BatchJob]:
        """
        Get all jobs.
        
        Returns:
            List of all BatchJob objects
        """
        return self.jobs.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of batch processing.
        
        Returns:
            Summary dictionary
        """
        total = len(self.jobs)
        completed = sum(1 for job in self.jobs if job.status == JobStatus.COMPLETED)
        failed = sum(1 for job in self.jobs if job.status == JobStatus.FAILED)
        in_progress = sum(1 for job in self.jobs if job.status == JobStatus.IN_PROGRESS)
        pending = sum(1 for job in self.jobs if job.status == JobStatus.PENDING)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": pending,
            "success_rate": completed / total if total > 0 else 0.0
        }


# Convenience function
def create_batch_processor(max_concurrent: int = 3) -> BatchProcessor:
    """
    Create and initialize a Batch Processor.
    
    Args:
        max_concurrent: Maximum number of concurrent jobs
    
    Returns:
        Initialized BatchProcessor instance
    """
    return BatchProcessor(max_concurrent=max_concurrent)
