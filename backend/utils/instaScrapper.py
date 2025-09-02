import instaloader
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

def main():
    """
    Scrapes an Instagram profile for metadata and recent posts.
    Credentials are to be provided in a .env file in the same directory.
    """
    # Load environment variables from .env file
    # This will look for a .env file in the current directory or parent directories
    load_dotenv()

    # --- Get target profile from command line arguments ---
    if len(sys.argv) < 2:
        print("Usage: python instaScrapper.py <instagram_username>")
        sys.exit(1)
    target_profile = sys.argv[1]

    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )

    # --- Login using credentials from .env file ---
    insta_user = os.getenv("INSTAGRAM_USERNAME")
    insta_pass = os.getenv("INSTAGRAM_PASSWORD")

    if insta_user and insta_pass:
        print(f"Attempting to log in as {insta_user}...")
        try:
            L.login(insta_user, insta_pass)
            print("Login successful.")
        except Exception as e:
            print(f"\nERROR: Login failed. Please check your credentials in the .env file.")
            print(f"Instagram's error: {e}")
            sys.exit(1)
    else:
        print("WARNING: INSTA_USER or INSTA_PASS not found in environment variables or .env file.")
        print("Proceeding without login. Scraping may fail or be severely limited.")

    # --- Scrape Profile ---
    print(f"\nFetching profile data for: {target_profile}")
    try:
        profile = instaloader.Profile.from_username(L.context, target_profile)
    except Exception as e:
        print(f"Error: Could not fetch profile for '{target_profile}'.")
        print(f"Details: {e}")
        sys.exit(1)

    profile_data = {
        "username": profile.username,
        "followers": profile.followers,
        "following": profile.followees,
        "posts_count": profile.mediacount,
        "biography": profile.biography,
        "external_url": profile.external_url,
        "is_private": profile.is_private
    }

    # --- Scrape Posts ---
    print(f"Fetching recent posts (up to 50)...")
    posts_data = []
    try:
        for i, post in enumerate(profile.get_posts()):
            if i >= 50:  # Limit to the 50 most recent posts
                break
            post_info = {
                "date_utc": post.date_utc.isoformat(),
                "caption": post.caption,
                "likes": post.likes,
                "comments": post.comments,
                "url": f"https://www.instagram.com/p/{post.shortcode}/"
            }
            posts_data.append(post_info)
            print(".", end="", flush=True)
        print("\nDone fetching posts.")
    except Exception as e:
        print(f"\nError fetching posts: {e}")

    # --- Save Data ---
    # The output file will be saved in the same directory where the script is run.
    output_data = {
        "profile": profile_data,
        "posts": posts_data
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{target_profile}_insta_data_{timestamp}.json"

    print(f"\nSaving data to {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print("\n✅ Scraping complete.")


if __name__ == "__main__":
    main()