import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from fuzzywuzzy import fuzz
from spacy.matcher import Matcher
import logging
from contact_app.models import Professional  # Import your model

# Initialize models
nlp = spacy.load('en_core_web_md')
model = SentenceTransformer('all-MiniLM-L6-v2')
matcher = Matcher(nlp.vocab)
matcher.add("JOB_TITLE", [[{"POS": "NOUN"}, {"POS": "NOUN", "OP": "*"}]])

# Configure logging
logging.basicConfig(level=logging.WARNING)

US_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", "illinois",
    "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland",
    "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana",
    "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
    "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah",
    "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming"
}

def parse_query(query):
    """
    Parse the user query to extract job titles, locations, maximum hourly rate, and query vector.
    """
    Doc = nlp(query)
    parsed = {
        "job_titles": [],
        "locations": [],
        "max_hourly_rate": None,
        "query_vector": model.encode([query]).reshape(1, -1)
    }

    # Extract job titles using matcher
    matches = matcher(Doc)
    for _, start, end in matches:
        span = Doc[start:end]
        parsed["job_titles"].append(span.text)

    # Extract entities
    for ent in Doc.ents:
        if ent.label_ == "GPE":
            location = ent.text.strip().lower()
            if location not in US_STATES:
                raise ValueError(f"We currently only support US locations. '{ent.text}' is outside the supported region.")
            parsed["locations"].append(location)
        elif ent.label_ == "MONEY":
            amount = ent.text.strip().replace("$", "").replace(",", "").lower()
            try:
                amount = ''.join(filter(lambda x: x.isdigit() or x == '.', amount))
                parsed["max_hourly_rate"] = float(amount)
            except ValueError:
                logging.warning(f"Invalid rate: {ent.text}")
    return parsed

def fetch_profiles():
    """
    Fetch profiles from the database and format them into a list of dictionaries.
    """
    profiles = Professional.objects.values(
        "id", "job_title", "state", "service_cost_per_hour", "expertise"
    )
    formatted_profiles = []

    for profile in profiles:
        try:
            profile["service_cost_per_hour"] = float(profile["service_cost_per_hour"])
        except (ValueError, TypeError):
            logging.warning(f"Invalid hourly rate for profile ID {profile['id']}")
            continue
        formatted_profiles.append(profile)

    return formatted_profiles

def find_recommendations(query, profiles=None, weights=None, threshold=0.5):
    """
    Find and rank profiles based on the user query using weighted scoring and fuzzy matching.
    """
    weights = weights or {
        "job_title": 0.4,
        "location": 0.3,
        "hourly_rate": 0.2,
        "semantic_similarity": 0.1
    }
    try:
        query_features = parse_query(query)
    except ValueError as e:
        return str(e)

    if profiles is None:
        profiles = fetch_profiles()

    recommendations = []

    for profile in profiles:
        score = 0

        # Job Title Matching
        if query_features["job_titles"]:
            profile_job_title = profile.get("job_title", "")
            if profile_job_title:
                for jt in query_features["job_titles"]:
                    ratio = fuzz.token_set_ratio(jt.lower(), profile_job_title.lower())
                    if ratio > 80:
                        score += weights["job_title"]
                        break

        # Location Matching
        if query_features["locations"]:
            profile_location = profile.get("state", "")
            if profile_location.lower() in query_features["locations"]:
                score += weights["location"]

        # Hourly Rate Matching
        if query_features["max_hourly_rate"] is not None:
            try:
                profile_rate = float(profile.get("service_cost_per_hour", 0))
                if profile_rate <= query_features["max_hourly_rate"]:
                    score += weights["hourly_rate"]
            except ValueError:
                logging.warning(f"Invalid hourly rate in profile: {profile.get('service_cost_per_hour')}")
                continue

        # Semantic Similarity
        profile_job_title = profile.get("job_title", "")
        if profile_job_title:
            profile_vector = model.encode([profile_job_title]).reshape(1, -1)
            semantic_similarity = cosine_similarity(
                query_features["query_vector"],
                profile_vector
            )[0][0]
            score += weights["semantic_similarity"] * semantic_similarity

        # Add profile only if score >= threshold
        if score >= threshold:
            recommendations.append((profile, score))

    # Sort recommendations based on score
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [rec[0] for rec in recommendations[:10]]
