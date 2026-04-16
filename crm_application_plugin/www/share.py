import time
import frappe
from frappe.utils import get_url


def get_context(context: dict) -> dict:
    """Prepare context for the PDF share wrapper page."""
    doc_name = frappe.form_dict.get("doc_name")
    image_url = frappe.form_dict.get("image_url")

    if not doc_name:
        frappe.local.flags.redirect_location = "/"
        raise frappe.Redirect

    # ── Fix #1: Prevent this page from being cached ──────────────────────────
    # Without this, the browser caches the meta-refresh redirect and never
    # re-runs get_context, serving the old PDF URL to every subsequent visitor.
    frappe.local.response["headers"] = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    base_url = get_url()

    try:
        # ── Fix #2: Use db.get_value to bypass Frappe's document-level cache ─
        # frappe.get_doc() can return a stale cached object within the same
        # request lifecycle. db.get_value() always hits the DB directly.
        file_data = frappe.db.get_value(
            "File",
            doc_name,
            ["file_name", "file_url", "modified"],
            as_dict=True,
        )

        if not file_data:
            raise frappe.DoesNotExistError

        # ── Fix #3: Cache-bust the PDF URL using the file's modified timestamp ─
        # If the file was replaced on disk at the same path, the browser would
        # serve its cached copy. Appending ?v=<timestamp> forces a fresh fetch
        # whenever the File doc's modified date changes.
        try:
            bust = int(file_data.modified.timestamp())
        except (AttributeError, OSError):
            bust = int(time.time())

        context.title = file_data.file_name or "Shared Document"
        context.description = "View this document securely."
        context.pdf_url = f"{base_url}{file_data.file_url}?v={bust}"
        context.image = image_url or f"{base_url}/assets/frappe/images/default-avatar.png"

    except frappe.DoesNotExistError:
        context.title = "Document Not Found"
        context.description = "The requested file no longer exists."
        context.pdf_url = base_url
        context.image = image_url or f"{base_url}/assets/frappe/images/default-avatar.png"

    return context