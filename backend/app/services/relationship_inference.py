import re
from enum import Enum
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import Entity, Relationship


class RelationshipType(str, Enum):
    founder = "founder"
    ceo = "ceo"
    employee = "employee"
    investor = "investor"
    competitor = "competitor"
    parentCompany = "parentCompany"
    subsidiary = "subsidiary"
    partner = "partner"
    acquiredBy = "acquiredBy"
    boardMember = "boardMember"
    advisor = "advisor"
    alumniOf = "alumniOf"
    affiliation = "affiliation"
    opponent = "opponent"


class RelationshipInferenceService:
    """
    Pattern-based relationship extraction (no LLM needed).
    Stores relationships in DB as a graph table.
    """

    def __init__(self, db: Session):
        self.db = db

        # More strict patterns (reduces garbage)
        self.relationship_patterns = {
            RelationshipType.ceo: [
                r"\b(.{2,60}?)\s+(?:is|was)\s+(?:the\s+)?CEO\s+(?:of\s+)?(.{2,80}?)\b",
                r"\bCEO\s+of\s+(.{2,80}?)\s*[:,\-]?\s*(.{2,60}?)\b",
            ],
            RelationshipType.founder: [
                r"\b(.{2,60}?)\s+(?:founded|co-founded|started)\s+(.{2,80}?)\b",
                r"\b(.{2,60}?)\s+(?:is|was)\s+(?:a\s+)?founder\s+of\s+(.{2,80}?)\b",
            ],
            RelationshipType.investor: [
                r"\b(.{2,80}?)\s+(?:invested in|invests in|backed|funded)\s+(.{2,80}?)\b",
            ],
            RelationshipType.partner: [
                r"\b(.{2,80}?)\s+(?:partnered with|partners with|partnered)\s+(.{2,80}?)\b",
                r"\bpartnership\s+between\s+(.{2,80}?)\s+and\s+(.{2,80}?)\b",
            ],
            RelationshipType.acquiredBy: [
                r"\b(.{2,80}?)\s+(?:was\s+)?acquired\s+by\s+(.{2,80}?)\b",
            ],
            RelationshipType.competitor: [
                r"\b(.{2,80}?)\s+(?:competes with|competitor of|rival of)\s+(.{2,80}?)\b",
            ],
            RelationshipType.opponent: [
                r"\b(.{2,80}?)\s+(?:criticized|opposed|sued)\s+(.{2,80}?)\b",
            ],
        }

    def extract_relationships_from_text(self, text: str) -> List[Dict]:
        """
        Extract relationships from text and store them.
        Returns stored relationships (deduped).
        """
        if not text:
            return []

        rels: List[Dict] = []
        for sentence in re.split(r"[.!?\n]+", text):
            sentence = sentence.strip()
            if not sentence:
                continue
            rels.extend(self._extract_from_sentence(sentence))

        stored = []
        for r in rels:
            rel = self._store_relationship(r)
            if rel:
                stored.append(
                    {
                        "id": rel.id,
                        "subject": r["subject"],
                        "relationship": r["relationship"],
                        "object": r["object"],
                        "confidence": rel.confidence_score,
                        "source_text": rel.source_text,
                    }
                )
        return stored

    def _extract_from_sentence(self, sentence: str) -> List[Dict]:
        out = []

        # Prevent extremely long garbage sentences
        if len(sentence) > 400:
            sentence = sentence[:400]

        for rtype, patterns in self.relationship_patterns.items():
            for pat in patterns:
                for m in re.finditer(pat, sentence, flags=re.I):
                    subj = self._clean(m.group(1))
                    obj = self._clean(m.group(2))

                    if not subj or not obj:
                        continue
                    if subj.lower() == obj.lower():
                        continue

                    # Avoid capturing full sentences as entity names
                    if len(subj) > 60 or len(obj) > 80:
                        continue

                    out.append(
                        {
                            "subject": subj,
                            "object": obj,
                            "relationship": rtype.value,
                            "confidence": 0.75,
                            "source_sentence": sentence,
                        }
                    )

        return out

    def _clean(self, name: str) -> str:
        name = re.sub(r"^(the|a|an)\s+", "", name, flags=re.I)
        name = re.sub(r"[@#]", "", name)
        name = re.sub(r"\s+", " ", name).strip()

        # Remove trailing punctuation
        name = re.sub(r"[,:;]+$", "", name).strip()

        return name

    def _guess_entity_type(self, name: str) -> str:
        """
        Very simple heuristic to label entity type.
        """
        n = name.lower()

        # company-ish keywords
        if any(k in n for k in ["inc", "corp", "ltd", "llc", "company", "technologies"]):
            return "company"

        # if looks like a person name (2 words, both capitalized-ish)
        if len(name.split()) in [2, 3]:
            return "person"

        return "unknown"

    def _find_or_create_entity(self, name: str) -> Entity:
        ent = self.db.query(Entity).filter(Entity.canonical_name.ilike(name)).first()
        if ent:
            return ent

        ent = Entity(
            canonical_name=name,
            entity_type=self._guess_entity_type(name),
            confidence_score=0.6,
        )
        self.db.add(ent)
        self.db.flush()
        return ent

    def _store_relationship(self, r: Dict) -> Optional[Relationship]:
        s = self._find_or_create_entity(r["subject"])
        o = self._find_or_create_entity(r["object"])

        existing = (
            self.db.query(Relationship)
            .filter(
                Relationship.subject_entity_id == s.id,
                Relationship.object_entity_id == o.id,
                Relationship.relationship_type == r["relationship"],
            )
            .first()
        )

        if existing:
            existing.confidence_score = max(existing.confidence_score, r["confidence"])
            existing.source_text = existing.source_text or r.get("source_sentence", "")
            self.db.commit()
            return existing

        rel = Relationship(
            subject_entity_id=s.id,
            object_entity_id=o.id,
            relationship_type=r["relationship"],
            confidence_score=r["confidence"],
            source_text=r.get("source_sentence", ""),
        )
        self.db.add(rel)
        self.db.commit()
        return rel

    def get_relationships(self, skip: int = 0, limit: int = 100):
        return self.db.query(Relationship).offset(skip).limit(limit).all()

    def get_entity_relationships(self, entity_id: int):
        return (
            self.db.query(Relationship)
            .filter(
                (Relationship.subject_entity_id == entity_id)
                | (Relationship.object_entity_id == entity_id)
            )
            .all()
        )
