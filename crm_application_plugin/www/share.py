import frappe

def get_context(context: dict) -> dict:
    """Prepare context for the PDF share wrapper page."""
    doc_name = frappe.form_dict.get("doc_name")
    image_url = frappe.form_dict.get("image_url")
    
    if not doc_name:
        frappe.local.flags.redirect_location = "/"
        raise frappe.Redirect
        
    base_url = frappe.utils.get_url()
        
    try:
        # Fetch the file record from Frappe to get the actual PDF path
        file_doc = frappe.get_doc("File", doc_name)
        
        context.title = file_doc.file_name or "Shared Document"
        context.description = "View this document securely."
        context.pdf_url = f"{base_url}{file_doc.file_url}"
        
        # Use the image URL provided by Flutter, with a fallback just in case
        context.image = image_url or f"{base_url}/assets/frappe/images/default-avatar.png"
        
    except frappe.DoesNotExistError:
        context.title = "Document Not Found"
        context.description = "The requested file no longer exists."
        context.pdf_url = base_url
        context.image = image_url or f"{base_url}/assets/frappe/images/default-avatar.png"
        
    return context