"""
Prompts for AI trending content ideas generation

This module contains prompts used for generating trending, viral-worthy content ideas.
Helps with content strategy, ideation, and planning by identifying:
- Current trending topics and themes
- Viral content opportunities
- Seasonal and cultural relevance
- Engagement potential across different content types

Functions:
1. get_trending_ideas_prompt:
   - Used for generating trending content ideas across all content types
   - Provides creative, viral-worthy concepts for stories, memes, and free content
   - Includes seasonal relevance and viral potential analysis
   - Helps with content ideation and strategy
"""


def get_trending_ideas_prompt(content_types: list, ideas_per_type: int) -> str:
    """
    Generate the prompt for creating trending content ideas.
    
    This function generates creative, viral-worthy content ideas across different
    content types (stories, memes, free content). It's useful for:
    - Content ideation and brainstorming
    - Identifying trending topics and themes
    - Understanding what's currently viral
    - Planning content calendars
    
    Args:
        content_types: List of content types to generate ideas for 
                      (e.g., ["story", "meme", "free_content"])
        ideas_per_type: Number of ideas to generate per content type
        
    Returns:
        str: The formatted prompt for generating trending ideas
    """
    
    return f"""
    You are a viral content strategist and creative director specializing in trending, engaging content ideas.

    Task:
    Generate {ideas_per_type} highly creative, trending, and unique content ideas for each of these content types: {', '.join(content_types)}

    **IMPORTANT CRITERIA FOR IDEAS**:
    - **Trending**: Based on current social media trends, viral topics, and popular culture
    - **Creative**: Unique angles, unexpected twists, fresh perspectives
    - **Engaging**: High potential for audience interaction, shares, and comments
    - **Seasonal Relevance**: Consider current season, upcoming festivals, and cultural moments
    - **Target Demographics**: Appeal to Gen Z, Millennials, and broad audiences
    - **Viral Potential**: Ideas that have strong shareability and meme potential

    **CONTENT TYPE GUIDELINES**:

    **Story Ideas** should be:
    - Emotionally engaging narratives
    - Relatable characters and situations
    - Plot twists or surprising elements
    - Universal themes with unique execution
    - Visual storytelling potential

    **Meme Ideas** should be:
    - Highly relatable situations
    - Current internet culture references
    - Observational humor about daily life
    - Trending formats and templates
    - Cross-generational appeal

    **Free Content Ideas** should be:
    - Practical, actionable value
    - Trending topics in lifestyle, productivity, health
    - "How-to" content with unique angles
    - Problem-solving for common issues
    - Educational but entertaining

    **SEASONAL/CULTURAL CONSIDERATIONS**:
    - Current month and season themes
    - Upcoming holidays and festivals
    - Trending hashtags and challenges
    - Popular culture moments
    - Social media trends

    Return ONLY valid JSON with this EXACT structure:
    {{{{
      "trending_ideas": {{{{
        "generation_date": "...", # current date
        "trending_themes": ["..."], # current trending themes used
        "content_types": [
          {{{{
            "type": "story", # or "meme" or "free_content"
            "ideas": [
              {{{{
                "id": 1,
                "title": "...", # catchy title under 60 chars
                "concept": "...", # 2-3 sentence description
                "why_trending": "...", # why this idea is trending now
                "target_audience": "...", # primary demographic
                "viral_potential": "...", # 1-10 rating
                "hashtags": ["..."], # relevant trending hashtags
                "seasonal_relevance": "...", # how it connects to current time
                "unique_angle": "...", # what makes this idea special
                "engagement_hooks": ["..."] # elements that drive engagement
              }}}}
            ]
          }}}}
        ]
      }}}}
    }}}}
    """
