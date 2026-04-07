import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from services.utils import extract_webpage_content

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 🔥 TEMP MEMORY STORE (POC)
SESSION_STORE = {}


def generate_content_brief(data):
    try:
        session_id = str(len(SESSION_STORE) + 1)

        # 🔹 Build input context
        if data.task_type == "create":
            input_context = f"Topic: {data.topic}"
        else:
            extracted_content = extract_webpage_content(data.page_url)

            input_context = f"""
Existing Page URL: {data.page_url}

EXTRACTED CONTENT:
{extracted_content}

TASK:
Analyze this content and improve SEO structure, headings, and coverage.
"""

        # 🔹 Prompt
        prompt = f"""
You are an expert SEO strategist.

Generate a COMPLETE CONTENT BRIEF in STRICT JSON format.

⚠️ RULES:
- Follow ALL specifications strictly
- Do NOT skip any field
- Return ONLY JSON (no explanation)

INPUT:
{input_context}

Primary Keyword: {data.primary_keyword}
Secondary Keywords: {', '.join(data.secondary_keywords)}
Website URL: {data.website_url}

Key Services:
{', '.join(data.key_services)}

Key Competitors:
{', '.join(data.key_competitors)}
Audience: {data.target_audience}
Funnel Stage: {data.funnel_stage}
Location: {data.target_location}
Word Count: {data.word_count}
Page Type: {data.page_type}
Tone: {data.brand_tone}

OUTPUT FORMAT:
{{
  "meta_title": "",
  "meta_description": "",
  "url_slug": "",

  "primary_keyword": "{data.primary_keyword}",
  "secondary_keywords": {data.secondary_keywords},

  "h1": "",
  "h1_caption": "",

  "h2": [],
  "h3": [],

  "tldr": [],

  "verifiable_facts": [
    {{"fact": "", "source": ""}},
    {{"fact": "", "source": ""}}
  ],

  "eeat_link": "",

  "external_links": [],

  "faqs": [
    {{"question": "", "answer": ""}},
    {{"question": "", "answer": ""}},
    {{"question": "", "answer": ""}},
    {{"question": "", "answer": ""}}
  ],

  "header_table": {{
    "h1": "",
    "h2": [],
    "h3": []
  }}
}}
"""

        # 🔥 CALL CLAUDE API
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            temperature=0.4,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        raw_output = response.content[0].text.strip()

        # 🧹 Clean output (remove markdown if Claude adds it)
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]

        # 🔄 Convert to JSON
        try:
            parsed_output = json.loads(raw_output)
        except Exception:
            return {
                "success": False,
                "error": "Claude returned invalid JSON",
                "raw_output": raw_output
            }

        # 🔥 Store session
        SESSION_STORE[session_id] = {
            "input": data.dict(),
            "brief": parsed_output
        }
        html_output = format_brief_as_html(parsed_output)

        return {
            "success": True,
            "session_id": session_id,
            "data": html_output
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_full_article(session_id):
    try:
        session_data = SESSION_STORE.get(session_id)

        if not session_data:
            return {"success": False, "error": "Invalid session_id"}

        brief = session_data["brief"]
        original_input = session_data["input"]

        prompt = f"""
You are an expert SEO content writer.
- Ensure content matches or exceeds top-ranking Google articles
Generate a COMPLETE, HIGH-QUALITY FULL ARTICLE strictly following the specifications below.

━━━━━━━━━━━━━━━━━━━━━━━
🔴 STRICT REQUIREMENTS (DO NOT VIOLATE)
━━━━━━━━━━━━━━━━━━━━━━━

1. STRUCTURE:
- H1: EXACTLY 1
- H2: 5–6 sections
- H3: 3–4 sub-sections (nested properly under H2)
- Maintain logical hierarchy

2. DEPTH:
- Each H2 section: MINIMUM 150–200 words
- Each H3 section: MINIMUM 100–150 words
- No short or generic content
- Add explanations, examples, and insights

3. TLDR SUMMARY (MANDATORY)
- At the very top
- 3–4 bullet points

4. HEADER TABLE (MANDATORY)
- At the top after TLDR
- Show H1, H2, H3 in table format

5. FAQs (MANDATORY – DO NOT SKIP)
- 4–5 unique questions
- Must NOT repeat content from article
- Must appear ONLY at the END
- Each answer must be detailed

⚠️ If FAQ section is missing → OUTPUT IS INVALID

6. CTAs (MANDATORY)
- 1–2 CTAs
- Must include trust signals (e.g., industry expertise, credibility)

7. VERIFIABLE FACTS (MANDATORY)
- Include 1–2 facts inside article
- MUST include source URLs inline

8. INFOGRAPHIC SECTION (MANDATORY)
- Add one section
- Include alt text
- Do NOT repeat content from article

9. ASSET RECOMMENDATION (MANDATORY)
- Recommend ONE asset (whitepaper / checklist / webinar / video)
- Must be relevant to:
  Website: {original_input['website_url']}
- Include compelling CTA

10. INTERNAL LINKS (MANDATORY)
- Suggest links based on:
  Website: {original_input['website_url']}
- Must be relevant to topic

11. EXTERNAL LINKS (MANDATORY)
- 1–2 authority links (Forbes, Gartner, etc.)
- 1–2 links from:
  analyst / review / news / blogs
  mentioning competitors positively:
  {', '.join(original_input['key_competitors'])}

12. SEO REQUIREMENTS:
- Primary keyword: {original_input['primary_keyword']}
- Secondary keywords: {', '.join(original_input['secondary_keywords'])}
- Use keywords naturally (no stuffing)

13. BRAND CONTEXT (VERY IMPORTANT):
- Website: {original_input['website_url']}
- Key Services: {', '.join(original_input['key_services'])}
- Competitors: {', '.join(original_input['key_competitors'])}

👉 Content must align with brand positioning and services

14. TONE:
- Third-person only
- No "I", "We", "Our"
- Tone: {original_input['brand_tone']}
- Professional, authoritative

15. WORD COUNT:
- MUST reach {original_input['word_count']} words

━━━━━━━━━━━━━━━━━━━━━━━
📘 CONTENT BRIEF
━━━━━━━━━━━━━━━━━━━━━━━
{json.dumps(brief, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT (STRICT ORDER)
━━━━━━━━━━━━━━━━━━━━━━━

1. TLDR Summary
2. Header Table
3. H1 Title
4. Full Article Content (H2 + H3 properly structured)
5. Infographic Section
6. Asset Recommendation
7. CTAs
8. Internal Links
9. External Links
10. FAQs (LAST SECTION)

⚠️ DO NOT MISS ANY SECTION
⚠️ DO NOT RETURN PARTIAL OUTPUT
⚠️ DO NOT SUMMARIZE — WRITE FULL ARTICLE

Return clean, well-formatted markdown.
"""

        # 🔥 CALL CLAUDE
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            temperature=0.4,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        article = response.content[0].text

        return {
            "success": True,
            "status": "generated",
            "session_id": session_id,
            "article": article
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
def format_brief_as_html(brief):
    return f"""
    <h2>📊 Content Brief</h2>

    <h3>Meta</h3>
    <p><b>Title:</b> {brief['meta_title']}</p>
    <p><b>Description:</b> {brief['meta_description']}</p>

    <h3>H1</h3>
    <p>{brief['h1']}</p>
    <p><i>{brief['h1_caption']}</i></p>

    <h3>H2</h3>
    <ul>{"".join(f"<li>{h}</li>" for h in brief['h2'])}</ul>

    <h3>H3</h3>
    <ul>{"".join(f"<li>{h}</li>" for h in brief['h3'])}</ul>

    <h3>TLDR</h3>
    <ul>{"".join(f"<li>{t}</li>" for t in brief['tldr'])}</ul>

    <h3>FAQs</h3>
    <ul>{"".join(f"<li><b>{f['question']}</b>: {f['answer']}</li>" for f in brief['faqs'])}</ul>
    """