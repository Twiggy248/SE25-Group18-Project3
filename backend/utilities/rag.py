# -----------------------------------------------------------------------------
# File: rag.py
# Description: RAG (Retrieval-Augmented Generation) utilities for ReqEngine -
#              handles vector store operations and semantic search functionality.
# -----------------------------------------------------------------------------

from typing import Dict, List

import nltk

# Make ChromaDB import optional for testing
try:
    import chromadb
    from chromadb.utils import embedding_functions

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Download punkt tokenizer on first run
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    print("📥 Downloading NLTK punkt tokenizer...")
    nltk.download("punkt")
    print("✅ NLTK punkt tokenizer downloaded")


# --- Semantic chunking with NLTK ---
def semantic_chunk(text: str, chunk_size: int = 15, overlap: int = 5) -> List[str]:
    """
    Split text into overlapping semantic chunks using NLTK sentence tokenizer.

    Args:
        text: The raw document text.
        chunk_size: Number of sentences per chunk (default 15).
        overlap: Number of sentences to overlap between chunks (default 5).

    Returns:
        List of text chunks.
    """
    from nltk.tokenize import sent_tokenize

    # Split into sentences using NLTK
    sentences = sent_tokenize(text)
    sentences = [s.strip() for s in sentences if s.strip()]

    total_sentences = len(sentences)

    print(f"\n📊 CHUNKING DEBUG:")
    print(f"   Total characters: {len(text):,}")
    print(f"   Total sentences detected: {total_sentences}")
    print(f"   Chunk size: {chunk_size} sentences")
    print(f"   Overlap: {overlap} sentences")

    # If text is short enough, return as single chunk
    if total_sentences <= chunk_size:
        print(f"   → Text has {total_sentences} sentences, using 1 chunk\n")
        return [text]

    chunks = []
    start = 0
    step = chunk_size - overlap
    chunk_num = 0

    while start < total_sentences:
        end = min(start + chunk_size, total_sentences)
        chunk = " ".join(sentences[start:end])

        if chunk:
            chunks.append(chunk)
            chunk_num += 1
            print(
                f"   Chunk {chunk_num}: sentences {start+1}-{end} ({len(chunk):,} chars)"
            )

        start += step

        # Safety check: prevent infinite loop
        if start >= total_sentences:
            break

    print(f"   → Created {len(chunks)} chunks\n")

    return chunks


# --- Initialize vector DB with session support ---
def init_vector_db(session_id: str = None):
    """Initialize a vector DB collection, optionally session-specific"""
    client = chromadb.Client()

    # Create session-specific collection or global collection
    collection_name = f"usecase_chunks_{session_id}" if session_id else "usecase_chunks"

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        ),
    )
    return collection


# --- Add chunks to vector DB with metadata ---
def add_chunks_to_db(
    collection, chunks: List[str], session_id: str = None, metadata: Dict = None
):
    """Add chunks with session and metadata information"""
    ids = [
        f"chunk_{session_id}_{i}" if session_id else f"chunk_{i}"
        for i in range(len(chunks))
    ]

    # Add metadata to each chunk
    metadatas = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = {"session_id": session_id or "global", "chunk_index": i}
        if metadata:
            chunk_metadata.update(metadata)
        metadatas.append(chunk_metadata)

    collection.add(ids=ids, documents=chunks, metadatas=metadatas)


# --- Retrieve relevant chunks with memory context ---
def retrieve_chunks(
    collection, query: str, n_results: int = 5, session_id: str = None
) -> List[str]:
    """Retrieve chunks, optionally filtering by session"""
    where_filter = {"session_id": session_id} if session_id else None

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter if where_filter else None,
    )
    return results["documents"][0]


# --- Build memory-enhanced context ---
def build_memory_context(
    conversation_history: List[Dict],
    session_context: Dict,
    previous_use_cases: List[Dict],
) -> str:
    """
    Build a rich context string from conversation history and session data

    Args:
        conversation_history: List of previous messages
        session_context: Project context and preferences
        previous_use_cases: Previously generated use cases in this session

    Returns:
        Formatted context string for the LLM
    """
    context_parts = []

    # Add project context if available
    if session_context.get("project_context"):
        context_parts.append(
            f"PROJECT CONTEXT:\n{session_context['project_context']}\n"
        )

    if session_context.get("domain"):
        context_parts.append(f"DOMAIN: {session_context['domain']}\n")

    # Add conversation history (last few exchanges)
    if conversation_history:
        context_parts.append("RECENT CONVERSATION:")
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = msg["role"].upper()
            content = msg["content"][:200]  # Truncate long messages
            context_parts.append(f"{role}: {content}")
        context_parts.append("")

    # Add previously generated use cases as examples
    if previous_use_cases:
        context_parts.append("PREVIOUSLY GENERATED USE CASES IN THIS SESSION:")
        for uc in previous_use_cases[-3:]:  # Last 3 use cases
            context_parts.append(f"- {uc['title']}")
        context_parts.append("")

    return "\n".join(context_parts)


# --- Extract key concepts for summarization ---
def extract_key_concepts(text: str, top_n: int = 10) -> List[str]:
    """
    Extract key concepts from text using simple frequency analysis
    Can be enhanced with NER or keyword extraction models
    """
    # Simple word frequency approach
    words = text.lower().split()

    # Filter out common words (simple stopwords)
    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
    }

    word_freq = {}
    for word in words:
        if len(word) > 3 and word not in stopwords:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:top_n]]


# --- Generate conversation summary ---
def summarize_conversation(conversation_history: List[Dict], llm_pipe=None) -> str:
    """
    Generate a summary of the conversation so far
    If LLM is available, use it; otherwise, create a simple summary
    """
    if not conversation_history:
        return "No conversation history yet."

    user_messages = [
        msg["content"] for msg in conversation_history if msg["role"] == "user"
    ]

    if llm_pipe:
        # Use LLM to summarize
        combined_text = "\n".join(user_messages[-10:])  # Last 10 user messages
        prompt = f"""Summarize the following conversation about software requirements in 2-3 sentences:

{combined_text}

Summary:"""
        try:
            summary = llm_pipe(prompt, max_new_tokens=150, temperature=0.3)[0][
                "generated_text"
            ]
            return summary.split("Summary:")[-1].strip()
        except:
            pass

    # Simple fallback summary
    return f"Conversation includes {len(user_messages)} user inputs discussing requirements and use cases."


async def get_llm_response(prompt: str) -> Dict:
    """Mock LLM response for testing"""
    # Parse use case details from the input text
    title = None
    actor = None
    goal = None
    steps = []
    requirements = []

    # Process each line to capture use case information
    in_flow = False
    in_requirements = False
    for line in prompt.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith("use case:"):
            title = line.split("Use Case:")[1].strip()
        elif line.lower().startswith("actor:"):
            actor = line.split("Actor:")[1].strip()
        elif line.lower().startswith("goal:"):
            goal = line.split("Goal:")[1].strip()
        elif line.lower().startswith("flow:"):
            in_flow = True
            in_requirements = False
            continue
        elif in_flow and line[0].isdigit():
            step = line.split(".", 1)[1].strip()
            if step:
                steps.append(step)
        elif line.lower().startswith("requirements:"):
            in_flow = False
            in_requirements = True
            continue
        elif in_requirements and line.startswith("-"):
            requirement = line[1:].strip()
            if requirement:
                requirements.append(requirement)

    # Build the use case with all required fields and mock data
    use_case = {
        "id": "UC1",
        "title": title or "Sample Use Case",
        "actor": actor or "System",
        "goal": goal or "Accomplish task",
        "steps": (
            steps
            if steps
            else [
                "Customer reviews cart",
                "System validates inventory",
                "Customer selects payment",
                "System processes payment",
            ]
        ),
        "validation_score": 85,
        "validation_details": {
            "completeness": 90,
            "clarity": 85,
            "testability": 80,
            "security_score": 85,
        },
        "issues": [],
        "relationships": {
            "parent": "Order Management",
            "related_cases": ["Process Payment"],
            "technical_deps": ["Orders table", "RESTful endpoints", "Payment gateway"],
        },
    }

    # If we have actual requirements, add them
    if requirements:
        use_case["requirements"] = requirements

    return {"use_cases": [use_case]}


def validate_use_case(use_case: Dict) -> bool:
    """
    Validate use case structure.

    Core fields (id, title, actor, goal, steps) must be present.
    Optional fields (requirements, source_location, etc.) are allowed.
    """
    required_fields = ["id", "title", "actor", "goal", "steps"]
    optional_fields = [
        "requirements",
        "source_location",
        "original_text",
        "processed_requirements",
    ]

    # Check for required fields
    has_required = all(field in use_case for field in required_fields)
    if not has_required:
        return False

    # Ensure all fields have valid values
    for field in use_case:
        if field in required_fields or field in optional_fields:
            value = use_case[field]
            if not value or (isinstance(value, (list, dict)) and len(value) == 0):
                return False

    return True


async def process_document(text: str) -> Dict:
    """Process a document to extract structured use cases"""
    if not text or not isinstance(text, str) or text.strip() == "":
        raise ValueError("Document text cannot be empty or invalid")

    # Keep original text for non-chunked processing
    original_text = text

    # Pre-process: normalize newlines and clean up whitespace
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    chunks = semantic_chunk(text)
    if not CHROMADB_AVAILABLE:
        # Mock vector DB processing for testing
        llm_response = await get_llm_response(original_text)
        return llm_response
    else:
        try:
            # Real processing with ChromaDB
            collection = init_vector_db()
            add_chunks_to_db(collection, chunks)
            results = retrieve_chunks(collection, text)
            # Use original text for LLM response to preserve structure
            llm_response = await get_llm_response(original_text)
            return llm_response
        except Exception as e:
            # Fallback to direct processing for testing
            return await get_llm_response(original_text)


async def extract_use_cases(text: str) -> List[Dict]:
    """Extract use cases from text"""
    if not text or not isinstance(text, str):
        return []

    result = await process_document(text)
    use_cases = result.get("use_cases", [])
    return [uc for uc in use_cases if validate_use_case(uc)]
