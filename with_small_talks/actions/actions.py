from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from .utils import get_pincode_details
from .constants import PINCODE_DETAILS_CATEGORY_TYPE_AND_JSON_MAP


class ValidatePincodeDetailForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_pincode_detail_form"

    def validate_pincode_detail_category_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pincode_detail_category_type` value."""
        pincode_detail_category_type = slot_value.lower()

        if (
            pincode_detail_category_type
            not in PINCODE_DETAILS_CATEGORY_TYPE_AND_JSON_MAP
        ):
            dispatcher.utter_message(
                f"You entered invalid option. Please select a valid option."
            )
            return {"pincode_detail_category_type": None}
        else:
            return {
                "pincode_detail_category_type": PINCODE_DETAILS_CATEGORY_TYPE_AND_JSON_MAP[
                    pincode_detail_category_type
                ]
            }

    @staticmethod
    def is_validate_pincode(pincode):
        if pincode.isnumeric() and len(pincode) != 6:
            return False

        pincodeJson = get_pincode_details(pincode)
        if "PostOffice" not in pincodeJson[0]:
            return False

        postOffices = pincodeJson[0]["PostOffice"]
        if postOffices is None:
            return False

        return True

    def validate_pincode(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pincode` value."""
        pincode = slot_value

        if not self.is_validate_pincode(pincode):
            dispatcher.utter_message(
                f"You entered invalid pincode. Please select a valid pincode having 6 digits."
            )
            return {"pincode": None}
        else:
            return {"pincode": pincode}


class ActionShowPincodeDetailResult(Action):
    def name(self) -> Text:
        return "action_show_pincode_detail_form_result"

    @staticmethod
    def get_pincode_detail_form_result(pincode_detail_category_type, pincode):
        pincodeJson = get_pincode_details(pincode)
        unique_pincode_detail_form_results = []
        for postOffice in pincodeJson[0]["PostOffice"]:
            pincode_detail_form_result = postOffice[pincode_detail_category_type]
            if pincode_detail_form_result not in unique_pincode_detail_form_results:
                unique_pincode_detail_form_results.append(
                    postOffice[pincode_detail_category_type].replace(" City", "")
                )

        if pincode_detail_category_type == "Division":
            pincode_detail_category_type = "city"

        if len(unique_pincode_detail_form_results) > 1:
            return (
                f"Your pincode have multiple {pincode_detail_category_type.lower()} names which are "
                + f'{", ".join(unique_pincode_detail_form_results[0:-1])} and {unique_pincode_detail_form_results[-1]}'
            )

        return f'Your {pincode_detail_category_type.lower()} is {"".join(unique_pincode_detail_form_results)}'

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        pincode_detail_category_type = tracker.get_slot("pincode_detail_category_type")
        pincode = tracker.get_slot("pincode")
        dispatcher.utter_message(
            self.get_pincode_detail_form_result(pincode_detail_category_type, pincode)
        )
        return [SlotSet("pincode_detail_category_type", None), SlotSet("pincode", None)]


class ActionExtractEntitiesToSlots(Action):
    def name(self) -> Text:
        return "action_extract_entities_to_slots"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        slots = []
        for entity in tracker.latest_message["entities"]:
            if tracker.get_slot(entity["entity"]) == None:
                slots.append(SlotSet(entity["entity"], entity["value"]))
        return slots
