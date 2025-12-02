import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.models.llm_router import get_llm_response
from sat_sight.core.config import DEBUG
import uuid

logger = logging.getLogger(__name__)

def reasoning_node(state: AgentState) -> Dict[str, Any]:
    """Reasoning Agent: Synthesizes all retrieved information and generates the final response."""
    
    logger.info(f"Reasoning Agent invoked. Current agent: {state.get('current_agent', 'unknown')}")

    query = state.get("query", "")
    image_path = state.get("image_path", "")
    retrieved_image_metadata = state.get("retrieved_image_metadata", [])
    retrieved_text_chunks = state.get("retrieved_text_chunks", [])
    web_snippets = state.get("web_snippets", [])
    wiki_content = state.get("wiki_content", None)
    wiki_source = state.get("wiki_source", None)
    short_term_memory = state.get("short_term_memory", [])
    memory_context = state.get("memory_context", "")  
    memory_summary = state.get("memory_summary", {})  
    episodic_memory = state.get("episodic_memory", [])  
    episode_id = state.get("episode_id", None)
    user_id = state.get("user_id", "anonymous")

    if not query:
        logger.error("Reasoning Agent: No query found in state.")
        return {"error_flag": True, "error_message": "Input query is missing.", "next_agent": "end"}

    context_parts = []
    context_parts.append(f"USER QUERY: {query}")

    if memory_context:
        context_parts.append("\n=== CONVERSATION HISTORY ===")
        context_parts.append(memory_context)
        context_parts.append("=== END HISTORY ===\n")
        logger.info(f"Reasoning Agent: Using memory context from memory agent ({len(memory_context)} chars)")
    elif short_term_memory:
        context_parts.append("\n=== CONVERSATION HISTORY ===")
        for i, turn in enumerate(short_term_memory[-6:]):
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            context_parts.append(f"{role.upper()}: {content}")
        context_parts.append("=== END HISTORY ===\n")
    
  
    if episodic_memory:
        context_parts.append("\n=== RELATED PAST CONVERSATIONS ===")
        for i, episode in enumerate(episodic_memory[:2]):
            past_query = episode.get("query", "")
            past_response = episode.get("response", "")
            if past_query and len(past_query) < 200:
                context_parts.append(f"Similar Query: {past_query}")
                if past_response and len(past_response) < 300:
                    context_parts.append(f"Previous Answer: {past_response[:300]}...")
        context_parts.append("=== END RELATED CONVERSATIONS ===\n")
        logger.info(f"Reasoning Agent: Including {len(episodic_memory)} similar past episodes")

    if wiki_content:
        context_parts.append(f"\n=== WIKIPEDIA KNOWLEDGE ===\nSource: {wiki_source or 'Wikipedia'}\n{wiki_content}\n=== END WIKIPEDIA ===\n")

    if retrieved_image_metadata:
        context_parts.append("\n=== IMAGE ANALYSIS ===")
        for i, meta in enumerate(retrieved_image_metadata[:3]):
            class_name = meta.get('class', 'N/A')
            description = meta.get('description', '')
            region = meta.get('region_hint', meta.get('region', ''))
            tags = meta.get('tags', [])
            distance = meta.get('distance', 1.0)
            similarity = f"{(1 - float(distance)) * 100:.1f}%"
            
            meta_str = f"Match {i+1} (Confidence: {similarity}):"
            meta_str += f"\n  Land Cover Type: {class_name}"
            if region:
                meta_str += f"\n  Location: {region}"
            if description:
                meta_str += f"\n  Description: {description}"
            if tags and isinstance(tags, list):
                meta_str += f"\n  Features: {', '.join(str(t) for t in tags[:5])}"
            context_parts.append(meta_str)
        context_parts.append("=== END IMAGE ANALYSIS ===\n")

    if retrieved_text_chunks:
        context_parts.append("\n=== KNOWLEDGE BASE (Domain Expert Knowledge) ===")
        for i, chunk in enumerate(retrieved_text_chunks[:3]):
            content = chunk.get('content', '').strip()
            source = chunk.get('source', chunk.get('metadata', {}).get('source', 'Internal KB'))
            if len(content) > 600:
                content = content[:600] + "..."
            chunk_str = f"[Source: {source}]\n{content}"
            context_parts.append(chunk_str)
        context_parts.append("=== END KNOWLEDGE BASE ===\n")

    if web_snippets:
        context_parts.append("\n=== WEB SEARCH RESULTS (Recent Information) ===")
        for i, snippet in enumerate(web_snippets[:3]):
            title = snippet.get('title', 'No Title')
            url = snippet.get('url', snippet.get('href', ''))
            content = snippet.get('content', snippet.get('body', ''))
            if len(content) > 500:
                content = content[:500] + "..."
            snippet_str = f"[{i+1}] {title}\n{content}\nSource: {url}"
            context_parts.append(snippet_str)
        context_parts.append("=== END WEB RESULTS ===\n")

    full_context = "\n".join(context_parts)
    
    query_lower = query.lower()
    is_what_question = query_lower.startswith(("what", "which"))
    is_why_question = query_lower.startswith("why")
    is_how_question = query_lower.startswith("how")
    is_risk_question = "risk" in query_lower or "threat" in query_lower or "danger" in query_lower
    
    if is_risk_question:
        specific_instruction = "Focus on identifying specific risks, their causes, and potential impacts."
    elif is_why_question:
        specific_instruction = "Focus on explaining causes, reasons, and underlying mechanisms."
    elif is_how_question:
        specific_instruction = "Focus on processes, methods, and step-by-step explanations."
    elif is_what_question:
        specific_instruction = "Focus on clear definitions, descriptions, and key characteristics."
    else:
        specific_instruction = "Provide a comprehensive, factual response."

    prompt = f"""You are a helpful AI assistant specializing in satellite imagery and environmental analysis. Provide clear, conversational answers that are easy to understand.

{full_context}

INSTRUCTIONS:
- Write in a natural, friendly tone like ChatGPT or Gemini
- NO meta-commentary about sources, confidence levels, or system limitations
- NO phrases like "Based on the image analysis which has a confidence level of 0.0%"
- NO phrases like "The query is met with..." or "Given the lack of specific data..."
- Start directly with the answer - don't explain what you're doing
- Be concise but informative (aim for 200-400 words total)
- Include specific numbers and facts when available
- Use simple language - avoid overly technical jargon unless necessary

RESPONSE STRUCTURE:
1. First paragraph: Direct answer to the question (2-3 sentences)
2. Second paragraph: Add context and details (3-4 sentences)  
3. Third paragraph: Additional insights or implications (2-3 sentences, optional)

EXAMPLES OF GOOD RESPONSES:

Query: "Show me forests"
BAD: "The query to 'Show me forests' is met with an interesting combination of sources, though none directly provide..."
GOOD: "I found several forest images in the satellite database. These show dense forest areas with extensive tree coverage, typical of temperate forest ecosystems. Forests play a crucial role in regulating climate, storing carbon, and maintaining biodiversity. They cover about 31% of Earth's land surface and absorb roughly 2.6 billion tons of CO2 annually."

Query: "What environmental problems does deforestation cause?"
GOOD: "Deforestation leads to several serious environmental problems. The most immediate impact is habitat loss, which threatens thousands of plant and animal species with extinction. When trees are removed, the area loses its ability to absorb CO2, contributing to climate change - forests normally absorb about 30% of global carbon emissions.

Beyond climate impacts, deforestation causes soil erosion, disrupts water cycles, and can trigger landslides in mountainous regions. It also affects local weather patterns and can lead to reduced rainfall in surrounding areas. Globally, agricultural expansion accounts for about 80% of deforestation, particularly in tropical regions."

Query: "Analyze this agricultural image"
GOOD: "This satellite image shows permanent crop agriculture, specifically olive orchards in a Mediterranean region. The terraced landscape helps prevent soil erosion on slopes while supporting long-term tree cultivation. Olive trees are a sustainable crop choice as they're drought-resistant and can produce for decades without replanting.

This type of agriculture differs from annual crops because the trees remain in place year-round, providing better soil stability and some wildlife habitat compared to seasonal croplands. The terracing visible here is a traditional farming technique that helps manage water runoff and maintain soil quality."

Now answer the user's query naturally and conversationally:"""

    try:
        llm_result = get_llm_response(
            prompt=prompt,
            max_tokens=500,
            temperature=0.2
        )

        final_response = llm_result.get("response", "")
        source_used = llm_result.get("source", "unknown")
        error_from_llm = llm_result.get("error", "")

        if error_from_llm:
            logger.warning(f"LLM Router error: {error_from_llm}")
            if not final_response:
                final_response = f"I encountered an issue generating a response: {error_from_llm}"

        logger.info(f"Reasoning Agent generated response using {source_used} model.")

        thinking_steps = []
        
        if retrieved_image_metadata:
            thinking_steps.append({
                "step": "Image Analysis",
                "details": f"Retrieved {len(retrieved_image_metadata)} matching images",
                "data": [
                    {
                        "class": meta.get('class', 'N/A'),
                        "confidence": f"{(1 - float(meta.get('distance', 1.0))) * 100:.1f}%",
                        "location": meta.get('region_hint', meta.get('region', 'Unknown')),
                        "description": meta.get('description', '')[:100]
                    }
                    for meta in retrieved_image_metadata[:3]
                ]
            })
        
        if retrieved_text_chunks:
            thinking_steps.append({
                "step": "Knowledge Base Search",
                "details": f"Found {len(retrieved_text_chunks)} relevant documents",
                "data": [
                    {
                        "source": chunk.get('source', 'Internal KB'),
                        "preview": chunk.get('content', '')[:150] + "..."
                    }
                    for chunk in retrieved_text_chunks[:3]
                ]
            })
        
        if wiki_content:
            thinking_steps.append({
                "step": "Wikipedia Research",
                "details": f"Retrieved information from {wiki_source or 'Wikipedia'}",
                "data": {
                    "source": wiki_source,
                    "content_length": f"{len(wiki_content)} characters"
                }
            })
        
        if web_snippets:
            thinking_steps.append({
                "step": "Web Search",
                "details": f"Found {len(web_snippets)} recent web results",
                "data": [
                    {
                        "title": snippet.get('title', 'No Title'),
                        "url": snippet.get('url', '')
                    }
                    for snippet in web_snippets[:3]
                ]
            })
        
        thinking_steps.append({
            "step": "Response Generation",
            "details": f"Synthesized answer using {source_used} model",
            "data": {
                "model": source_used,
                "response_length": f"{len(final_response)} characters"
            }
        })

        new_user_turn = {"role": "user", "content": query}
        new_assistant_turn = {"role": "assistant", "content": final_response}
        updated_stm = short_term_memory + [new_user_turn, new_assistant_turn]

        updates = {
            "current_agent": "reasoning_agent",
            "llm_response": final_response,
            "thinking_process": thinking_steps,  # NEW: For UI dropdown
            "short_term_memory": updated_stm,
            "episode_id": episode_id or str(uuid.uuid4()),
            "next_agent": "guardrail_agent" if final_response else "end",
        }

        if DEBUG:
            logger.debug(f"Reasoning Agent updates: {updates}")

        return updates

    except Exception as e:
        logger.error(f"Error in Reasoning Agent: {e}")
        import traceback
        traceback.print_exc()
        
        error_msg = f"An error occurred during processing: {str(e)}"
        error_turn = {"role": "assistant", "content": error_msg}
        updated_stm_error = short_term_memory + [error_turn]

        return {
            "error_flag": True,
            "error_message": str(e),
            "llm_response": error_msg,
            "short_term_memory": updated_stm_error,
            "episode_id": episode_id or str(uuid.uuid4()),
            "next_agent": "end"
        }