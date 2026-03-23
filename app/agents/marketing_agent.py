"""
Marketing AI Agent
Generates blog posts, social media content, and manages email marketing campaigns.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List
import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketingAgent:
    """
    Autonomous marketing agent that:
    - Generates SEO-optimized blog posts
    - Creates social media content (Twitter, LinkedIn)
    - Manages email marketing campaigns
    - Tracks content performance metrics
    - A/B tests email subject lines
    - Maintains content calendar
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the Marketing Agent.

        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.client = anthropic.Anthropic(
            api_key=self.config.get("anthropic_api_key", "")
        )
        self.model = "claude-3-5-sonnet-20241022"
        self.content_calendar = []
        self.campaign_history = []
        self.performance_metrics = {}
        logger.info("Marketing Agent initialized")

    def generate_blog_post(self, topic: str, keywords: List[str], target_audience: str = "developers") -> dict:
        """
        Generate an SEO-optimized blog post.

        Args:
            topic: Main blog topic
            keywords: List of SEO keywords to include
            target_audience: Target audience for the post

        Returns:
            Dictionary with blog post content and metadata
        """
        blog_prompt = f"""Write a comprehensive, SEO-optimized blog post about: {topic}

Target Audience: {target_audience}
Primary Keywords: {', '.join(keywords)}
Target Length: 1500-2000 words
Tone: Professional but conversational

Structure:
1. Engaging title with primary keyword
2. Meta description (160 characters max)
3. Introduction with hook
4. 4-5 main sections with subheadings
5. Conclusion with CTA

Format your response as JSON:
{{
    "title": "Blog post title",
    "meta_description": "SEO meta description",
    "slug": "url-slug-format",
    "content": "Full blog post content",
    "keywords": ["keyword1", "keyword2"],
    "estimated_read_time": "X minutes"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": blog_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["generated_at"] = datetime.now().isoformat()
            result["type"] = "blog_post"

            logger.info(f"Blog post generated: {result['title']}")
            return result
        except Exception as e:
            logger.error(f"Blog post generation error: {e}")
            return {
                "error": str(e),
                "title": topic,
                "type": "blog_post",
                "generated_at": datetime.now().isoformat()
            }

    def generate_social_media_posts(self, content_topic: str, platforms: List[str] = None) -> dict:
        """
        Generate social media posts for multiple platforms.

        Args:
            content_topic: Topic for social posts
            platforms: List of platforms ('twitter', 'linkedin', 'instagram')

        Returns:
            Dictionary with posts for each platform
        """
        if platforms is None:
            platforms = ["twitter", "linkedin"]

        social_prompt = f"""Generate engaging social media posts about: {content_topic}

Platforms to generate for: {', '.join(platforms)}

Requirements:
- Twitter: Multiple tweet threads (280 chars each), engaging and informative
- LinkedIn: Professional post with hooks for engagement
- Instagram: Captions for visual content with relevant hashtags

Format as JSON:
{{
    "twitter": {{
        "thread": ["tweet 1", "tweet 2", "tweet 3"],
        "hashtags": ["#hashtag1", "#hashtag2"]
    }},
    "linkedin": {{
        "post": "LinkedIn post content",
        "hashtags": ["#hashtag1", "#hashtag2"]
    }},
    "instagram": {{
        "caption": "Instagram caption with emojis",
        "hashtags": ["#hashtag1", "#hashtag2"]
    }}
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": social_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["generated_at"] = datetime.now().isoformat()
            result["topic"] = content_topic

            logger.info(f"Social media posts generated for {content_topic}")
            return result
        except Exception as e:
            logger.error(f"Social media generation error: {e}")
            return {
                "error": str(e),
                "topic": content_topic,
                "generated_at": datetime.now().isoformat()
            }

    def create_email_campaign(self, campaign_type: str, segment: str) -> dict:
        """
        Create an email marketing campaign.

        Args:
            campaign_type: Type of campaign ('welcome', 'feature_announcement', 'tips_newsletter')
            segment: Target customer segment

        Returns:
            Dictionary with email campaign details
        """
        campaign_templates = {
            "welcome": "Create a 3-email welcome series for new users. Include product overview, getting started guide, and early wins guide.",
            "feature_announcement": "Create an announcement email for a new feature launch. Include benefit overview, usage instructions, and CTA.",
            "tips_newsletter": "Create a weekly tips newsletter with 3-5 actionable tips for using ContentPilot AI effectively."
        }

        campaign_prompt = f"""Create an email marketing campaign.

Campaign Type: {campaign_type}
Target Segment: {segment}
{campaign_templates.get(campaign_type, 'Create a relevant email campaign')}

For each email, provide:
- Subject line (with A/B variant)
- Preview text
- Email body (HTML-friendly)

Format as JSON:
{{
    "campaign_name": "Campaign name",
    "type": "{campaign_type}",
    "segment": "{segment}",
    "emails": [
        {{
            "sequence": 1,
            "subject_line_a": "Subject A",
            "subject_line_b": "Subject B (variant)",
            "preview_text": "Preview text",
            "body": "Email body HTML",
            "cta": "Call to action"
        }}
    ],
    "schedule": ["Day 1", "Day 3", "Day 7"]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                messages=[{"role": "user", "content": campaign_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["generated_at"] = datetime.now().isoformat()
            result["status"] = "draft"

            logger.info(f"Email campaign created: {result['campaign_name']}")
            self.campaign_history.append(result)
            return result
        except Exception as e:
            logger.error(f"Campaign creation error: {e}")
            return {
                "error": str(e),
                "type": campaign_type,
                "generated_at": datetime.now().isoformat()
            }

    def generate_seo_metadata(self, title: str, content_snippet: str) -> dict:
        """
        Generate SEO-optimized metadata.

        Args:
            title: Content title
            content_snippet: Brief content snippet

        Returns:
            Dictionary with SEO metadata
        """
        seo_prompt = f"""Generate SEO metadata for this content:

Title: {title}
Content: {content_snippet}

Provide JSON:
{{
    "meta_title": "SEO title (50-60 chars)",
    "meta_description": "Meta description (150-160 chars)",
    "h1": "H1 heading",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "slug": "url-slug",
    "focus_keyword": "main keyword",
    "related_keywords": ["related1", "related2"]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": seo_prompt}]
            )

            result = json.loads(response.content[0].text)
            logger.info(f"SEO metadata generated for: {title}")
            return result
        except Exception as e:
            logger.error(f"SEO metadata generation error: {e}")
            return {"error": str(e)}

    def plan_content_calendar(self, weeks_ahead: int = 4, topics: List[str] = None) -> dict:
        """
        Plan a content calendar for the coming weeks.

        Args:
            weeks_ahead: Number of weeks to plan
            topics: List of topics to cover

        Returns:
            Dictionary with content calendar
        """
        if topics is None:
            topics = ["AI", "automation", "productivity", "integration"]

        calendar_prompt = f"""Create a {weeks_ahead}-week content calendar.

Topics to cover: {', '.join(topics)}
Content types: blog posts, social media, email campaigns, case studies

For each week, provide:
- Week dates
- Blog post topic and keywords
- Social media themes
- Email campaign type
- Key dates/events to align with

Format as JSON:
{{
    "calendar": [
        {{
            "week": 1,
            "start_date": "YYYY-MM-DD",
            "blog_post": {{"topic": "title", "keywords": ["kw1", "kw2"]}},
            "social_media": ["topic1", "topic2"],
            "email_campaign": "campaign_type",
            "notes": "Key points"
        }}
    ],
    "performance_targets": {{
        "blog_views": "X per post",
        "social_engagement": "Y%",
        "email_open_rate": "Z%"
    }}
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": calendar_prompt}]
            )

            result = json.loads(response.content[0].text)
            self.content_calendar = result.get("calendar", [])
            logger.info(f"Content calendar planned for {weeks_ahead} weeks")
            return result
        except Exception as e:
            logger.error(f"Content calendar error: {e}")
            return {"error": str(e)}

    def track_performance(self, content_id: str, metrics: dict) -> None:
        """
        Track performance metrics for content.

        Args:
            content_id: Identifier for the content
            metrics: Dictionary with performance metrics
        """
        self.performance_metrics[content_id] = {
            "tracked_at": datetime.now().isoformat(),
            "metrics": metrics
        }
        logger.info(f"Performance tracked for {content_id}: {metrics}")

    def run(self, content_plan: dict = None) -> dict:
        """
        Run the marketing agent for periodic content generation.

        Args:
            content_plan: Optional content plan dictionary

        Returns:
            Dictionary with generated content
        """
        logger.info("Running marketing agent")

        default_plan = {
            "blog_topics": [
                {"topic": "AI Automation Best Practices", "keywords": ["automation", "AI", "efficiency"]},
            ],
            "social_topics": ["ContentPilot Features", "Customer Success Stories"],
            "campaigns": [
                {"type": "welcome", "segment": "new_users"},
                {"type": "tips_newsletter", "segment": "active_users"}
            ]
        }

        plan = content_plan or default_plan
        results = {}

        # Generate blog posts
        results["blog_posts"] = [
            self.generate_blog_post(bp["topic"], bp["keywords"])
            for bp in plan.get("blog_topics", [])
        ]

        # Generate social media posts
        results["social_posts"] = [
            self.generate_social_media_posts(topic)
            for topic in plan.get("social_topics", [])
        ]

        # Create email campaigns
        results["campaigns"] = [
            self.create_email_campaign(c["type"], c["segment"])
            for c in plan.get("campaigns", [])
        ]

        logger.info("Marketing agent run completed")
        return results


if __name__ == "__main__":
    # Example usage
    agent = MarketingAgent()

    print("=== Marketing Agent Demo ===\n")

    # Generate a blog post
    blog = agent.generate_blog_post(
        "Automating Customer Support with AI",
        ["AI", "customer support", "automation"]
    )
    print(f"Blog Post: {blog.get('title', 'N/A')}\n")

    # Generate social media posts
    social = agent.generate_social_media_posts("AI Automation Trends")
    print(f"Social Media Posts Generated\n")

    # Create email campaign
    campaign = agent.create_email_campaign("welcome", "new_users")
    print(f"Campaign: {campaign.get('campaign_name', 'N/A')}")
