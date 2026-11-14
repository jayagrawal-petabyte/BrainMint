import sys
import os

# Ensure backend root is on Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.service import Service
from app.models.content import SiteSetting, FAQ, SocialLink

def seed():
    db = SessionLocal()
    print("🌱 Seeding initial BrainMint content...")

    # 1. 4 Primary Services
    services_data = [
        {
            "name": "Website Development",
            "slug": "website-development",
            "short_description": "Modern, high-performance, and responsive web platforms tailored to your business needs.",
            "description": "BrainMint delivers end-to-end website engineering, ranging from dynamic corporate portals to scalable web applications built with cutting-edge frontends and reliable backends.",
            "features": ["Responsive Web Design", "SEO-ready Architecture", "Modern CMS Integration", "Optimized Web Vitals"],
            "benefits": ["Enhanced brand presence", "Faster page loading", "Higher customer conversions"],
            "display_order": 1,
            "is_active": True,
            "meta_title": "Website Development Services | BrainMint",
            "meta_description": "Custom enterprise website development and modern web apps by BrainMint."
        },
        {
            "name": "Application Development",
            "slug": "application-development",
            "short_description": "Scalable, secure mobile and desktop applications engineered for high performance.",
            "description": "We build native and cross-platform applications designed for robust multi-tier environments, seamless user experience, and enterprise data security.",
            "features": ["iOS & Android Mobile Apps", "Cross-Platform Engineering", "Real-Time Sync", "Microservices Backends"],
            "benefits": ["Omnichannel access", "Smooth user retention", "Enterprise reliability"],
            "display_order": 2,
            "is_active": True,
            "meta_title": "Application Development Services | BrainMint",
            "meta_description": "Custom mobile and cloud application engineering services by BrainMint."
        },
        {
            "name": "AI Agent Development",
            "slug": "ai-agent-development",
            "short_description": "Autonomous AI workflows, custom agents, and intelligent enterprise automation.",
            "description": "Empower your business workflows with autonomous AI agents capable of contextual reasoning, data synthesis, task execution, and seamless integration with existing business systems.",
            "features": ["Autonomous Task Execution", "Contextual RAG Pipelines", "Tool & API Calling", "Continuous Learning & Safety"],
            "benefits": ["Reduced manual overhead", "24/7 intelligent processing", "Scalable decision support"],
            "display_order": 3,
            "is_active": True,
            "meta_title": "AI Agent Development | BrainMint",
            "meta_description": "Autonomous AI agents and business workflow automation by BrainMint."
        },
        {
            "name": "Offshore Development Team",
            "slug": "offshore-development-team",
            "short_description": "Dedicated elite engineering teams seamlessly integrated with your product cycles.",
            "description": "Scale your technical development bandwidth effortlessly with our vetted offshore engineers, product architects, and QA specialists.",
            "features": ["Dedicated Engineering Squads", "Agile & Transparent Sprints", "Direct Lead Alignment", "Flexible Scaling"],
            "benefits": ["Cost-effective scalability", "Access to deep technical talent", "Accelerated release velocity"],
            "display_order": 4,
            "is_active": True,
            "meta_title": "Offshore Development Team | BrainMint",
            "meta_description": "Hire dedicated offshore engineering teams and technical consultants from BrainMint."
        }
    ]

    for item in services_data:
        existing = db.query(Service).filter(Service.slug == item["slug"]).first()
        if not existing:
            db.add(Service(**item))
            print(f"  + Added service: {item['name']}")

    # 2. Site Content Sections
    site_settings = [
        (
            "about_us",
            {
                "headline": "Guiding You to a World of Technology & Innovation",
                "description": "BrainMint is a software consultancy focused on delivering enterprise-grade engineering, digital acceleration, and intelligent software solutions.",
                "mission": "To dedicate advanced research, business process engineering, and cutting-edge software innovation to working together with clients to transform enterprise operations.",
                "vision": "Transforming business velocity through excellence in technology and software innovation."
            },
            "About Us section content"
        ),
        (
            "why_choose_us",
            {
                "title": "Why Choose Us",
                "subtitle": "More than a company. A team that builds, learns, and grows together.",
                "points": [
                    {"title": "Proven Experience", "description": "High-impact execution across complex enterprise domains."},
                    {"title": "Collaborative Team", "description": "Dedicated talent bringing diverse problem-solving perspectives."},
                    {"title": "Client-Centric Approach", "description": "Solutions engineered directly around your business ROI."},
                    {"title": "Innovation & Growth", "description": "Proactive adoption of the latest architectural standards."}
                ]
            },
            "Why Choose Us section content"
        ),
        (
            "contact_info",
            {
                "email": "brainmint@gmail.com",
                "phone": "+91 1234567890",
                "locations": [
                    "SRM Nagar, Potheri, Kattankulathur - 603203, Chengalpattu District, Tamil Nadu, India"
                ],
                "business_hours": "Monday - Friday, 9:00 AM - 6:00 PM IST"
            },
            "Company Contact Information"
        ),
        (
            "privacy_policy",
            {
                "title": "Privacy Policy",
                "last_updated": "October 2026",
                "content": "BrainMint respects your privacy and is committed to protecting visitor personal information submitted through our enquiry channels."
            },
            "Privacy policy text"
        ),
        (
            "terms_and_conditions",
            {
                "title": "Terms and Conditions",
                "last_updated": "October 2026",
                "content": "These terms govern the use of the BrainMint website and consultancy enquiry submissions."
            },
            "Terms and conditions text"
        )
    ]

    for key, value, desc in site_settings:
        existing = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if not existing:
            db.add(SiteSetting(key=key, value=value, description=desc))
            print(f"  + Added site setting: {key}")

    # 3. Social Links
    social_links = [
        {"platform": "LinkedIn", "url": "https://linkedin.com/company/brainmint", "icon": "linkedin", "display_order": 1},
        {"platform": "Twitter", "url": "https://twitter.com/brainmint", "icon": "twitter", "display_order": 2},
        {"platform": "Facebook", "url": "https://facebook.com/brainmint", "icon": "facebook", "display_order": 3}
    ]

    for link in social_links:
        existing = db.query(SocialLink).filter(SocialLink.platform == link["platform"]).first()
        if not existing:
            db.add(SocialLink(**link))
            print(f"  + Added social link: {link['platform']}")

    db.commit()
    db.close()
    print(" Done seeding BrainMint content!")

if __name__ == "__main__":
    seed()