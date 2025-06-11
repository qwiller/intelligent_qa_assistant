from typing import List, Callable

# A simple text splitter function, can be replaced with more sophisticated ones
# from libraries like Langchain or NLTK if needed.

def split_text_by_fixed_size(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Splits text into chunks of a fixed size with a specified overlap.

    Args:
        text: The input text to split.
        chunk_size: The desired size of each chunk (e.g., number of characters).
        chunk_overlap: The number of characters to overlap between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    if not isinstance(text, str) or not text:
        return []
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")
    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")
    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap should be less than chunk size.")

    chunks = []
    start_index = 0
    text_len = len(text)

    while start_index < text_len:
        end_index = min(start_index + chunk_size, text_len)
        chunks.append(text[start_index:end_index])
        
        # Move to the next chunk start position
        # If we are at the end of the text, no need to advance further for overlap
        if end_index == text_len:
            break
        
        start_index += (chunk_size - chunk_overlap)
        
        # Ensure we don't create an empty chunk due to overlap logic at the very end
        if start_index >= text_len and chunks[-1] != text[text_len-chunk_size if text_len-chunk_size > 0 else 0:] :
             # This condition is a bit complex, aims to avoid re-adding the last part if overlap makes it so
             pass # Or handle potential edge cases more gracefully

    # A simpler loop structure might be preferred for clarity, e.g.:
    # for i in range(0, len(text), chunk_size - chunk_overlap):
    #     chunks.append(text[i:i + chunk_size])
    # The above simpler loop might create chunks that are smaller than chunk_size at the end,
    # and the last chunk might be identical to the previous one if overlap is large.
    # The current while loop tries to ensure chunks are mostly of chunk_size.

    return chunks


class TextStructurizer:
    """Handles structuring text into manageable chunks for RAG."""

    def __init__(self, 
                 chunk_size: int = 1000, 
                 chunk_overlap: int = 200, 
                 splitter_fn: Callable[[str, int, int], List[str]] = None):
        """
        Initializes the TextStructurizer.

        Args:
            chunk_size: Default size of text chunks.
            chunk_overlap: Default overlap between chunks.
            splitter_fn: A custom function to split text. If None, uses split_text_by_fixed_size.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter_fn = splitter_fn if splitter_fn else split_text_by_fixed_size

    def structure_text(self, text: str) -> List[str]:
        """
        Splits the given text into structured chunks.

        Args:
            text: The text to be structured.

        Returns:
            A list of text chunks.
        """
        if not text:
            return []
        return self.splitter_fn(text, self.chunk_size, self.chunk_overlap)

# Example Usage:
if __name__ == '__main__':
    sample_long_text = (
        "This is a very long string that needs to be split into smaller chunks. "
        "The splitting should ideally happen at sensible points, but for this basic example, "
        "we will use a fixed-size chunking mechanism. This mechanism will take a chunk size "
        "and an overlap size as parameters. The overlap is important to maintain context "
        "between chunks, which can be crucial for the performance of RAG systems. "
        "Let's imagine this text continues for many more sentences, detailing various aspects "
        "of natural language processing and information retrieval. We need to ensure that "
        "our splitting function handles edge cases correctly, such as when the text is shorter "
        "than the chunk size, or when the overlap is close to the chunk size itself. "
        "Testing with different lengths of text and different parameters is essential. "
        "The goal is to produce a list of strings, where each string is a chunk of the original text."
    ) * 5 # Make the text longer for better demonstration

    structurizer = TextStructurizer(chunk_size=100, chunk_overlap=20)
    chunks = structurizer.structure_text(sample_long_text)

    print(f"Original text length: {len(sample_long_text)}")
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} (length: {len(chunk)}) ---")
        print(chunk)
        if i < len(chunks) -1:
            overlap_part = chunk[-(structurizer.chunk_overlap):]
            next_chunk_start = chunks[i+1][:structurizer.chunk_overlap]
            # This is a simplified check, actual overlap might vary slightly based on word boundaries if using advanced splitters
            # print(f"  Overlap with next (expected {structurizer.chunk_overlap}): '{overlap_part}' vs '{next_chunk_start}'") 
    print("\n")

    # Test with text shorter than chunk_size
    short_text = "This is a short text."
    chunks_short = structurizer.structure_text(short_text)
    print(f"Short text ('{short_text}') chunks:")
    for chunk in chunks_short:
        print(f"- {chunk}")
    print("\n")

    # Test with empty text
    empty_text = ""
    chunks_empty = structurizer.structure_text(empty_text)
    print(f"Empty text chunks: {chunks_empty}")

    # Test with custom splitter (example, not a good one, just for structure)
    def sentence_splitter(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        # This is a very naive sentence splitter, real ones are more complex.
        # Ignores chunk_size and chunk_overlap for this simple example.
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        # A real implementation would then try to group sentences into chunks respecting size/overlap.
        return sentences 

    # structurizer_sentence = TextStructurizer(splitter_fn=sentence_splitter)
    # chunks_sentence = structurizer_sentence.structure_text(sample_long_text)
    # print(f"\nSentence-based chunks (naive): {len(chunks_sentence)}")
    # for i, chunk in enumerate(chunks_sentence):
    #     print(f"--- Sentence Chunk {i+1} ---")
    #     print(chunk)