"""
Enterprise Plugin Registry
Manages pluggable components for enterprise integrations
"""
from typing import Dict, Any, Callable, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins that can be registered"""
    API_CONNECTOR = "api_connector"
    UI_COMPONENT = "ui_component"
    VIDEO_CHAT = "video_chat"
    ASL_INTERPRETER = "asl_interpreter"
    PAYMENT_PROCESSOR = "payment_processor"
    AUTHENTICATION = "authentication"
    DATA_CONNECTOR = "data_connector"


class PluginInterface:
    """Base interface for all plugins"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.name = config.get('name', self.__class__.__name__)
    
    def initialize(self) -> bool:
        """Initialize the plugin"""
        raise NotImplementedError("Plugins must implement initialize()")
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the plugin's main functionality"""
        raise NotImplementedError("Plugins must implement execute()")
    
    def validate_config(self) -> bool:
        """Validate plugin configuration"""
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'type': getattr(self, 'plugin_type', 'unknown')
        }


class EnterprisePluginRegistry:
    """
    Central registry for all enterprise plugins
    Allows large companies to plug in their own implementations
    """
    
    def __init__(self):
        self._plugins: Dict[str, Dict[str, PluginInterface]] = {}
        self._factories: Dict[str, Callable] = {}
        
        # Initialize empty registries for each plugin type
        for plugin_type in PluginType:
            self._plugins[plugin_type.value] = {}
    
    def register_plugin(
        self, 
        plugin_type: PluginType, 
        name: str, 
        plugin_class: type,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a new plugin
        
        Args:
            plugin_type: Type of plugin
            name: Unique name for the plugin
            plugin_class: Class implementing PluginInterface
            config: Optional configuration dictionary
        
        Returns:
            True if registration successful
        """
        try:
            if config is None:
                config = {}
            
            config['name'] = name
            plugin_instance = plugin_class(config)
            
            if not isinstance(plugin_instance, PluginInterface):
                logger.error(f"Plugin {name} does not implement PluginInterface")
                return False
            
            if not plugin_instance.validate_config():
                logger.error(f"Plugin {name} configuration validation failed")
                return False
            
            self._plugins[plugin_type.value][name] = plugin_instance
            logger.info(f"Registered plugin: {name} of type {plugin_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin {name}: {str(e)}")
            return False
    
    def get_plugin(self, plugin_type: PluginType, name: str) -> Optional[PluginInterface]:
        """Get a specific plugin by type and name"""
        return self._plugins.get(plugin_type.value, {}).get(name)
    
    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[Dict[str, Any]]:
        """List all registered plugins, optionally filtered by type"""
        if plugin_type:
            plugins = self._plugins.get(plugin_type.value, {})
            return [p.get_metadata() for p in plugins.values()]
        
        all_plugins = []
        for plugin_dict in self._plugins.values():
            all_plugins.extend([p.get_metadata() for p in plugin_dict.values()])
        return all_plugins
    
    def execute_plugin(
        self, 
        plugin_type: PluginType, 
        name: str, 
        *args, 
        **kwargs
    ) -> Optional[Any]:
        """Execute a specific plugin"""
        plugin = self.get_plugin(plugin_type, name)
        if plugin and plugin.enabled:
            try:
                return plugin.execute(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing plugin {name}: {str(e)}")
                return None
        return None
    
    def unregister_plugin(self, plugin_type: PluginType, name: str) -> bool:
        """Unregister a plugin"""
        if name in self._plugins.get(plugin_type.value, {}):
            del self._plugins[plugin_type.value][name]
            logger.info(f"Unregistered plugin: {name}")
            return True
        return False


# Global registry instance
enterprise_registry = EnterprisePluginRegistry()
