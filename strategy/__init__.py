"""Package definition"""
from os.path import dirname, abspath

from .rsi import rsi_from_json, rsi
from .strategy import Trend

__all__ = ('rsi_from_json', 'rsi', 'Trend', )

ROOT_DIR = dirname(abspath(__file__))
