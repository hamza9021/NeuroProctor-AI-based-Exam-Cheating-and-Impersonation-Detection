"""
PipelineManager - Stage registration and execution management.

This module provides the PipelineManager class which is responsible for
registering, managing, and executing pipeline stages. It follows the
Open/Closed Principle - new stages can be added without modifying the
manager code.

The manager is agnostic to specific AI implementations - it only knows
about the PipelineStage interface, enabling loose coupling and easy testing.
"""

import logging
from typing import Dict, List, Optional

from app.services.ai.pipeline.base_pipeline import PipelineStage
from app.services.ai.pipeline.frame_context import FrameContext

logger = logging.getLogger(__name__)


class PipelineManager:
    """
    Manager for registering and executing pipeline stages.

    This class handles stage registration, removal, enabling/disabling,
    and execution order management. It maintains a registry of all
    available stages and their execution status.

    The manager follows the Single Responsibility Principle - it only
    manages stage lifecycle and execution, not the actual processing logic.

    Example:
        manager = PipelineManager()
        manager.register_stage(detector)
        manager.register_stage(tracker)
        manager.register_stage(analyzer)
        
        manager.disable_stage("tracker")
        
        context = FrameContext(frame=frame, frame_number=0)
        processed = manager.execute_stages(context)
    """

    def __init__(self):
        """Initialize the pipeline manager with empty stage registry."""
        self._stages: Dict[str, PipelineStage] = {}
        self._execution_order: List[str] = []
        self._disabled_stages: set[str] = set()
        logger.info("PipelineManager initialized")

    def register_stage(self, stage: PipelineStage) -> None:
        """
        Register a pipeline stage with the manager.

        If a stage with the same name already exists, it will be replaced.

        Args:
            stage: The PipelineStage instance to register.
        """
        stage_name = stage.name
        if stage_name in self._stages:
            logger.warning(
                "Stage '%s' already registered, replacing with new instance",
                stage_name,
            )
            self._execution_order = [
                name for name in self._execution_order if name != stage_name
            ]
        else:
            logger.info("Registered stage '%s'", stage_name)

        self._stages[stage_name] = stage
        self._execution_order.append(stage_name)

    def unregister_stage(self, stage_name: str) -> bool:
        """
        Unregister a pipeline stage by name.

        Args:
            stage_name: Name of the stage to unregister.

        Returns:
            True if stage was unregistered, False if not found.
        """
        if stage_name not in self._stages:
            logger.warning("Stage '%s' not found, cannot unregister", stage_name)
            return False

        del self._stages[stage_name]
        self._execution_order = [
            name for name in self._execution_order if name != stage_name
        ]
        self._disabled_stages.discard(stage_name)
        logger.info("Unregistered stage '%s'", stage_name)
        return True

    def enable_stage(self, stage_name: str) -> bool:
        """
        Enable a previously disabled stage.

        Args:
            stage_name: Name of the stage to enable.

        Returns:
            True if stage was enabled, False if not found or already enabled.
        """
        if stage_name not in self._stages:
            logger.warning("Stage '%s' not found, cannot enable", stage_name)
            return False

        if stage_name not in self._disabled_stages:
            logger.debug("Stage '%s' is already enabled", stage_name)
            return False

        self._disabled_stages.remove(stage_name)
        logger.info("Enabled stage '%s'", stage_name)
        return True

    def disable_stage(self, stage_name: str) -> bool:
        """
        Disable a stage without unregistering it.

        Disabled stages remain registered but are skipped during execution.

        Args:
            stage_name: Name of the stage to disable.

        Returns:
            True if stage was disabled, False if not found or already disabled.
        """
        if stage_name not in self._stages:
            logger.warning("Stage '%s' not found, cannot disable", stage_name)
            return False

        if stage_name in self._disabled_stages:
            logger.debug("Stage '%s' is already disabled", stage_name)
            return False

        self._disabled_stages.add(stage_name)
        logger.info("Disabled stage '%s'", stage_name)
        return True

    def is_stage_enabled(self, stage_name: str) -> bool:
        """
        Check if a stage is currently enabled.

        Args:
            stage_name: Name of the stage to check.

        Returns:
            True if stage exists and is enabled, False otherwise.
        """
        return stage_name in self._stages and stage_name not in self._disabled_stages

    def get_stage(self, stage_name: str) -> Optional[PipelineStage]:
        """
        Get a registered stage by name.

        Args:
            stage_name: Name of the stage to retrieve.

        Returns:
            The PipelineStage instance if found, None otherwise.
        """
        return self._stages.get(stage_name)

    def get_all_stages(self) -> List[PipelineStage]:
        """
        Get all registered stages in execution order.

        Returns:
            List of PipelineStage instances.
        """
        return [self._stages[name] for name in self._execution_order]

    def get_enabled_stages(self) -> List[PipelineStage]:
        """
        Get only enabled stages in execution order.

        Returns:
            List of enabled PipelineStage instances.
        """
        return [
            self._stages[name]
            for name in self._execution_order
            if name not in self._disabled_stages
        ]

    def set_execution_order(self, stage_names: List[str]) -> bool:
        """
        Set the execution order for stages.

        All provided stage names must be registered. Any stages not in the
        list will maintain their relative order after the provided names.

        Args:
            stage_names: List of stage names in desired execution order.

        Returns:
            True if order was set successfully, False if any stage not found.
        """
        for name in stage_names:
            if name not in self._stages:
                logger.error("Cannot set order: stage '%s' not registered", name)
                return False

        # Preserve order of stages not in the provided list
        remaining = [name for name in self._execution_order if name not in stage_names]
        self._execution_order = stage_names + remaining
        logger.info("Execution order updated: %s", self._execution_order)
        return True

    def execute_stages(self, context: FrameContext) -> FrameContext:
        """
        Execute all enabled stages in order on the given context.

        Args:
            context: The FrameContext to process.

        Returns:
            The processed FrameContext with outputs from all enabled stages.
        """
        enabled_stages = self.get_enabled_stages()

        if not enabled_stages:
            logger.warning("No enabled stages, returning context as-is")
            return context

        logger.debug(
            "Executing %d enabled stages for frame %d",
            len(enabled_stages),
            context.frame_number,
        )

        for stage in enabled_stages:
            try:
                logger.debug(
                    "Executing stage '%s' for frame %d",
                    stage.name,
                    context.frame_number,
                )
                context = stage.process(context)
                context.set_stage_output(stage.name, True)
            except Exception as exc:
                context.set_stage_output(stage.name, exc)
                logger.error(
                    "Stage '%s' failed for frame %d: %s",
                    stage.name,
                    context.frame_number,
                    exc,
                )
                raise

        logger.debug("Completed execution of all enabled stages")
        return context

    def clear_all(self) -> None:
        """Unregister all stages and reset the manager."""
        self._stages.clear()
        self._execution_order.clear()
        self._disabled_stages.clear()
        logger.info("PipelineManager cleared all stages")

    def get_status(self) -> Dict[str, any]:
        """
        Get the current status of the pipeline manager.

        Returns:
            Dictionary with manager status information.
        """
        return {
            "total_stages": len(self._stages),
            "enabled_stages": len(self.get_enabled_stages()),
            "disabled_stages": len(self._disabled_stages),
            "execution_order": self._execution_order.copy(),
            "disabled_stage_names": list(self._disabled_stages),
        }
