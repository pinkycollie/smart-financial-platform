"""
Enterprise Integration Routes
Handles enterprise plugin configuration and inquiries
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from services.enterprise.plugin_registry import enterprise_registry, PluginType
from services.enterprise.api_plugins import (
    BloombergAPIPlugin,
    TurboTaxAPIPlugin, 
    BankAPIPlugin,
    CustomEnterpriseAPIPlugin
)
from services.enterprise.video_plugins import (
    TwilioVideoPlugin,
    ZoomVideoPlugin,
    VSLLabsInterpreterPlugin,
    SignASLInterpreterPlugin,
    PinkSyncInterpreterPlugin
)
import logging
import os

logger = logging.getLogger(__name__)

enterprise_bp = Blueprint('enterprise', __name__, url_prefix='/enterprise')

# Contact email addresses for enterprise inquiries
ENTERPRISE_CONTACT_EMAILS = [
    'architect@360magicians.com',
    'architect@mbtq.dev'
]


@enterprise_bp.route('/')
def index():
    """Enterprise integration portal"""
    return render_template(
        'enterprise/index.html',
        title='Enterprise Integration Portal'
    )


@enterprise_bp.route('/plugins')
def list_plugins():
    """List all available and registered plugins"""
    registered_plugins = enterprise_registry.list_plugins()
    
    available_plugins = {
        'API Connectors': [
            {
                'name': 'Bloomberg API',
                'description': 'Connect to Bloomberg financial data and terminology',
                'class': 'BloombergAPIPlugin',
                'icon': 'fab fa-bloomberg'
            },
            {
                'name': 'TurboTax/Intuit API',
                'description': 'Integrate with TurboTax for tax preparation',
                'class': 'TurboTaxAPIPlugin',
                'icon': 'fas fa-file-invoice-dollar'
            },
            {
                'name': 'Bank API',
                'description': 'Connect to your bank\'s API for account data',
                'class': 'BankAPIPlugin',
                'icon': 'fas fa-university'
            },
            {
                'name': 'Custom Enterprise API',
                'description': 'Flexible plugin for any RESTful API',
                'class': 'CustomEnterpriseAPIPlugin',
                'icon': 'fas fa-plug'
            }
        ],
        'Video Chat': [
            {
                'name': 'Twilio Video',
                'description': 'Twilio video conferencing',
                'class': 'TwilioVideoPlugin',
                'icon': 'fas fa-video'
            },
            {
                'name': 'Zoom',
                'description': 'Zoom video meetings',
                'class': 'ZoomVideoPlugin',
                'icon': 'fas fa-video'
            }
        ],
        'ASL Interpreters': [
            {
                'name': 'VSL Labs',
                'description': 'AI-powered ASL interpretation and translation',
                'class': 'VSLLabsInterpreterPlugin',
                'icon': 'fas fa-hands'
            },
            {
                'name': 'SignASL',
                'description': 'Live ASL interpreter service',
                'class': 'SignASLInterpreterPlugin',
                'icon': 'fas fa-sign-language'
            },
            {
                'name': 'PinkSync',
                'description': 'Full accessibility suite with gloss ASL conversion',
                'class': 'PinkSyncInterpreterPlugin',
                'icon': 'fas fa-universal-access'
            }
        ]
    }
    
    return render_template(
        'enterprise/plugins.html',
        title='Enterprise Plugins',
        registered_plugins=registered_plugins,
        available_plugins=available_plugins
    )


@enterprise_bp.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    """Enterprise inquiry form"""
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name')
        contact_name = request.form.get('contact_name')
        contact_email = request.form.get('contact_email')
        phone = request.form.get('phone')
        company_type = request.form.get('company_type')
        integration_type = request.form.getlist('integration_type')
        message = request.form.get('message')
        
        # Log inquiry
        logger.info(f"Enterprise inquiry from {company_name} ({contact_email})")
        
        # In production, this would send an email
        inquiry_data = {
            'company_name': company_name,
            'contact_name': contact_name,
            'contact_email': contact_email,
            'phone': phone,
            'company_type': company_type,
            'integration_type': integration_type,
            'message': message,
            'contact_emails': ENTERPRISE_CONTACT_EMAILS
        }
        
        flash('Thank you for your inquiry! Our enterprise team will contact you within 24 hours.', 'success')
        return redirect(url_for('enterprise.inquiry_success'))
    
    # GET request - show form
    company_types = [
        'Financial Institution / Bank',
        'Insurance Company',
        'Tax Preparation Service',
        'Investment Firm',
        'Enterprise Software Company',
        'Other'
    ]
    
    integration_types = [
        'API Integration',
        'Video Chat / Conference',
        'ASL Interpreter Services',
        'Data Connector',
        'Custom UI Components',
        'White Label Solution',
        'Full Platform Deployment'
    ]
    
    return render_template(
        'enterprise/inquiry.html',
        title='Enterprise Inquiry',
        company_types=company_types,
        integration_types=integration_types,
        contact_emails=ENTERPRISE_CONTACT_EMAILS
    )


@enterprise_bp.route('/inquiry/success')
def inquiry_success():
    """Inquiry submission success page"""
    return render_template(
        'enterprise/inquiry_success.html',
        title='Inquiry Received'
    )


@enterprise_bp.route('/templates')
def deployment_templates():
    """View deployment templates"""
    templates_list = [
        {
            'name': 'Video Chat Integration',
            'description': 'Ready-to-deploy video chat with ASL support',
            'features': [
                'Multi-provider support (Twilio, Zoom)',
                'ASL interpreter embedding',
                'Screen sharing',
                'Recording capabilities'
            ],
            'icon': 'fas fa-video'
        },
        {
            'name': 'ASL Interpreter Embedding',
            'description': 'Embed ASL interpreters into your application',
            'features': [
                'VSL Labs AI interpretation',
                'SignASL live interpreters',
                'PinkSync full accessibility',
                'Real-time translation'
            ],
            'icon': 'fas fa-hands'
        },
        {
            'name': 'Gloss ASL Conversion',
            'description': 'Convert heavy financial context to accessible gloss ASL',
            'features': [
                'Financial terminology conversion',
                'Context-aware translation',
                'Video generation',
                'Multi-format export'
            ],
            'icon': 'fas fa-language'
        },
        {
            'name': 'API Integration Suite',
            'description': 'Complete API integration framework',
            'features': [
                'Bloomberg data integration',
                'Bank API connectors',
                'TurboTax integration',
                'Custom API support'
            ],
            'icon': 'fas fa-plug'
        }
    ]
    
    return render_template(
        'enterprise/templates.html',
        title='Deployment Templates',
        templates=templates_list
    )


@enterprise_bp.route('/api/plugins', methods=['GET'])
def api_list_plugins():
    """API endpoint to list plugins"""
    plugin_type = request.args.get('type')
    
    if plugin_type:
        try:
            ptype = PluginType[plugin_type.upper()]
            plugins = enterprise_registry.list_plugins(ptype)
        except KeyError:
            return jsonify({'error': 'Invalid plugin type'}), 400
    else:
        plugins = enterprise_registry.list_plugins()
    
    return jsonify({'plugins': plugins})


@enterprise_bp.route('/api/plugin/execute', methods=['POST'])
def api_execute_plugin():
    """API endpoint to execute a plugin"""
    data = request.get_json()
    
    plugin_type_str = data.get('plugin_type')
    plugin_name = data.get('plugin_name')
    kwargs = data.get('parameters', {})
    
    if not plugin_type_str or not plugin_name:
        return jsonify({'error': 'Missing plugin_type or plugin_name'}), 400
    
    try:
        plugin_type = PluginType[plugin_type_str.upper()]
    except KeyError:
        return jsonify({'error': 'Invalid plugin type'}), 400
    
    result = enterprise_registry.execute_plugin(plugin_type, plugin_name, **kwargs)
    
    if result is None:
        return jsonify({'error': 'Plugin execution failed'}), 500
    
    return jsonify({'result': result})


@enterprise_bp.route('/dashboard')
def dashboard():
    """Enterprise configuration dashboard"""
    registered_plugins = enterprise_registry.list_plugins()
    
    # Group by type
    plugins_by_type = {}
    for plugin in registered_plugins:
        ptype = plugin.get('type', 'unknown')
        if ptype not in plugins_by_type:
            plugins_by_type[ptype] = []
        plugins_by_type[ptype].append(plugin)
    
    return render_template(
        'enterprise/dashboard.html',
        title='Enterprise Dashboard',
        plugins_by_type=plugins_by_type,
        total_plugins=len(registered_plugins)
    )


@enterprise_bp.route('/pinksync')
def pinksync_partner():
    """PinkSync partnership and subscription page"""
    subscription_tiers = [
        {
            'name': 'Basic',
            'price': '$99/month',
            'features': [
                'ASL interpreter integration',
                'Basic video captioning',
                'Email support',
                '10 hours/month interpreter time'
            ]
        },
        {
            'name': 'Professional',
            'price': '$299/month',
            'features': [
                'All Basic features',
                'Gloss ASL conversion',
                'Real-time translation',
                'Priority support',
                '50 hours/month interpreter time',
                'Custom integration support'
            ]
        },
        {
            'name': 'Enterprise',
            'price': 'Custom',
            'features': [
                'All Professional features',
                'Unlimited interpreter time',
                'Dedicated account manager',
                'White-label options',
                'SLA guarantees',
                'Custom feature development'
            ]
        }
    ]
    
    return render_template(
        'enterprise/pinksync.html',
        title='PinkSync Partnership',
        subscription_tiers=subscription_tiers
    )
