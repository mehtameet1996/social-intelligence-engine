import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import Entity, EntityMention


class EntityResolutionService:
    def __init__(self, db: Session):
        self.db = db

    async def resolve_entities_in_text(self, text: str) -> List[Dict]:
        # Very simple heuristic resolver (fast + no heavy model downloads)
        raw = self._extract_candidates(text)
        merged = self._merge_similar(raw)

        results = []
        for ent in merged:
            entity = self._store_entity(ent)
            results.append(
                {
                    "id": entity.id,
                    "canonical_name": entity.canonical_name,
                    "entity_type": entity.entity_type,
                    "confidence_score": entity.confidence_score,
                }
            )
        return results

    def _extract_candidates(self, text: str) -> List[Dict]:
        # captures @handles and Proper Nouns (basic)
        candidates = []

        for m in re.finditer(r"@([A-Za-z0-9_]+)", text):
            candidates.append({"name": "@" + m.group(1), "type": "company", "confidence": 0.7, "context": text})

        for m in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text):
            name = m.group(1).strip()
            if len(name) < 3:
                continue
            candidates.append({"name": name, "type": "other", "confidence": 0.6, "context": text})

        return candidates

    def _normalize(self, name: str) -> str:
        name = re.sub(r"^(the|a|an)\s+", "", name, flags=re.I)
        name = re.sub(r"[^\w\s]", "", name)
        name = re.sub(r"\s+", " ", name).strip().lower()
        return name

    def _similarity(self, a: str, b: str) -> float:
        na, nb = self._normalize(a), self._normalize(b)
        if na == nb:
            return 1.0
        s = SequenceMatcher(None, na, nb).ratio()
        if na in nb or nb in na:
            s = min(1.0, s + 0.2)
        return s

    def _merge_similar(self, ents: List[Dict]) -> List[Dict]:
        merged = []
        used = set()
        for i, e in enumerate(ents):
            if i in used:
                continue
            group = [e]
            used.add(i)
            for j in range(i + 1, len(ents)):
                if j in used:
                    continue
                if self._similarity(e["name"], ents[j]["name"]) >= 0.85:
                    group.append(ents[j])
                    used.add(j)

            best = max(group, key=lambda x: x["confidence"])
            avg_conf = sum(x["confidence"] for x in group) / len(group)
            merged.append(
                {
                    "canonical_name": best["name"],
                    "type": best["type"],
                    "confidence": min(avg_conf, 1.0),
                    "mentions": [{"text": x["name"], "context": x["context"], "confidence": x["confidence"]} for x in group],
                }
            )
        return merged

    def _store_entity(self, ent: Dict) -> Entity:
        existing = (
            self.db.query(Entity)
            .filter(Entity.canonical_name == ent["canonical_name"], Entity.entity_type == ent["type"])
            .first()
        )
        if existing:
            entity = existing
            entity.confidence_score = max(entity.confidence_score, ent["confidence"])
        else:
            entity = Entity(
                canonical_name=ent["canonical_name"],
                entity_type=ent["type"],
                confidence_score=ent["confidence"],
            )
            self.db.add(entity)
            self.db.flush()

        for m in ent.get("mentions", []):
            exists = (
                self.db.query(EntityMention)
                .filter(EntityMention.entity_id == entity.id, EntityMention.mention_text == m["text"])
                .first()
            )
            if not exists:
                self.db.add(
                    EntityMention(
                        entity_id=entity.id,
                        mention_text=m["text"],
                        context=m.get("context", ""),
                        confidence_score=m.get("confidence", 0.5),
                    )
                )

        self.db.commit()
        return entity

    def get_entities(self, skip: int = 0, limit: int = 100, entity_type: Optional[str] = None):
        q = self.db.query(Entity)
        if entity_type:
            q = q.filter(Entity.entity_type == entity_type)
        return q.offset(skip).limit(limit).all()

    def get_entity(self, entity_id: int):
        return self.db.query(Entity).filter(Entity.id == entity_id).first()

    def get_entity_mentions(self, entity_id: int):
        return self.db.query(EntityMention).filter(EntityMention.entity_id == entity_id).all()

    def search_entities(self, query: str, limit: int = 20):
        return self.db.query(Entity).filter(Entity.canonical_name.ilike(f"%{query}%")).limit(limit).all()
