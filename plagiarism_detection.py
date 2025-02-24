import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# API Keys (Replace with your actual SerpAPI Key)
SERP_API_KEY = "e8661da46a78c8c6d2ceea08d194bbcd7a5fb7c69da85a785ae6dc61229e0e71"  # Your SerpAPI Key
SCRAPER_API_KEY = "dceaa5bd68d799af8dd1be6b1e714fc7"  # Your ScraperAPI Key

SERP_API_URL = "https://serpapi.com/search"
SCRAPER_API_URL = "https://api.scraperapi.com"

def search_google_serpapi(query):
    """Fetches search results using SerpAPI (Google Search Scraper)."""
    params = {
        "api_key": SERP_API_KEY,
        "q": query[:100],  # Use only first 100 characters for better search
        "num": 5  # Fetch top 5 results
    }
    
    response = requests.get(SERP_API_URL, params=params)
    
    if response.status_code == 200:
        results = response.json().get("organic_results", [])
        return [item["link"] for item in results]
    else:
        print("Error fetching search results:", response.json())
        return []

def extract_text_from_url(url):
    """Uses ScraperAPI to extract webpage content."""
    try:
        proxy_url = f"{SCRAPER_API_URL}?api_key={SCRAPER_API_KEY}&url={url}"
        response = requests.get(proxy_url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        text = " ".join([p.get_text() for p in soup.find_all("p")])  # Extract text from <p> tags
        return text.strip() if text else "No text extracted"
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def extract_website_name(url):
    """Extracts the domain name from a URL (e.g., 'example.com')."""
    parsed_url = urlparse(url)
    return parsed_url.netloc.replace("www.", "")

def check_plagiarism(input_text, scraped_texts):
    """Calculates cosine similarity between input text and scraped web content."""
    if not scraped_texts or all(not text for text in scraped_texts):
        return []
    
    vectorizer = TfidfVectorizer().fit_transform([input_text] + scraped_texts)
    similarity_matrix = cosine_similarity(vectorizer)[0][1:]  # Compare input_text with each scraped text
    return similarity_matrix.tolist()  # Convert numpy array to list

def detect_plagiarism(input_text):
    """Detects plagiarism by searching online, scraping content, and comparing similarity."""
    print("🔎 Searching for similar content online...")
    urls = search_google_serpapi(input_text)
    
    if not urls:
        return {"plagiarism_percentage": 0.0, "results": []}
    
    print(f"📂 Fetching data from {len(urls)} sources...")
    scraped_texts = [extract_text_from_url(url) for url in urls]
    
    print("⚖️ Checking plagiarism...")
    similarity_scores = check_plagiarism(input_text, scraped_texts)
    
    if not similarity_scores:
        return {"plagiarism_percentage": 0.0, "results": []}
    
    # Sort results based on highest similarity
    results = [{"site": extract_website_name(url), "url": url, "similarity": similarity_scores[i]} for i, url in enumerate(urls)]
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)  # Sort by similarity
    
    # Calculate plagiarism percentage based on top result
    plagiarism_percentage = round(similarity_scores[0] * 100, 2) if similarity_scores else 0.0
    
    return {"plagiarism_percentage": plagiarism_percentage, "results": results}

# Example usage
if __name__ == "__main__":
    input_text = input("Enter text to check plagiarism: ")
    result = detect_plagiarism(input_text)
    
    print("\n📝 Plagiarism Report")
    print(f"Plagiarism Detected: {result['plagiarism_percentage']}%")
    
    if result["plagiarism_percentage"] > 0:
        print("\n🔗 Potential Sources:")
        for res in result["results"]:
            print(f"- {res['site']} (Similarity: {res['similarity']*100:.2f}%)")
            print(f"  URL: {res['url']}\n")
    else:
        print("✅ No plagiarism detected.")
