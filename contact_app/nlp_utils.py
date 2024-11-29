import spacy
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load('en_core_web_md')

def parse_query(query):
    Doc = nlp(query)
    parsed = {
        "job_title": None,
        "location": None,
        "max_hourly_rate": None,
        "query_vector": Doc.vector
    }

    for ent in Doc.ents:
        if ent.label_ == "GPE":
            parsed["location"] = ent.text
        elif ent.label_ == "MONEY":
            try:
                parsed["max_hourly_rate"] = float(ent.text.strip("$"))
            except ValueError:
                parsed["max_hourly_rate"] = None

    for token in Doc:
        if token.pos_ == "NOUN" and token.dep_ == "attr":
            parsed["job_title"] = token.text
    
    return parsed

def find_recommendations(query, profiles):
    query_features = parse_query(query)
    recommendations = []

    for profile in profiles:
        match = True
        if query_features["job_title"] and query_features["job_title"] != profile["job_title"]:
            match = False
        if query_features["location"] and query_features["location"].lower() != profile["state"].lower():
            match = False
        if query_features["max_hourly_rate"] and profile["hourly_rate"] > query_features["max_hourly_rate"]:
            match = False

        profile_Doc = nlp(profile["job_title"])
        profile_vector = profile_Doc.vector
        semantic_similarity = cosine_similarity([query_features["query_vector"], profile_vector.reshape(1, -1)])[0][0]
        hybrid_score = (1.0 if match else 0.5) + semantic_similarity
        
        recommendations.append((profile, hybrid_score))

    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [rec[0] for rec in recommendations[:10]]