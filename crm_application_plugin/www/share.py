import time
import frappe
from frappe.utils import get_url


def get_context(context: dict) -> dict:
    """Prepare context for the PDF share wrapper page."""

    # ── Critical: Disable Frappe's Redis page cache for this route ────────
    # Frappe caches rendered portal page HTML in Redis. Without this flag,
    # get_context() is skipped on every request after the first, and the
    # stale PDF URL from the cached HTML is served — even in incognito.
    context.no_cache = 1

    doc_name = frappe.form_dict.get("doc_name")
    image_url = frappe.form_dict.get("image_url")

    if not doc_name:
        frappe.local.flags.redirect_location = "/"
        raise frappe.Redirect

    # ── Also set HTTP headers to prevent browser/CDN caching ─────────────
    frappe.local.response["headers"] = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    base_url = get_url()

    try:
        file_data = frappe.db.get_value(
            "File",
            doc_name,
            ["file_name", "file_url", "modified"],
            as_dict=True,
        )

        if not file_data:
            raise frappe.DoesNotExistError

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