"""
Bootstrap module for Fargate service
Initializes and registers singleton services in the container
"""

import logging
from include import Container
from app.providers.GHAgent import GHAgent
from app.providers.HGAgent import HGAgent
from app.providers.LLMAgent import LLMAgent

logger = logging.getLogger(__name__)


def bootstrap_agents():
    """
    Bootstrap and register agents as singletons in the container
    This ensures each agent is instantiated only once and reused across jobs
    """
    logger.info("[BOOTSTRAP] Registering agents as singletons...")
    
    # Register GHAgent as singleton
    Container.singleton('GHAgent', lambda: GHAgent())
    logger.info("[BOOTSTRAP] ✓ GHAgent registered")
    
    # Register HGAgent as singleton
    Container.singleton('HGAgent', lambda: HGAgent())
    logger.info("[BOOTSTRAP] ✓ HGAgent registered")
    
    # Register LLMAgent as singleton
    Container.singleton('LLMAgent', lambda: LLMAgent())
    logger.info("[BOOTSTRAP] ✓ LLMAgent registered")
    
    logger.info("[BOOTSTRAP] All agents bootstrapped successfully")


def get_gh_agent() -> GHAgent:
    """Get the singleton GHAgent instance from container"""
    return Container.make('GHAgent')


def get_hg_agent() -> HGAgent:
    """Get the singleton HGAgent instance from container"""
    return Container.make('HGAgent')


def get_llm_agent() -> LLMAgent:
    """Get the singleton LLMAgent instance from container"""
    return Container.make('LLMAgent')
