import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from fuzzywuzzy import fuzz
from spacy.matcher import Matcher
import logging

# Initialize models
nlp = spacy.load('en_core_web_md')
model = SentenceTransformer('all-MiniLM-L6-v2')
matcher = Matcher(nlp.vocab)
matcher.add("JOB_TITLE", [[{"POS": "NOUN"}, {"POS": "NOUN", "OP": "*"}]])

# Configure logging
logging.basicConfig(level=logging.WARNING)

# Parse query to extract relevant information and save it in a variable
def parse_query(query):
    Doc = nlp(query)
    parsed = {
        "job_titles": [],
        "locations": [],
        "max_hourly_rate": None,
        "query_vector": model.encode(query)
    }

    # Extract job titles using matcher
    matches = matcher(Doc)
    for _, start, end in matches:
        span = Doc[start:end]
        parsed["job_titles"].append(span.text)

    # Extract entities
    for ent in Doc.ents:
        if ent.label_ == "GPE":
            parsed["locations"].append(ent.text)
        elif ent.label_ == "MONEY":
            # Enhance monetary parsing to handle different formats
            amount = ent.text.strip().replace("$", "").replace(",", "").lower()
            try:
                # Handle formats like '50 dollars', '€50', etc.
                amount = ''.join(filter(lambda x: x.isdigit() or x == '.', amount))
                parsed["max_hourly_rate"] = float(amount)
            except ValueError:
                logging.warning(f"Invalid rate: {ent.text}")
    return parsed

# Recommend with weighted scoring and fuzzy matching
def find_recommendations(query, profiles, weights=None):
    weights = weights or {
        "job_title": 0.4,
        "location": 0.3,
        "hourly_rate": 0.2,
        "semantic_similarity": 0.1
    }
    query_features = parse_query(query)
    recommendations = []
    for profile in profiles:
        score = 0

        # Ensure required keys are present in the profile
        required_keys = ["job_title", "state", "hourly_rate"]
        if not all(key in profile for key in required_keys):
            logging.warning(f"Profile missing required keys: {profile}")
            continue

        # Job Title Matching
        if query_features["job_titles"]:
            profile_job_title = profile["job_title"]
            if any(fuzz.token_set_ratio(jt.lower(), profile_job_title.lower()) > 80 for jt in query_features["job_titles"]):
                score += weights["job_title"]

        # Location Matching
        if query_features["locations"]:
            profile_location = profile["state"]
            if profile_location.lower() in [loc.lower() for loc in query_features["locations"]]:
                score += weights["location"]
            else:
                # Handle hierarchical locations or synonyms (e.g., city vs. state)
                pass  # You can enhance this part using a location library

        # Hourly Rate Matching
        if query_features["max_hourly_rate"]:
            try:
                profile_rate = float(profile["hourly_rate"])
                if profile_rate <= query_features["max_hourly_rate"]:
                    score += weights["hourly_rate"]
            except ValueError:
                logging.warning(f"Invalid hourly rate in profile: {profile['hourly_rate']}")
                continue

        # Semantic Similarity
        # Compute profile vector if not precomputed
        profile_vector = profile.get("query_vector")
        if profile_vector is None:
            profile_job_title = profile["job_title"]
            profile_vector = model.encode(profile_job_title)
            profile["query_vector"] = profile_vector  # Optionally store it for future use

        semantic_similarity = cosine_similarity(
            [query_features["query_vector"]],
            [profile_vector]
        )[0][0]
        score += weights["semantic_similarity"] * semantic_similarity

        recommendations.append((profile, score))

    # Sort recommendations based on score
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [rec[0] for rec in recommendations[:10]]