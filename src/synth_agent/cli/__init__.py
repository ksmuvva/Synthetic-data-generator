"""CLI module for the Synthetic Data Generator."""

# Import the new NLP-based chat interface as default
from synth_agent.cli.nlp_app import app as main

# Legacy command-based app is still available in app.py if needed
__all__ = ["main"]
