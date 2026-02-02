import requests

APP_ID = "xxxxxxx"
APP_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxx"

def fetch_jobs(primary_skill, limit=10):
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": primary_skill + " python django flask",
        "results_per_page": limit
    }

    response = requests.get(url, params=params)
    data = response.json()

    jobs = []
    for job in data.get("results", []):
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name", "N/A"),
            "location": job.get("location", {}).get("display_name", "N/A"),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "description": job.get("description", ""),
            "url": job.get("redirect_url")
        })
    return jobs
