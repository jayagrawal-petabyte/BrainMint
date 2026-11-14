from app.services.email_service import render_template

def test_template_rendering():
    context = {
        "name": "Test User", 
        "service": "Web Development", 
        "enquiry_id": 1, 
        "email": "test@example.com", 
        "phone": "9876543210", 
        "message": "Hello world", 
        "source": "contact_form"
    }
    html = render_template("enquiry_notification.html", context)
    assert "Test User" in html
    assert "Web Development" in html