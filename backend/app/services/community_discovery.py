import math
import requests
from typing import List, Dict
from sqlalchemy.orm import Session

HEADERS = {"User-Agent": "SocialIntelEngine/1.0"}


class CommunityDiscoveryService:
    """
    Community discovery WITHOUT Reddit API credentials.
    Uses public Reddit JSON endpoints.
    """

    async def discover_subreddits(self, company_domain: str) -> List[Dict]:
        company = self._extract_company_name(company_domain)

        # 1) discover subreddits (top 20)
        url = f"https://www.reddit.com/subreddits/search.json?q={company}&limit=20"
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()

        payload = r.json()
        results = payload.get("data", {}).get("children", [])

        subreddits = []
        for item in results:
            s = item.get("data", {})
            name = s.get("display_name", "")
            subscribers = s.get("subscribers") or 0
            desc = s.get("public_description", "") or ""
            title = s.get("title", "") or ""

            # 2) fetch posts for each subreddit (limit small to avoid rate limit)
            recent_posts = self._fetch_recent_posts_public(name, limit=25)

            # 3) mention frequency
            mention_count = self._count_mentions(recent_posts, company)

            # 4) engagement quality (based on real posts)
            engagement_score = self._calc_engagement_from_posts(recent_posts)

            subreddit_data = {
                "name": name,
                "subscribers": subscribers,
                "description": desc,
                "title": title,
                "recent_posts": recent_posts,
                "mention_count": mention_count,
                "engagement_score": engagement_score,
            }

            relevance_score = self._relevance_score(name, title, desc, company)
            subreddit_data["relevance_score"] = relevance_score

            business_value = self._calculate_business_value(subreddit_data, company)
            subreddit_data["business_value_score"] = business_value

            subreddits.append(subreddit_data)

        # sort by business value
        subreddits.sort(key=lambda x: x["business_value_score"], reverse=True)

        # Top 20, and only top 5 show sample posts (demo)
        top20 = subreddits[:20]
        for i, sr in enumerate(top20):
            if i < 5:
                sr["sample_posts"] = sr.get("recent_posts", [])[:10]
            else:
                sr["sample_posts"] = []

            # remove heavy field from response
            sr.pop("recent_posts", None)

        return top20

    def _extract_company_name(self, domain: str) -> str:
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "")
        return domain.split(".")[0].strip().lower()

    def _relevance_score(self, name: str, title: str, desc: str, company: str) -> float:
        name = (name or "").lower()
        title = (title or "").lower()
        desc = (desc or "").lower()
        company = (company or "").lower()

        if company in name:
            return 1.0
        if company in title:
            return 0.8
        if company in desc:
            return 0.6
        return 0.2

    def _normalize_audience_size(self, subscribers: int) -> float:
        if subscribers <= 0:
            return 0.0
        max_size = 10_000_000
        return min(math.log(subscribers + 1) / math.log(max_size + 1), 1.0)

    def _calculate_business_value(self, subreddit_data: Dict, company_name: str) -> float:
        relevance = subreddit_data.get("relevance_score", 0.2)
        audience = self._normalize_audience_size(subreddit_data.get("subscribers") or 0)

        posts = subreddit_data.get("recent_posts", [])
        mention_count = subreddit_data.get("mention_count", 0)
        mention_ratio = mention_count / max(len(posts), 1)  # 0..1

        engagement = subreddit_data.get("engagement_score", 0.0)

        score = (
                relevance * 0.50 +
                audience * 0.15 +
                engagement * 0.15 +
                mention_ratio * 0.20
        )

        if mention_count == 0:
            score *= 0.75

        return min(max(score, 0.0), 1.0)

    def _fetch_recent_posts_public(self, subreddit_name: str, limit: int = 25) -> List[Dict]:
        """
        Uses public Reddit JSON endpoint (no auth):
        https://www.reddit.com/r/{sub}/new.json
        """
        try:
            url = f"https://www.reddit.com/r/{subreddit_name}/new.json?limit={limit}"
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                return []
            payload = r.json()
            children = payload.get("data", {}).get("children", [])
            posts = []
            for c in children:
                d = c.get("data", {})
                posts.append(
                    {
                        "id": d.get("id"),
                        "title": d.get("title") or "",
                        "selftext": (d.get("selftext") or "")[:1500],
                        "score": int(d.get("score") or 0),
                        "num_comments": int(d.get("num_comments") or 0),
                        "permalink": f"https://reddit.com{d.get('permalink')}",
                        "created_utc": float(d.get("created_utc") or 0),
                    }
                )
            return posts
        except Exception:
            return []

    def _count_mentions(self, posts: List[Dict], company_name: str) -> int:
        company_lower = (company_name or "").lower()
        count = 0
        for p in posts:
            text = ((p.get("title", "") or "") + " " + (p.get("selftext", "") or "")).lower()
            if company_lower in text:
                count += 1
        return count

    def _calc_engagement_from_posts(self, posts: List[Dict]) -> float:
        if not posts:
            return 0.0

        avg_score = sum(p.get("score", 0) for p in posts) / len(posts)
        avg_comments = sum(p.get("num_comments", 0) for p in posts) / len(posts)

        # normalize heuristically
        score_norm = min(avg_score / 500.0, 1.0)
        comments_norm = min(avg_comments / 100.0, 1.0)

        return (0.6 * comments_norm) + (0.4 * score_norm)
