# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.exceptions import ValidationError
from frappe.utils import get_url, strip_html_tags
from frappe.utils.html_utils import clean_html

no_cache = 1


def get_context(context):
	message_context = frappe._dict()
	if hasattr(frappe.local, "message"):
		message_context["header"] = frappe.local.message_title
		message_context["title"] = strip_html_tags(frappe.local.message_title)
		message_context["traceback"] = strip_html_tags(frappe.local.message)
		full_message = frappe.local.message
		if isinstance(full_message, ValidationError):
			message_context["message"] = str(full_message)
		else:
			exception_start = full_message.find(": ")
			if exception_start != -1:
				exception_message = full_message[exception_start + 2:]
				error_message = get_error_message(exception_message)
				message_context["message"] = error_message["message"]
				message_context["title"] = error_message["title"]
			else:
				error_message = get_error_message(full_message)
				message_context["message"] = error_message["message"]
				message_context["title"] = error_message["title"]
		message_context["siteURL"] = get_url()

		if hasattr(frappe.local, "message_success"):
			message_context["success"] = frappe.local.message_success

	elif frappe.local.form_dict.id:
		message_id = frappe.local.form_dict.id
		key = f"message_id:{message_id}"
		message = frappe.cache.get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				frappe.local.response["http_status_code"] = message["http_status_code"]

	if not message_context.title:
		message_context.title = clean_html(frappe.form_dict.title)

	if not message_context.message:
		message_context.message = clean_html(frappe.form_dict.message)

	return message_context

error_message_template = {
	"subscription": {
		"title": "Subscription expired",
		"message": "Your subscription has expired. Please reach out to marketing@assureai.in for renewal."
	},
	"signup": {
		"title": "Invalid credentials",
		"message": "Invalid user ID"
	},
	"disabled": {
		"title": "Invalid credentials",
		"message": "Your user ID is not active. Please reach out to the AssureAI Support team."
	},
	"denied": {
		"title": "Access Denied",
		"message": "You do not have permission to access this page."
	},
	"unexpected_error": {
		"title": "Error",
		"message": "An unexpected error occurred, please reach out to the AssureAI Support team"
	}
}

def get_error_message(message):
	if message == "":
		return error_message_template["signup"]
	for key, value in error_message_template.items():
		if message.lower().find(key) != -1:
			return value
	return error_message_template["unexpected_error"]