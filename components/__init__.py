"""
Components initialization for custom Rasa components.
"""

# Import needed Rasa components
from components.multilingual import UnderthesaTokenizer, process_vietnamese

__all__ = ["UnderthesaTokenizer", "process_vietnamese"]
