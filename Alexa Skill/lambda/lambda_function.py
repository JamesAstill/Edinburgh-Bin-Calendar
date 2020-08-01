import logging
import os
import boto3
import ask_sdk_core.utils as ask_utils
from ask_sdk_s3.adapter import S3Adapter
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
# Bring in the main function to perform the lookup and return output
from bin_lookup import main

# Set logging for the function
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#S3 persistence session adapter
bucket_region = os.environ.get('S3_PERSISTENCE_REGION') 
bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET') 
s3_client = boto3.client('s3', region_name = bucket_region)
s3_adapter = S3Adapter(bucket_name, s3_client = s3_client)

# Introduction and parameter gather for the skill
class GatherIntentHandler(AbstractRequestHandler):
    """Handler for Gathering Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # Read persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['state'] = "STARTED"
        handler_input.attributes_manager.persistent_attributes = session_attr
        handler_input.attributes_manager.save_persistent_attributes()
        try:
            speak_output = main(session_attr['address'])
            return (handler_input.response_builder
                .speak(speak_output)
                .response)
        except: 
            speak_output = "Now then! What street do you live at?"
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response)

# Pass parameter in and produce bin calendar
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("streetname")(handler_input)

    def handle(self, handler_input):
        intent_val = ask_utils.get_slot_value(handler_input=handler_input, slot_name="street")
        speak_output = main(intent_val)
        # Save persistent_attributes
        attr = handler_input.attributes_manager.persistent_attributes
        attr['address'] = intent_val
        attr['state'] = 'ENDED'
        handler_input.attributes_manager.session_attributes = attr
        handler_input.attributes_manager.save_persistent_attributes()
        return (handler_input.response_builder
            .speak(speak_output)
            .response)

# End the session 
class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


# SkillBuilder helps organise conversation. sb are executed in order.
sb = CustomSkillBuilder(persistence_adapter = s3_adapter)
# Say hello and gather street name
sb.add_request_handler(GatherIntentHandler())
# Process the name and get main() to write the output line
sb.add_request_handler(LaunchRequestHandler())
# Handle session end
sb.add_request_handler(SessionEndedRequestHandler())
lambda_handler = sb.lambda_handler()