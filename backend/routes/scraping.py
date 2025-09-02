from fastapi import APIRouter, HTTPException
from services import scraping_service

router = APIRouter(
    prefix="/scraping",
    tags=["Scraping"],
)

@router.post("/emails", summary="Trigger Email Scraping")
def scrape_emails_endpoint():
    """
    Triggers the email scraper to process .eml files in the `mails` directory.
    Saves the results to a CSV file on the server.
    """
    try:
        output_path = scraping_service.scrape_emails()
        return {"message": "Email scraping completed successfully.", "output_file": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instagram/{username}", summary="Scrape an Instagram Profile")
def scrape_instagram_endpoint(username: str):
    """
    Triggers the Instagram scraper for a specific username.
    Requires `INSTA_USER` and `INSTA_PASS` to be set in a `.env` file.
    Returns the scraped data as JSON.
    """
    try:
        data = scraping_service.scrape_instagram_profile(username)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whatsapp", summary="Trigger WhatsApp Chat Analysis")
def analyze_whatsapp_endpoint():
    """
    Triggers the analysis of all WhatsApp chat logs in the `whatsapp` directory.
    Returns the analysis results as JSON.
    """
    try:
        analysis_results = scraping_service.analyze_whatsapp_chats()
        return analysis_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
