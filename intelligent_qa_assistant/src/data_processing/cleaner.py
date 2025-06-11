import re

class TextCleaner:
    """A class for cleaning text data."""

    def __init__(self, remove_special_chars: bool = True):
        """
        Initializes the TextCleaner.

        Args:
            remove_special_chars (bool): Whether to remove special characters.
        """
        self.remove_special_chars = remove_special_chars

    def clean_text(self, text: str) -> str:
        """Basic text cleaning: lowercase, remove extra whitespace, and optionally remove special characters."""
        text = text.lower()
        text = self.normalize_whitespace(text)

        if self.remove_special_chars:
            # Using double quotes for the raw string to avoid issues with the single quote inside.
            # This regex aims to keep lowercase letters, numbers, whitespace, and basic punctuation (.,?!')
            # It will remove other special characters.
            text = re.sub(r"[^a-z0-9\s.,?!']", '', text)

        return text

    def normalize_whitespace(self, text: str) -> str:
        """Replaces multiple whitespace characters with a single space and trims leading/trailing whitespace."""
        text = re.sub(r'\s+', ' ', text).strip()
        return text

# Example Usage (optional, for testing)
if __name__ == '__main__':
    cleaner_default = TextCleaner()
    cleaner_keep_special = TextCleaner(remove_special_chars=False)

    sample_text_with_special_chars = "  Hello   World! How are you doing today? Is it 2024 yet?! Let's test this... It's great!  "
    sample_text_chinese = "你好，世界！这是一个测试。123？「推荐」“不错”"

    cleaned_text1 = cleaner_default.clean_text(sample_text_with_special_chars)
    print(f"Original: '{sample_text_with_special_chars}'")
    print(f"Cleaned (remove special): '{cleaned_text1}'")

    cleaned_text2 = cleaner_keep_special.clean_text(sample_text_with_special_chars)
    print(f"Cleaned (keep special): '{cleaned_text2}'")

    # Note: The current regex r"[^a-z0-9\s.,?!']" will remove Chinese characters.
    # If you need to support Chinese, the regex needs to be adjusted.
    # For example, to keep Chinese characters, English letters, numbers, and basic English punctuation:
    # cleaner_chinese = TextCleaner()
    # cleaner_chinese.clean_text = lambda t: re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,?!\'']', '', t.lower())
    # cleaned_chinese_text = cleaner_chinese.clean_text(sample_text_chinese)
    # print(f"Original Chinese: '{sample_text_chinese}'")
    # print(f"Cleaned Chinese: '{cleaned_chinese_text}'")

    # A more robust regex for CJK and basic English might be:
    # text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s.,?!'，。？！；：‘“’”《》]", '', text)
    # This would require careful consideration of which punctuation to keep.