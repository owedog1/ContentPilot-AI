"""
AI Content Generation Service
Handles all AI-powered content generation using Anthropic Claude API with OpenAI fallback
"""
import logging
from typing import Optional, Tuple
from anthropic import Anthropic, APIError as AnthropicAPIError
try:
    from openai import OpenAI, APIError as OpenAIAPIError
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None
    OpenAIAPIError = Exception
import os

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered content generation"""

    def __init__(self):
        """Initialize AI service with API clients"""
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        self.anthropic_client = None
        self.openai_client = None

        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
        if self.openai_api_key and HAS_OPENAI:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

    def _get_system_prompt(self, content_type: str) -> str:
        """Get system prompt based on content type"""
        prompts = {
            "blog_post": """You are an expert blog writer and SEO specialist. Write engaging, informative blog posts that rank well in search engines.
            Your blog posts should have:
            - Compelling headline
            - Meta description (max 160 chars)
            - Introduction that hooks the reader
            - Well-structured body with subheadings
            - Actionable insights and examples
            - Strong conclusion with CTA
            - 1000-2000 words""",

            "social_media": """You are a social media expert specializing in creating viral content.
            Create engaging posts for Twitter, LinkedIn, and Instagram. Posts should:
            - Be platform-specific (Twitter: concise, LinkedIn: professional, Instagram: engaging)
            - Include relevant hashtags
            - Be conversational and authentic
            - Include CTAs or questions to drive engagement
            - Optimal length for each platform""",

            "email_copy": """You are an email marketing expert. Write compelling email copy that converts.
            Your emails should:
            - Have subject lines that achieve 45%+ open rates
            - Personalized and conversational tone
            - Clear value proposition
            - Strong call-to-action
            - Mobile-friendly formatting
            - Avoid spam trigger words""",

            "ad_copy": """You are a digital advertising copywriter with expertise in Google Ads, Facebook Ads, and LinkedIn Ads.
            Create high-converting ad copy that includes:
            - Attention-grabbing headlines
            - Compelling descriptions highlighting unique value
            - Clear and specific CTAs
            - Benefit-focused messaging
            - Emotional triggers and urgency when appropriate""",

            "seo_content": """You are an SEO content specialist. Write keyword-optimized content that ranks.
            Your content should:
            - Be optimized for target keywords (include 2-3 variations naturally)
            - Have proper heading hierarchy (H1, H2, H3)
            - Include internal linking suggestions
            - Use meta descriptions and title tags
            - Answer user intent completely
            - Include relevant FAQ section""",

            "product_description": """You are a product copywriter specializing in e-commerce.
            Write compelling product descriptions that:
            - Start with the key benefit
            - Highlight unique features
            - Address customer pain points
            - Include social proof suggestions
            - Have clear product specifications
            - Include persuasive CTAs
            - Are SEO-optimized"""
        }
        return prompts.get(content_type, "You are a professional content writer.")

    async def generate_blog_post(self, topic: str, keywords: Optional[str] = None) -> Tuple[dict, int]:
        """
        Generate a complete blog post
        Returns: (content_dict, tokens_used)
        """
        prompt = f"""Write a comprehensive blog post about: {topic}
        {f'Target keywords: {keywords}' if keywords else ''}

        Format the response as follows:
        TITLE: [Your blog title]
        META_DESCRIPTION: [SEO meta description - max 160 chars]
        BODY: [Full blog post content]"""

        system_prompt = self._get_system_prompt("blog_post")
        content, tokens = await self._call_ai(prompt, system_prompt)

        # Parse response
        result = self._parse_blog_response(content)
        result["type"] = "blog_post"
        return result, tokens

    async def generate_social_media(self, topic: str, platform: str = "twitter") -> Tuple[dict, int]:
        """
        Generate social media post(s)
        Supports: twitter, linkedin, instagram
        """
        prompt = f"""Create a {platform} post about: {topic}

        Format as follows:
        PLATFORM: {platform}
        POST: [Your post content with relevant hashtags and emojis if appropriate]"""

        system_prompt = self._get_system_prompt("social_media")
        content, tokens = await self._call_ai(prompt, system_prompt)

        result = {"type": "social_media", "platform": platform, "content": content}
        return result, tokens

    async def generate_email_copy(self, subject: str, purpose: str) -> Tuple[dict, int]:
        """Generate email marketing copy with subject line and body"""
        prompt = f"""Create an email marketing piece with:
        Subject: {subject}
        Purpose: {purpose}

        Format as follows:
        SUBJECT_LINE: [Compelling subject line]
        BODY: [Email body content]
        CTA: [Clear call-to-action]"""

        system_prompt = self._get_system_prompt("email_copy")
        content, tokens = await self._call_ai(prompt, system_prompt)

        result = self._parse_email_response(content)
        result["type"] = "email_copy"
        return result, tokens

    async def generate_ad_copy(self, product: str, audience: str = "") -> Tuple[dict, int]:
        """Generate advertising copy for various platforms"""
        prompt = f"""Create ad copy for: {product}
        {f'Target audience: {audience}' if audience else ''}

        Format as follows:
        HEADLINE: [Attention-grabbing headline]
        DESCRIPTION: [Compelling description]
        CTA: [Clear call-to-action]
        AD_VARIATIONS: [2-3 alternative versions]"""

        system_prompt = self._get_system_prompt("ad_copy")
        content, tokens = await self._call_ai(prompt, system_prompt)

        result = self._parse_ad_response(content)
        result["type"] = "ad_copy"
        return result, tokens

    async def generate_seo_content(self, topic: str, keywords: str) -> Tuple[dict, int]:
        """Generate SEO-optimized content"""
        prompt = f"""Create SEO-optimized content for:
        Topic: {topic}
        Keywords: {keywords}

        Format as follows:
        TITLE: [SEO-optimized title]
        META_DESCRIPTION: [Meta description]
        CONTENT: [SEO-optimized article content]
        FAQ_SECTION: [FAQ with target keywords]"""

        system_prompt = self._get_system_prompt("seo_content")
        content, tokens = await self._call_ai(prompt, system_prompt)

        result = self._parse_seo_response(content)
        result["type"] = "seo_content"
        return result, tokens

    async def generate_product_description(self, product_name: str, features: str) -> Tuple[dict, int]:
        """Generate product description for e-commerce"""
        prompt = f"""Write a compelling product description for:
        Product: {product_name}
        Features/Specs: {features}

        Format as follows:
        SHORT_DESCRIPTION: [100-150 word marketing description]
        LONG_DESCRIPTION: [Detailed product description]
        BULLET_POINTS: [5-7 key features as bullets]
        CTA: [Persuasive call-to-action]"""

        system_prompt = self._get_system_prompt("product_description")
        content, tokens = await self._call_ai(prompt, system_prompt)

        result = self._parse_product_response(content)
        result["type"] = "product_description"
        return result, tokens

    async def _call_ai(self, prompt: str, system_prompt: str) -> Tuple[str, int]:
        """
        Call AI API with fallback mechanism
        First tries Anthropic Claude, falls back to OpenAI if needed
        Returns: (generated_content, tokens_used)
        """
        try:
            if self.anthropic_client:
                logger.info("Using Anthropic Claude API")
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                # Calculate tokens (Anthropic provides usage info)
                tokens = response.usage.output_tokens + response.usage.input_tokens
                return response.content[0].text, tokens
        except (AnthropicAPIError, Exception) as e:
            logger.warning(f"Anthropic API failed: {str(e)}, falling back to OpenAI")

        # Fallback to OpenAI
        try:
            if self.openai_client:
                logger.info("Using OpenAI GPT API")
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=2000,
                    temperature=0.7,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                tokens = response.usage.total_tokens
                return response.choices[0].message.content, tokens
        except (OpenAIAPIError, Exception) as e:
            logger.error(f"OpenAI API failed: {str(e)}")

        # Mock response if both APIs fail (for development)
        logger.warning("Both APIs unavailable, using mock response")
        return self._generate_mock_response(prompt), 100

    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response for development/testing"""
        return f"""[Mock Response - API Unavailable]

This is a mock response generated because the AI APIs are not configured or available.

Original request: {prompt[:100]}...

In production, this would contain actual AI-generated content from Claude or GPT.
Please ensure ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables are set."""

    @staticmethod
    def _parse_blog_response(content: str) -> dict:
        """Parse blog post response"""
        result = {"content": content}
        lines = content.split("\n")
        for line in lines:
            if line.startswith("TITLE:"):
                result["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("META_DESCRIPTION:"):
                result["meta_description"] = line.replace("META_DESCRIPTION:", "").strip()
        return result

    @staticmethod
    def _parse_email_response(content: str) -> dict:
        """Parse email response"""
        result = {"content": content}
        lines = content.split("\n")
        for line in lines:
            if line.startswith("SUBJECT_LINE:"):
                result["subject_line"] = line.replace("SUBJECT_LINE:", "").strip()
            elif line.startswith("CTA:"):
                result["cta"] = line.replace("CTA:", "").strip()
        return result

    @staticmethod
    def _parse_ad_response(content: str) -> dict:
        """Parse ad copy response"""
        result = {"content": content}
        lines = content.split("\n")
        for line in lines:
            if line.startswith("HEADLINE:"):
                result["headline"] = line.replace("HEADLINE:", "").strip()
            elif line.startswith("CTA:"):
                result["cta"] = line.replace("CTA:", "").strip()
        return result

    @staticmethod
    def _parse_seo_response(content: str) -> dict:
        """Parse SEO content response"""
        result = {"content": content}
        lines = content.split("\n")
        for line in lines:
            if line.startswith("TITLE:"):
                result["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("META_DESCRIPTION:"):
                result["meta_description"] = line.replace("META_DESCRIPTION:", "").strip()
        return result

    @staticmethod
    def _parse_product_response(content: str) -> dict:
        """Parse product description response"""
        result = {"content": content}
        lines = content.split("\n")
        for line in lines:
            if line.startswith("SHORT_DESCRIPTION:"):
                result["short_description"] = line.replace("SHORT_DESCRIPTION:", "").strip()
        return result
