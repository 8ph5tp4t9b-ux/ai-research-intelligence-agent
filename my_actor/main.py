"""AI Research Intelligence Agent - Main Entry Point

An Apify Actor that autonomously researches any topic across the web,
integrates multi-source data, and generates structured intelligence reports.

Uses CrewAI for agent orchestration + Apify Store Actors for web data.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

os.environ.setdefault('CREWAI_TESTING', 'true')

from apify import Actor
from crewai import Agent, Crew, Task
from crewai_tools import ApifyActorsTool

if TYPE_CHECKING:
    from crewai.tools import BaseTool


async def main() -> None:
    """Main entry point for the AI Research Intelligence Agent."""
    async with Actor:
        apify_token = os.getenv('APIFY_TOKEN')
        if not apify_token:
            raise ValueError('APIFY_TOKEN environment variable must be set.')
        os.environ['APIFY_API_TOKEN'] = apify_token

        # Charge for Actor start
        await Actor.charge('actor-start')

        # Handle input
        actor_input = await Actor.get_input()

        query = actor_input.get('query')
        if not query:
            raise ValueError('Missing "query" attribute in input!')

        model_name = actor_input.get('modelName', 'gpt-4o-mini')
        depth = actor_input.get('depth', 'standard')
        max_sources = actor_input.get('maxSources', 10)
        output_format = actor_input.get('outputFormat', 'structured')

        # Determine research scope based on depth
        search_results_limit = 5 if depth == 'quick' else (10 if depth == 'standard' else 20)
        crawl_pages_limit = 3 if depth == 'quick' else (7 if depth == 'standard' else 15)

        # Build toolkit: Google Search + Website Content Crawler
        tools: list[BaseTool] = [
            ApifyActorsTool('apify/google-search-scraper'),
            ApifyActorsTool('apify/website-content-crawler'),
        ]

        # Create the Research Agent
        agent = Agent(
            role='Senior Intelligence Research Analyst',
            goal=(
                'Deliver comprehensive, well-sourced intelligence reports on any topic. '
                'You gather data from multiple web sources, cross-verify facts, '
                'and synthesize findings into actionable insights.'
            ),
            backstory=(
                'You are an elite research analyst with 15+ years of experience in '
                'market intelligence, competitive analysis, and due diligence. '
                'You specialize in: (1) finding authoritative sources quickly, '
                '(2) extracting signal from noise, (3) structuring findings '
                'into executive-ready reports. You never hallucinate facts—every '
                'claim is grounded in sourced data. You write in clear, '
                'professional business English.'
            ),
            tools=tools,
            verbose=True,
            llm=model_name,
            max_iter=15,
        )

        # Create the research task with structured output requirements
        task_description = (
            f'Research the following topic thoroughly and produce a structured intelligence report:\n\n'
            f'TOPIC: {query}\n\n'
            f'RESEARCH PARAMETERS:\n'
            f'- Depth: {depth}\n'
            f'- Max search results to analyze: {search_results_limit}\n'
            f'- Max web pages to crawl and analyze: {crawl_pages_limit}\n\n'
            f'WORKFLOW:\n'
            f'1. Use google-search-scraper to find relevant search results for the topic.\n'
            f'   Search queries: "{query}", "{query} market analysis", "{query} trends 2025 2026"\n'
            f'2. Use website-content-crawler to extract full text from the most promising URLs found.\n'
            f'3. Synthesize all gathered information into a structured report.\n\n'
            f'REQUIRED OUTPUT STRUCTURE (strict JSON format):\n'
            f'{{\n'
            f'  "executive_summary": "2-3 paragraph overview of key findings",\n'
            f'  "key_findings": [\n'
            f'    {{"finding": "...", "source": "...", "confidence": "high|medium|low"}},\n'
            f'    ...\n'
            f'  ],\n'
            f'  "market_landscape": "Analysis of key players, market size, trends",\n'
            f'  "opportunities": ["...", "..."],\n'
            f'  "risks": ["...", "..."],\n'
            f'  "recommendations": ["...", "..."],\n'
            f'  "sources": [\n'
            f'    {{"title": "...", "url": "...", "relevance": "high|medium|low"}},\n'
            f'    ...\n'
            f'  ],\n'
            f'  "raw_analysis": "Detailed narrative analysis (500-1000 words)"\n'
            f'}}\n\n'
            f'RULES:\n'
            f'- Only include facts you have actually found from sources.\n'
            f'- Cite every major claim with a source URL.\n'
            f'- If information is contradictory, present both sides and note the conflict.\n'
            f'- If a section has no data, return "insufficient data" rather than making it up.\n'
            f'- Return ONLY the JSON object, no markdown formatting or code blocks around it.'
        )

        task = Task(
            description=task_description,
            expected_output='A valid JSON object containing the structured intelligence report.',
            agent=agent,
        )

        crew = Crew(agents=[agent], tasks=[task])

        # Execute research
        crew_output = await crew.kickoff_async()
        raw_response = crew_output.raw

        Actor.log.info('Total tokens used by the model: %s', crew_output.token_usage.total_tokens)

        # Charge for task completion (price varies by depth)
        charge_event = f'task-completed-{depth}'
        await Actor.charge(charge_event)

        # Parse and validate output
        report_data = {}
        try:
            # Try to extract JSON from response (CrewAI sometimes wraps it)
            cleaned = raw_response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            report_data = json.loads(cleaned)
        except json.JSONDecodeError:
            Actor.log.warning('Failed to parse JSON from LLM response. Wrapping raw text.')
            report_data = {
                'executive_summary': raw_response[:500] + '...',
                'key_findings': [],
                'market_landscape': 'insufficient data',
                'opportunities': [],
                'risks': [],
                'recommendations': [],
                'sources': [],
                'raw_analysis': raw_response,
                'parse_error': True,
            }

        # Build final output payload
        output_payload = {
            'query': query,
            'depth': depth,
            'model_used': model_name,
            'tokens_used': crew_output.token_usage.total_tokens,
            'report': report_data,
        }

        # Also push a markdown-formatted version if requested
        if output_format == 'markdown':
            md_report = _format_markdown_report(query, report_data)
            output_payload['markdown_report'] = md_report

        await Actor.push_data(output_payload)
        Actor.log.info('Research complete. Pushed structured report to dataset.')


def _format_markdown_report(query: str, data: dict) -> str:
    """Convert structured JSON report to Markdown format."""
    lines = [
        f'# Intelligence Report: {query}',
        '',
        '---',
        '',
        '## Executive Summary',
        '',
        data.get('executive_summary', 'N/A'),
        '',
        '## Key Findings',
        '',
    ]
    for finding in data.get('key_findings', []):
        conf = finding.get('confidence', 'unknown')
        lines.append(f'- **[{conf.upper()}]** {finding.get("finding", "N/A")}')
        lines.append(f'  - Source: {finding.get("source", "N/A")}')
        lines.append('')

    lines.extend([
        '## Market Landscape',
        '',
        data.get('market_landscape', 'insufficient data'),
        '',
        '## Opportunities',
        '',
    ])
    for opp in data.get('opportunities', []):
        lines.append(f'- {opp}')
    lines.extend(['', '## Risks', ''])
    for risk in data.get('risks', []):
        lines.append(f'- {risk}')
    lines.extend(['', '## Recommendations', ''])
    for rec in data.get('recommendations', []):
        lines.append(f'- {rec}')
    lines.extend(['', '## Sources', ''])
    for src in data.get('sources', []):
        rel = src.get('relevance', 'unknown')
        lines.append(f'- [{rel.upper()}] [{src.get("title", "Untitled")}]({src.get("url", "#")})')
    lines.extend(['', '## Detailed Analysis', ''])
    lines.append(data.get('raw_analysis', 'N/A'))

    return '\n'.join(lines)
