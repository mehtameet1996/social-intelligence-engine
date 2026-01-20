
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Social Intelligence Engine")

MOCK_SUBREDDITS = [
    {"name": "MachineLearning", "score": 92},
    {"name": "OpenAI", "score": 90},
    {"name": "ArtificialIntelligence", "score": 87},
    {"name": "technology", "score": 80},
    {"name": "datascience", "score": 78},
]

MOCK_ENTITIES = [
    {
        "canonical": "OpenAI",
        "aliases": ["Open AI", "openai", "@openai", "company behind ChatGPT"],
        "confidence": 0.94,
        "mentions": [
            "OpenAI released a new model",
            "The company behind ChatGPT is growing fast"
        ]
    },
    {
        "canonical": "Sam Altman",
        "aliases": ["sam altman"],
        "confidence": 0.91,
        "mentions": [
            "Sam Altman announced a new initiative"
        ]
    }
]

MOCK_RELATIONSHIPS = [
    {
        "subject": "Sam Altman",
        "predicate": "ceo",
        "object": "OpenAI",
        "confidence": 0.93
    }
]

@app.get("/subreddits")
def discover_subreddits():
    return MOCK_SUBREDDITS

@app.get("/entities")
def get_entities():
    return MOCK_ENTITIES

@app.get("/relationships")
def get_relationships():
    return MOCK_RELATIONSHIPS
