"""
DarkBench loader for PFMD experiments.
Loads DarkBench queries and converts them to Scenario format for multi-turn experiments.
"""
import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests

from src.scenarios import Scenario


@dataclass
class DarkBenchQuery:
    """Represents a DarkBench query."""
    query_id: str
    query: str
    category: Optional[str] = None
    dark_pattern: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DarkBenchLoader:
    """Loads and processes DarkBench queries."""
    
    def __init__(self, darkbench_path: Optional[str] = None):
        """
        Initialize DarkBench loader.
        
        Args:
            darkbench_path: Path to DarkBench dataset file or directory
        """
        self.darkbench_path = darkbench_path
        self.queries: List[DarkBenchQuery] = []
    
    def load_from_file(self, filepath: str) -> List[DarkBenchQuery]:
        """
        Load DarkBench queries from a file.
        
        Supports:
        - JSON files (list of queries or dict with queries key)
        - CSV files
        - JSONL files (one JSON object per line)
        
        Args:
            filepath: Path to DarkBench file
        
        Returns:
            List of DarkBenchQuery objects
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"DarkBench file not found: {filepath}")
        
        queries = []
        
        if filepath.suffix == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                queries_data = data
            elif isinstance(data, dict):
                # Try common keys
                queries_data = data.get('queries', data.get('data', data.get('items', [])))
            else:
                raise ValueError(f"Unexpected JSON structure in {filepath}")
            
            for item in queries_data:
                query = self._parse_query_item(item)
                if query:
                    queries.append(query)
        
        elif filepath.suffix == '.jsonl':
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        query = self._parse_query_item(item)
                        if query:
                            queries.append(query)
        
        elif filepath.suffix == '.csv':
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    query = self._parse_query_item(row)
                    if query:
                        queries.append(query)
        
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")
        
        self.queries = queries
        return queries
    
    def _parse_query_item(self, item: Dict[str, Any]) -> Optional[DarkBenchQuery]:
        """Parse a single query item from various formats."""
        # Try different possible field names
        query_text = (
            item.get('query') or 
            item.get('text') or 
            item.get('prompt') or 
            item.get('input') or
            item.get('question') or
            item.get('message')
        )
        
        if not query_text:
            return None
        
        query_id = (
            item.get('id') or 
            item.get('query_id') or 
            item.get('_id') or
            str(hash(query_text))  # Fallback to hash
        )
        
        category = item.get('category') or item.get('type') or item.get('class')
        dark_pattern = item.get('dark_pattern') or item.get('pattern') or item.get('dark_design_pattern')
        
        metadata = {k: v for k, v in item.items() 
                   if k not in ['query', 'text', 'prompt', 'input', 'question', 'message',
                               'id', 'query_id', '_id', 'category', 'type', 'class',
                               'dark_pattern', 'pattern', 'dark_design_pattern']}
        
        return DarkBenchQuery(
            query_id=str(query_id),
            query=str(query_text),
            category=category,
            dark_pattern=dark_pattern,
            metadata=metadata if metadata else None
        )
    
    def load_from_url(self, url: str) -> List[DarkBenchQuery]:
        """
        Load DarkBench queries from a URL.
        
        Args:
            url: URL to DarkBench dataset (JSON/JSONL)
        
        Returns:
            List of DarkBenchQuery objects
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Try JSON first
            try:
                data = response.json()
                # Save to temp file and use load_from_file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(data, f)
                    temp_path = f.name
                
                queries = self.load_from_file(temp_path)
                os.unlink(temp_path)
                return queries
            except:
                # Try JSONL
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
                    f.write(response.text)
                    temp_path = f.name
                
                queries = self.load_from_file(temp_path)
                os.unlink(temp_path)
                return queries
        
        except Exception as e:
            raise ValueError(f"Failed to load DarkBench from URL {url}: {e}")
    
    def load_from_directory(self, directory: str) -> List[DarkBenchQuery]:
        """
        Load DarkBench queries from a directory (searches for JSON/JSONL/CSV files).
        
        Args:
            directory: Directory containing DarkBench files
        
        Returns:
            List of DarkBenchQuery objects
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        queries = []
        for ext in ['.json', '.jsonl', '.csv']:
            for filepath in directory.glob(f'*{ext}'):
                try:
                    file_queries = self.load_from_file(str(filepath))
                    queries.extend(file_queries)
                except Exception as e:
                    print(f"Warning: Failed to load {filepath}: {e}")
        
        self.queries = queries
        return queries
    
    def to_scenarios(
        self,
        max_queries: Optional[int] = None,
        category_filter: Optional[str] = None,
        dark_pattern_filter: Optional[str] = None
    ) -> Dict[str, Scenario]:
        """
        Convert DarkBench queries to Scenario objects.
        
        Args:
            max_queries: Maximum number of queries to convert (None = all)
            category_filter: Filter by category (None = all)
            dark_pattern_filter: Filter by dark pattern (None = all)
        
        Returns:
            Dictionary of scenario_name -> Scenario
        """
        if not self.queries:
            raise ValueError("No queries loaded. Call load_from_file/url/directory first.")
        
        # Filter queries
        filtered_queries = self.queries
        if category_filter:
            filtered_queries = [q for q in filtered_queries if q.category == category_filter]
        if dark_pattern_filter:
            filtered_queries = [q for q in filtered_queries if q.dark_pattern == dark_pattern_filter]
        if max_queries:
            filtered_queries = filtered_queries[:max_queries]
        
        scenarios = {}
        for query in filtered_queries:
            # Generate scenario name
            scenario_name = f"darkbench_{query.query_id}"
            
            # Extract manipulation opportunities from dark pattern
            manipulation_opportunities = []
            if query.dark_pattern:
                # Map common dark patterns to our manipulation tactics
                pattern_mapping = {
                    'urgency': ['false_urgency', 'commitment_escalation'],
                    'scarcity': ['false_urgency'],
                    'social_proof': ['sycophancy', 'fabrication'],
                    'authority': ['false_authority', 'authority_inflation'],
                    'reciprocity': ['dependency', 'commitment_escalation'],
                    'commitment': ['commitment_escalation'],
                    'consistency': ['commitment_escalation'],
                    'liking': ['sycophancy', 'emotional_manipulation'],
                    'anchoring': ['fabrication'],
                    'framing': ['fabrication', 'emotional_manipulation'],
                }
                
                pattern_lower = query.dark_pattern.lower()
                for key, tactics in pattern_mapping.items():
                    if key in pattern_lower:
                        manipulation_opportunities.extend(tactics)
                
                if not manipulation_opportunities:
                    manipulation_opportunities = ['fabrication', 'commitment_escalation']  # Default
            else:
                manipulation_opportunities = ['fabrication', 'commitment_escalation']  # Default
            
            # Create scenario
            scenario = Scenario(
                name=f"DarkBench: {query.query_id}",
                setup=query.query,
                manipulation_opportunities=list(set(manipulation_opportunities)),  # Remove duplicates
                description=f"DarkBench query (Category: {query.category or 'unknown'}, Pattern: {query.dark_pattern or 'unknown'})"
            )
            
            scenarios[scenario_name] = scenario
        
        return scenarios


def load_darkbench_scenarios(
    source: str,
    max_queries: Optional[int] = None,
    category_filter: Optional[str] = None,
    dark_pattern_filter: Optional[str] = None
) -> Dict[str, Scenario]:
    """
    Convenience function to load DarkBench and convert to scenarios.
    
    Args:
        source: Path to file/directory or URL
        max_queries: Maximum number of queries (None = all)
        category_filter: Filter by category
        dark_pattern_filter: Filter by dark pattern
    
    Returns:
        Dictionary of scenario_name -> Scenario
    """
    loader = DarkBenchLoader()
    
    # Determine source type
    if source.startswith('http://') or source.startswith('https://'):
        loader.load_from_url(source)
    elif os.path.isdir(source):
        loader.load_from_directory(source)
    elif os.path.isfile(source):
        loader.load_from_file(source)
    else:
        raise ValueError(f"Invalid source: {source}. Must be file path, directory, or URL.")
    
    return loader.to_scenarios(
        max_queries=max_queries,
        category_filter=category_filter,
        dark_pattern_filter=dark_pattern_filter
    )

