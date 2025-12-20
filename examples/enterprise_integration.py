"""
Example: Enterprise Integration Setup
Demonstrates how to set up and use enterprise plugins
"""

# Example 1: Register Bloomberg API Plugin
def setup_bloomberg():
    from services.enterprise.plugin_registry import enterprise_registry, PluginType
    from services.enterprise.api_plugins import BloombergAPIPlugin
    
    # Register the plugin
    success = enterprise_registry.register_plugin(
        PluginType.API_CONNECTOR,
        'bloomberg',
        BloombergAPIPlugin,
        config={
            'api_key': 'YOUR_BLOOMBERG_API_KEY',
            'base_url': 'https://api.bloomberg.com',
            'enabled': True
        }
    )
    
    if success:
        print("✓ Bloomberg API plugin registered successfully")
    else:
        print("✗ Failed to register Bloomberg API plugin")
    
    # Use the plugin
    result = enterprise_registry.execute_plugin(
        PluginType.API_CONNECTOR,
        'bloomberg',
        method='GET',
        endpoint='/market-data/v1/securities',
        params={'symbols': 'AAPL,GOOGL'}
    )
    
    print(f"Result: {result}")


# Example 2: Set up Video Chat with ASL Interpreter
def setup_video_chat():
    from services.enterprise.plugin_registry import enterprise_registry, PluginType
    from services.enterprise.video_plugins import TwilioVideoPlugin, VSLLabsInterpreterPlugin
    
    # Register Twilio video
    enterprise_registry.register_plugin(
        PluginType.VIDEO_CHAT,
        'twilio',
        TwilioVideoPlugin,
        config={
            'account_sid': 'YOUR_TWILIO_SID',
            'api_secret': 'YOUR_TWILIO_SECRET',
            'enabled': True
        }
    )
    
    # Register VSL Labs interpreter
    enterprise_registry.register_plugin(
        PluginType.ASL_INTERPRETER,
        'vsl_labs',
        VSLLabsInterpreterPlugin,
        config={
            'api_key': 'YOUR_VSL_API_KEY',
            'enabled': True
        }
    )
    
    # Create a video room
    room = enterprise_registry.execute_plugin(
        PluginType.VIDEO_CHAT,
        'twilio',
        action='create_room',
        room_config={
            'name': 'Financial Consultation',
            'type': 'group',
            'max_participants': 10
        }
    )
    
    print(f"✓ Video room created: {room}")
    
    # Request ASL interpreter
    interpreter = enterprise_registry.execute_plugin(
        PluginType.ASL_INTERPRETER,
        'vsl_labs',
        action='request_interpreter',
        appointment_details={
            'session_id': room['room_id'],
            'duration': 60
        }
    )
    
    print(f"✓ ASL interpreter assigned: {interpreter}")


# Example 3: PinkSync Full Accessibility Suite
def setup_pinksync():
    from services.enterprise.plugin_registry import enterprise_registry, PluginType
    from services.enterprise.video_plugins import PinkSyncInterpreterPlugin
    
    # Register PinkSync
    enterprise_registry.register_plugin(
        PluginType.ASL_INTERPRETER,
        'pinksync',
        PinkSyncInterpreterPlugin,
        config={
            'api_key': 'YOUR_PINKSYNC_API_KEY',
            'subscription_tier': 'professional',
            'enabled': True
        }
    )
    
    print("✓ PinkSync registered")
    
    # Request full accessibility suite
    session = enterprise_registry.execute_plugin(
        PluginType.ASL_INTERPRETER,
        'pinksync',
        action='request_interpreter',
        appointment_details={
            'session_id': 'consultation_123',
            'scheduled_time': '2025-12-20T14:00:00Z',
            'duration': 60
        }
    )
    
    print(f"✓ PinkSync session: {session}")
    
    # Convert heavy financial text to gloss ASL
    plugin = enterprise_registry.get_plugin(PluginType.ASL_INTERPRETER, 'pinksync')
    gloss = plugin.convert_to_gloss_asl(
        "The compound interest on your investment portfolio will be calculated quarterly "
        "and added to your principal balance, which will then earn additional interest."
    )
    
    print(f"✓ Gloss ASL: {gloss['gloss_asl']}")
    print(f"✓ Video URL: {gloss['video_url']}")


# Example 4: Custom Bank Integration
def setup_bank_integration():
    from services.enterprise.plugin_registry import enterprise_registry, PluginType
    from services.enterprise.api_plugins import BankAPIPlugin
    
    # Register bank API
    enterprise_registry.register_plugin(
        PluginType.API_CONNECTOR,
        'my_bank',
        BankAPIPlugin,
        config={
            'api_key': 'YOUR_BANK_API_KEY',
            'base_url': 'https://api.mybank.com',
            'bank_name': 'My Bank',
            'enabled': True
        }
    )
    
    print("✓ Bank API registered")
    
    # Get customer accounts
    accounts = enterprise_registry.execute_plugin(
        PluginType.API_CONNECTOR,
        'my_bank',
        method='GET',
        endpoint='/accounts/v1/customers/12345/accounts'
    )
    
    print(f"✓ Customer accounts: {accounts}")


# Example 5: List All Registered Plugins
def list_all_plugins():
    from services.enterprise.plugin_registry import enterprise_registry
    
    plugins = enterprise_registry.list_plugins()
    
    print("\n=== Registered Plugins ===")
    for plugin in plugins:
        status = "✓ Enabled" if plugin['enabled'] else "✗ Disabled"
        print(f"{status} - {plugin['name']} ({plugin['type']})")


if __name__ == '__main__':
    print("MBTQ Enterprise Integration Examples")
    print("=" * 50)
    print()
    
    print("Example 1: Bloomberg API Integration")
    print("-" * 50)
    print("# Register Bloomberg plugin")
    print("enterprise_registry.register_plugin(")
    print("    PluginType.API_CONNECTOR,")
    print("    'bloomberg',")
    print("    BloombergAPIPlugin,")
    print("    config={'api_key': 'YOUR_KEY'}")
    print(")")
    print()
    
    print("Example 2: Video Chat with ASL Interpreter")
    print("-" * 50)
    print("# Create video room")
    print("room = enterprise_registry.execute_plugin(")
    print("    PluginType.VIDEO_CHAT,")
    print("    'twilio',")
    print("    action='create_room'")
    print(")")
    print()
    
    print("Example 3: PinkSync Full Accessibility")
    print("-" * 50)
    print("# Request PinkSync services")
    print("session = enterprise_registry.execute_plugin(")
    print("    PluginType.ASL_INTERPRETER,")
    print("    'pinksync',")
    print("    action='request_interpreter'")
    print(")")
    print()
    
    print("Example 4: Bank API Integration")
    print("-" * 50)
    print("# Get customer accounts")
    print("accounts = enterprise_registry.execute_plugin(")
    print("    PluginType.API_CONNECTOR,")
    print("    'my_bank',")
    print("    method='GET',")
    print("    endpoint='/accounts/v1/customers/12345/accounts'")
    print(")")
    print()
    
    print("\nFor full examples, see:")
    print("- docs/ENTERPRISE_INTEGRATION.md")
    print("- /enterprise (web interface)")
    print()
    print("Contact: architect@360magicians.com | architect@mbtq.dev")
