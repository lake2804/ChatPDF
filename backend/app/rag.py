"""
RAG (Retrieval-Augmented Generation) pipeline module.
Handles document indexing, retrieval, and answer generation.
"""
from typing import List, Dict, Optional, Iterator
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from app.loader import load_document
from app.vision import caption_image_bytes, ocr_image_bytes
from app.embeddings import GoogleEmbeddings
from app.store import create_collection_if_not_exists, create_vectorstore_from_docs, get_vectorstore, get_qdrant_client
from app.config import (
    QDRANT_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP, 
    DEFAULT_K, LLM_MODEL, GOOGLE_API_KEY
)
from google import genai
import logging

logger = logging.getLogger(__name__)

# Initialize Google GenAI client for LLM
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY is not set. Some features may not work.")
    client = None
else:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI client: {e}")
        client = None


def build_and_store_index(file_path: str, force_recreate: bool = False) -> int:
    """
    Build and store document index in vector database.
    
    Args:
        file_path: Path to the document file
        force_recreate: If True, recreate collection if dimension mismatch
    
    Returns:
        Number of chunks indexed
    """
    logger.info(f"Building index for: {file_path}")
    
    # 1. Load documents and images
    text_docs, images = load_document(file_path)
    logger.info(f"Loaded {len(text_docs)} text documents and {len(images)} images")
    
    # 2. Split text documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    
    split_text_docs = []
    for doc in text_docs:
        split_docs = text_splitter.split_documents([doc])
        split_text_docs.extend(split_docs)
    
    logger.info(f"Split into {len(split_text_docs)} text chunks")
    
    # 3. Process images: OCR + Caption
    image_docs = []
    for i, (img_bytes, metadata) in enumerate(images):
        logger.info(f"Processing image {i+1}/{len(images)}")
        
        try:
            # OCR
            ocr_text = ocr_image_bytes(img_bytes)
            if ocr_text:
                ocr_doc = Document(
                    page_content=f"[IMAGE OCR] {ocr_text}",
                    metadata={**metadata, "content_type": "ocr"}
                )
                image_docs.append(ocr_doc)
        except Exception as e:
            logger.warning(f"Error processing OCR for image {i+1}: {e}")
        
        try:
            # Caption
            caption = caption_image_bytes(img_bytes, detailed=True)
            if caption:
                caption_doc = Document(
                    page_content=f"[IMAGE DESCRIPTION] {caption}",
                    metadata={**metadata, "content_type": "caption"}
                )
                image_docs.append(caption_doc)
        except Exception as e:
            logger.warning(f"Error processing caption for image {i+1}: {e}")
    
    logger.info(f"Created {len(image_docs)} image-based documents")
    
    # 4. Combine all documents
    all_docs = split_text_docs + image_docs
    logger.info(f"Total documents to index: {len(all_docs)}")
    
    if not all_docs:
        raise ValueError("No documents to index. File may be empty or unreadable.")
    
    # 5. Create collection if needed
    try:
        create_collection_if_not_exists()
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise ValueError(f"Cannot connect to Qdrant vector database: {str(e)}")
    
    # 6. Generate embeddings and store
    try:
        embeddings = GoogleEmbeddings()
    except Exception as e:
        logger.error(f"Error initializing embeddings: {e}")
        raise ValueError(f"Failed to initialize embeddings: {str(e)}")
    
    try:
        vectorstore = create_vectorstore_from_docs(all_docs, embeddings, force_recreate=force_recreate)
    except Exception as e:
        logger.error(f"Error storing documents in vectorstore: {e}")
        error_msg = str(e)
        if "qdrant" in error_msg.lower() or "connection" in error_msg.lower():
            raise ValueError(f"Cannot connect to Qdrant vector database: {error_msg}")
        else:
            raise ValueError(f"Failed to store documents: {error_msg}")
    
    logger.info(f"Successfully indexed {len(all_docs)} chunks")
    return len(all_docs)


def _detect_language(text: str) -> str:
    """Detect language from text. Returns 'vi' for Vietnamese, 'en' for English, or 'auto'."""
    # Vietnamese character set
    vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ'
    
    # Count Vietnamese characters
    vi_count = sum(1 for char in text if char in vietnamese_chars)
    total_chars = len([c for c in text if c.isalpha()])
    
    # If more than 5% Vietnamese characters or Vietnamese words detected, consider it Vietnamese
    if total_chars > 0 and (vi_count / total_chars > 0.05 or vi_count > 3):
        return 'vi'
    
    # Check for common Vietnamese words
    vietnamese_words = ['là', 'của', 'và', 'với', 'cho', 'được', 'trong', 'về', 'này', 'đó', 
                        'như', 'theo', 'từ', 'đến', 'có', 'không', 'một', 'các', 'đã', 'sẽ']
    text_lower = text.lower()
    vi_word_count = sum(1 for word in vietnamese_words if word in text_lower)
    if vi_word_count >= 2:
        return 'vi'
    
    return 'en'


def _generate_answer_stream(context: str, question: str) -> Iterator[str]:
    """Generate streaming answer."""
    if not client:
        raise ValueError("Google API client is not initialized. Please check GOOGLE_API_KEY in .env file.")
    
    # Detect language from question
    detected_lang = _detect_language(question)
    
    if detected_lang == 'vi':
        language_instruction = """Trả lời bằng tiếng Việt một cách chi tiết, đầy đủ và rõ ràng. 
        - Sử dụng ngôn ngữ tự nhiên, dễ hiểu
        - Giải thích đầy đủ các khái niệm
        - Cung cấp ví dụ cụ thể khi có thể
        - Trình bày có cấu trúc với các đoạn văn rõ ràng"""
    else:
        language_instruction = """Answer in the same language as the question, providing a detailed, comprehensive, and well-structured response.
        - Use natural, clear language
        - Explain concepts thoroughly
        - Provide specific examples when possible
        - Structure your response with clear paragraphs"""
    
    prompt = f"""You are an expert AI assistant specialized in document analysis and question answering. Your task is to provide detailed, comprehensive, and well-structured answers based on the provided context.

Context from documents:
{context}

User's question: {question}

CRITICAL INSTRUCTIONS - FOLLOW THESE CAREFULLY:

1. LANGUAGE REQUIREMENT: {language_instruction}
   - Match the language of the question exactly
   - If question is in Vietnamese, answer in Vietnamese
   - If question is in English, answer in English
   - Maintain consistency throughout the response

2. LENGTH AND COMPREHENSIVENESS (VERY IMPORTANT):
   - Provide a THOROUGH, DETAILED answer - NOT a brief summary
   - Aim for at least 300-500 words for complex questions, 150-300 words for simpler ones
   - Elaborate on ALL relevant points mentioned in the context
   - Include background information and context when relevant
   - Do NOT give short, one-sentence answers
   - Expand on each point with explanations and details

3. STRUCTURE AND ORGANIZATION:
   - Start with a brief introduction that summarizes what you'll cover
   - Organize main points clearly with:
     * Clear paragraphs for each major point
     * Bullet points or numbered lists for multiple items
     * Subheadings or bold text for key sections (if using markdown)
   - Include specific examples, data, or quotes from the context
   - End with a brief conclusion or summary if appropriate

4. DETAIL AND DEPTH:
   - Include ALL relevant information from the context
   - If multiple sources mention the same topic, synthesize them comprehensively
   - Explain relationships between different pieces of information
   - Provide context and background when helpful
   - Don't skip important details - be thorough

5. FORMATTING AND READABILITY:
   - Use clear paragraphs (2-4 sentences each)
   - Use bullet points (•) or numbered lists (1., 2., 3.) for multiple items
   - Use line breaks to separate major sections
   - Bold or emphasize key terms when appropriate (using **bold** in markdown)
   - Make the answer easy to scan and read

6. CITATIONS AND SOURCES:
   - Reference specific sources when mentioning information
   - Use phrases like "According to Source 1...", "As mentioned in the document...", "The text states..."
   - When multiple sources agree, mention that

7. COMPLETENESS:
   - Ensure your answer FULLY addresses the question
   - If the question asks for multiple aspects, cover ALL of them
   - If the question has sub-questions, answer each one
   - Don't leave any part of the question unanswered

8. IMAGES AND VISUAL CONTENT:
   - If the question is about images, refer to the image descriptions and OCR text provided
   - Describe visual elements in detail when relevant

9. CLARITY AND PROFESSIONALISM:
   - Write in a clear, professional manner
   - Use appropriate terminology from the context
   - Define technical terms if needed
   - Ensure the answer is easy to understand

10. QUALITY CHECK:
    - Before finalizing, ensure the answer is:
      * Long enough (not too brief)
      * Comprehensive (covers all aspects)
      * Well-structured (easy to read)
      * In the correct language
      * Based on the provided context

REMEMBER: The user expects a THOROUGH, DETAILED response that fully answers their question. Do NOT provide a brief summary. Be comprehensive, clear, and well-organized.
"""
    response = client.models.generate_content_stream(
        model=LLM_MODEL,
        contents=prompt,
        config={
            "temperature": 0.7,
            # No max_output_tokens limit - let the model generate as much as needed for comprehensive answers
        }
    )
    
    for chunk in response:
        if chunk.text:
            yield chunk.text


def generate_answer(context: str, question: str, stream: bool = False):
    """
    Generate answer using LLM with context.
    
    Args:
        context: Retrieved context documents
        question: User question
        stream: If True, return streaming response
    
    Returns:
        Answer string or iterator of chunks
    """
    if stream:
        return _generate_answer_stream(context, question)
    
    # Non-streaming response
    if not client:
        raise ValueError("Google API client is not initialized. Please check GOOGLE_API_KEY in .env file.")
    
    # Detect language from question
    detected_lang = _detect_language(question)
    
    if detected_lang == 'vi':
        language_instruction = """Trả lời bằng tiếng Việt một cách chi tiết, đầy đủ và rõ ràng. 
        - Sử dụng ngôn ngữ tự nhiên, dễ hiểu
        - Giải thích đầy đủ các khái niệm
        - Cung cấp ví dụ cụ thể khi có thể
        - Trình bày có cấu trúc với các đoạn văn rõ ràng"""
    else:
        language_instruction = """Answer in the same language as the question, providing a detailed, comprehensive, and well-structured response.
        - Use natural, clear language
        - Explain concepts thoroughly
        - Provide specific examples when possible
        - Structure your response with clear paragraphs"""
    
    prompt = f"""You are an expert AI assistant specialized in document analysis and question answering. Your task is to provide detailed, comprehensive, and well-structured answers based on the provided context.

Context from documents:
{context}

User's question: {question}

CRITICAL INSTRUCTIONS - FOLLOW THESE CAREFULLY:

1. LANGUAGE REQUIREMENT: {language_instruction}
   - Match the language of the question exactly
   - If question is in Vietnamese, answer in Vietnamese
   - If question is in English, answer in English
   - Maintain consistency throughout the response

2. LENGTH AND COMPREHENSIVENESS (VERY IMPORTANT):
   - Provide a THOROUGH, DETAILED answer - NOT a brief summary
   - Aim for at least 300-500 words for complex questions, 150-300 words for simpler ones
   - Elaborate on ALL relevant points mentioned in the context
   - Include background information and context when relevant
   - Do NOT give short, one-sentence answers
   - Expand on each point with explanations and details

3. STRUCTURE AND ORGANIZATION:
   - Start with a brief introduction that summarizes what you'll cover
   - Organize main points clearly with:
     * Clear paragraphs for each major point
     * Bullet points or numbered lists for multiple items
     * Subheadings or bold text for key sections (if using markdown)
   - Include specific examples, data, or quotes from the context
   - End with a brief conclusion or summary if appropriate

4. DETAIL AND DEPTH:
   - Include ALL relevant information from the context
   - If multiple sources mention the same topic, synthesize them comprehensively
   - Explain relationships between different pieces of information
   - Provide context and background when helpful
   - Don't skip important details - be thorough

5. FORMATTING AND READABILITY:
   - Use clear paragraphs (2-4 sentences each)
   - Use bullet points (•) or numbered lists (1., 2., 3.) for multiple items
   - Use line breaks to separate major sections
   - Bold or emphasize key terms when appropriate (using **bold** in markdown)
   - Make the answer easy to scan and read

6. CITATIONS AND SOURCES:
   - Reference specific sources when mentioning information
   - Use phrases like "According to Source 1...", "As mentioned in the document...", "The text states..."
   - When multiple sources agree, mention that

7. COMPLETENESS:
   - Ensure your answer FULLY addresses the question
   - If the question asks for multiple aspects, cover ALL of them
   - If the question has sub-questions, answer each one
   - Don't leave any part of the question unanswered

8. IMAGES AND VISUAL CONTENT:
   - If the question is about images, refer to the image descriptions and OCR text provided
   - Describe visual elements in detail when relevant

9. CLARITY AND PROFESSIONALISM:
   - Write in a clear, professional manner
   - Use appropriate terminology from the context
   - Define technical terms if needed
   - Ensure the answer is easy to understand

10. QUALITY CHECK:
    - Before finalizing, ensure the answer is:
      * Long enough (not too brief)
      * Comprehensive (covers all aspects)
      * Well-structured (easy to read)
      * In the correct language
      * Based on the provided context

REMEMBER: The user expects a THOROUGH, DETAILED response that fully answers their question. Do NOT provide a brief summary. Be comprehensive, clear, and well-organized.
"""
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config={
            "temperature": 0.7,
            # No max_output_tokens limit - let the model generate as much as needed for comprehensive answers
        }
    )
    # Handle different response formats from Google API
    try:
        # Try to get text directly
        if hasattr(response, 'text') and response.text:
            return str(response.text)
        
        # Try to get from candidates
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content'):
                if hasattr(candidate.content, 'parts'):
                    text_parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(str(part.text))
                    if text_parts:
                        return ' '.join(text_parts)
                elif hasattr(candidate.content, 'text'):
                    return str(candidate.content.text)
        
        # Try string conversion
        if isinstance(response, str):
            return response
        
        # Last resort: convert to string
        response_str = str(response)
        if response_str and response_str != "None":
            return response_str
        else:
            return "I apologize, but I couldn't generate a response. Please try again."
    except Exception as e:
        logger.error(f"Error parsing Google API response: {e}", exc_info=True)
        logger.error(f"Response type: {type(response)}, Response: {response}")
        raise ValueError(f"Failed to parse response from Google API: {str(e)}")


def rag_query(question: str, k: int = None, stream: bool = False) -> Dict:
    """
    Perform RAG query: retrieve relevant documents and generate answer.
    
    Args:
        question: User question
        k: Number of documents to retrieve (defaults to config)
        stream: If True, return streaming response
    
    Returns:
        Dictionary with answer, sources, and metadata
    """
    k = k or DEFAULT_K
    
    try:
        # Get vectorstore
        embeddings = GoogleEmbeddings()
        vectorstore = get_vectorstore(embeddings)
        
        # Retrieve relevant documents
        # Handle different LangChain versions - try multiple methods
        docs = None
        last_error = None
        
        # Method 1: Try similarity_search directly (most reliable)
        try:
            docs = vectorstore.similarity_search(question, k=k)
            logger.debug(f"Retrieved {len(docs)} documents using similarity_search")
        except Exception as e1:
            last_error = e1
            logger.warning(f"similarity_search failed: {e1}, trying retriever methods")
            
            # Method 2: Try using retriever with invoke (LangChain v0.1+)
            try:
                retriever = vectorstore.as_retriever(search_kwargs={"k": k})
                if hasattr(retriever, 'invoke'):
                    docs = retriever.invoke(question)
                    logger.debug(f"Retrieved {len(docs)} documents using retriever.invoke")
                elif hasattr(retriever, '__call__'):
                    # Try calling retriever directly
                    docs = retriever(question)
                    logger.debug(f"Retrieved {len(docs)} documents using retriever()")
                else:
                    raise AttributeError("Retriever has no invoke or __call__ method")
            except Exception as e2:
                last_error = e2
                logger.warning(f"retriever methods failed: {e2}, trying search method")
                
                # Method 3: Try search method if available
                try:
                    if hasattr(vectorstore, 'search'):
                        docs = vectorstore.search(question, k=k)
                        logger.debug(f"Retrieved {len(docs)} documents using search")
                    else:
                        raise AttributeError("No search method available")
                except Exception as e3:
                    last_error = e3
                    logger.error(f"All retrieval methods failed. Last error: {e3}")
                    raise ValueError(f"Failed to retrieve documents: {str(e3)}")
        
        if not docs:
            raise ValueError("No documents retrieved. Please ensure documents are indexed.")
            
    except ValueError as ve:
        # Re-raise ValueError as-is (these are our custom errors)
        raise ve
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}", exc_info=True)
        # Check if collection exists
        try:
            qdrant_client = get_qdrant_client()
            collections = qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]
            if QDRANT_COLLECTION not in collection_names:
                raise ValueError("No documents indexed. Please upload at least one document first.")
        except Exception as check_error:
            logger.error(f"Error checking collection: {check_error}")
        
        # Provide helpful error message
        error_msg = str(e)
        if "get_relevant_documents" in error_msg:
            raise ValueError("LangChain version compatibility issue. Please ensure you're using a compatible version of langchain-community.")
        elif "connection" in error_msg.lower() or "qdrant" in error_msg.lower():
            raise ValueError("Cannot connect to Qdrant vector database. Please ensure Qdrant is running.")
        else:
            raise ValueError(f"Failed to retrieve documents: {error_msg}")
    
    if not docs:
        return {
            "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
            "sources": [],
            "source_count": 0
        }
    
    # Build context from retrieved documents
    context_parts = []
    for i, doc in enumerate(docs):
        source_info = doc.metadata.get("source_file", "Unknown")
        page_info = ""
        if "page" in doc.metadata:
            page_info = f" (Page {doc.metadata['page']})"
        elif "slide_number" in doc.metadata:
            page_info = f" (Slide {doc.metadata['slide_number']})"
        
        context_parts.append(f"[Source {i+1}: {source_info}{page_info}]\n{doc.page_content}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Generate answer
    if stream:
        answer_iterator = generate_answer(context, question, stream=True)
        return {
            "answer_stream": answer_iterator,
            "sources": docs,
            "source_count": len(docs)
        }
    else:
        try:
            answer = generate_answer(context, question, stream=False)
            if not answer or answer.strip() == "":
                logger.warning("Generated empty answer, using fallback")
                answer = "I couldn't generate a proper answer. Please try rephrasing your question or check if the documents contain relevant information."
            return {
                "answer": answer,
                "sources": docs,
                "source_count": len(docs)
            }
        except Exception as e:
            logger.error(f"Error generating answer: {e}", exc_info=True)
            # Return error message but still return sources for debugging
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower() or "GOOGLE_API_KEY" in error_msg:
                error_msg = "Google API key error. Please check your .env file."
            elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                error_msg = "API quota exceeded or rate limited. Please try again later."
            elif "client" in error_msg.lower() and "not initialized" in error_msg.lower():
                error_msg = "Google AI client not initialized. Please check GOOGLE_API_KEY in .env file."
            raise ValueError(f"Failed to generate answer: {error_msg}")

