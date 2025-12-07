"""
Error Recovery and State Management for Global Brand Localizer

Handles:
- State saving on unrecoverable errors
- Recovery mechanism to resume from saved state
- Comprehensive error logging with structured format
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages system state for error recovery.
    
    Saves state on errors and provides recovery mechanisms to resume
    processing from the point of failure.
    """
    
    def __init__(self, state_dir: str = "output/state"):
        """
        Initialize State Manager.
        
        Args:
            state_dir: Directory for state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"State Manager initialized (state_dir={self.state_dir})")
    
    def save_state(
        self,
        campaign_id: str,
        master_json: Dict[str, Any],
        processed_regions: list,
        pending_regions: list,
        error_info: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save current processing state for recovery.
        
        Args:
            campaign_id: Campaign identifier
            master_json: Master JSON configuration
            processed_regions: List of successfully processed regions
            pending_regions: List of regions still to process
            error_info: Optional error information
        
        Returns:
            Path to saved state file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        state_file = self.state_dir / f"state_{campaign_id}_{timestamp}.json"
        
        state_data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "campaign_id": campaign_id,
            "master_json": master_json,
            "progress": {
                "total_regions": len(processed_regions) + len(pending_regions),
                "processed": len(processed_regions),
                "pending": len(pending_regions),
                "processed_regions": processed_regions,
                "pending_regions": pending_regions
            },
            "error_info": error_info or {},
            "recovery_instructions": {
                "message": "Use StateManager.load_state() to resume processing",
                "next_action": "Process pending_regions list"
            }
        }
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.info(f"✓ State saved to {state_file.name}")
            logger.info(f"  Processed: {len(processed_regions)}, Pending: {len(pending_regions)}")
            
            return state_file
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise
    
    def load_state(self, state_file: Path) -> Dict[str, Any]:
        """
        Load saved state for recovery.
        
        Args:
            state_file: Path to state file
        
        Returns:
            Dictionary with saved state data
        """
        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            logger.info(f"✓ State loaded from {state_file.name}")
            logger.info(f"  Campaign: {state_data.get('campaign_id')}")
            logger.info(f"  Saved at: {state_data.get('saved_at')}")
            
            progress = state_data.get('progress', {})
            logger.info(f"  Progress: {progress.get('processed')}/{progress.get('total_regions')} regions")
            
            return state_data
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            raise
    
    def list_saved_states(self, campaign_id: Optional[str] = None) -> list:
        """
        List all saved state files.
        
        Args:
            campaign_id: Optional campaign ID to filter by
        
        Returns:
            List of state file paths
        """
        if campaign_id:
            pattern = f"state_{campaign_id}_*.json"
        else:
            pattern = "state_*.json"
        
        state_files = sorted(self.state_dir.glob(pattern), reverse=True)
        
        logger.info(f"Found {len(state_files)} saved state(s)")
        
        return state_files
    
    def get_latest_state(self, campaign_id: str) -> Optional[Path]:
        """
        Get the most recent state file for a campaign.
        
        Args:
            campaign_id: Campaign identifier
        
        Returns:
            Path to latest state file, or None if not found
        """
        states = self.list_saved_states(campaign_id)
        
        if states:
            logger.info(f"Latest state: {states[0].name}")
            return states[0]
        else:
            logger.info(f"No saved state found for campaign: {campaign_id}")
            return None
    
    def delete_state(self, state_file: Path) -> bool:
        """
        Delete a state file after successful recovery.
        
        Args:
            state_file: Path to state file
        
        Returns:
            True if deleted successfully
        """
        try:
            state_file.unlink()
            logger.info(f"✓ Deleted state file: {state_file.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete state file: {e}")
            return False


class ErrorLogger:
    """
    Structured error logging for debugging and monitoring.
    """
    
    def __init__(self, log_dir: str = "output/logs"):
        """
        Initialize Error Logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create daily log file
        date_str = datetime.now().strftime("%Y%m%d")
        self.log_file = self.log_dir / f"errors_{date_str}.jsonl"
        
        logger.info(f"Error Logger initialized (log_file={self.log_file.name})")
    
    def log_error(
        self,
        error_type: str,
        component: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "ERROR",
        recovery_action: Optional[str] = None
    ) -> None:
        """
        Log a structured error entry.
        
        Args:
            error_type: Type of error (e.g., "VLM_BRIDGE_ERROR", "FILE_IO_ERROR")
            component: Component where error occurred
            message: Error message
            context: Additional context information
            severity: Error severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            recovery_action: Action taken to recover from error
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "severity": severity,
            "component": component,
            "message": message,
            "context": context or {},
            "recovery_action": recovery_action
        }
        
        try:
            # Append to JSONL file (one JSON object per line)
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(error_entry) + '\n')
            
            # Also log to standard logger
            log_func = getattr(logger, severity.lower(), logger.error)
            log_func(f"[{component}] {error_type}: {message}")
            
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")
    
    def get_recent_errors(self, count: int = 10) -> list:
        """
        Get recent error entries.
        
        Args:
            count: Number of recent errors to retrieve
        
        Returns:
            List of error entries
        """
        errors = []
        
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    
                # Get last N lines
                recent_lines = lines[-count:] if len(lines) > count else lines
                
                for line in recent_lines:
                    try:
                        errors.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            logger.error(f"Failed to read error log: {e}")
        
        return errors


# Convenience functions
def create_state_manager(state_dir: str = "output/state") -> StateManager:
    """
    Create and initialize a State Manager.
    
    Args:
        state_dir: Directory for state files
    
    Returns:
        Initialized StateManager instance
    """
    return StateManager(state_dir=state_dir)


def create_error_logger(log_dir: str = "output/logs") -> ErrorLogger:
    """
    Create and initialize an Error Logger.
    
    Args:
        log_dir: Directory for log files
    
    Returns:
        Initialized ErrorLogger instance
    """
    return ErrorLogger(log_dir=log_dir)
