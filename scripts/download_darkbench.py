"""
Download DarkBench dataset from Hugging Face and convert to JSON format.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from pathlib import Path

try:
    from datasets import load_dataset
    USE_DATASETS = True
except ImportError:
    USE_DATASETS = False
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
        USE_HF_HUB = True
    except ImportError:
        USE_HF_HUB = False
        print("Warning: Neither 'datasets' nor 'huggingface_hub' available. Install one of them.")


def download_darkbench(output_path: str = "data/darkbench/darkbench.json"):
    """
    Download DarkBench dataset from Hugging Face.
    
    Args:
        output_path: Path to save the converted JSON file
    """
    print("Downloading DarkBench dataset from Hugging Face...")
    print("Dataset: anonymous152311/darkbench")
    print()
    
    try:
        data = None
        
        if USE_DATASETS:
            # Load dataset from Hugging Face using datasets library
            print("Loading dataset using 'datasets' library...")
            dataset = load_dataset("anonymous152311/darkbench")
            
            # Check what splits are available
            print(f"Available splits: {list(dataset.keys())}")
            
            # Use 'test' or 'default' split, or first available
            split_name = None
            for possible_split in ['test', 'train', 'validation', 'default']:
                if possible_split in dataset:
                    split_name = possible_split
                    break
            
            if split_name is None:
                split_name = list(dataset.keys())[0]
            
            print(f"Using split: {split_name}")
            data = dataset[split_name]
            
        elif USE_HF_HUB:
            # Try to download raw files directly
            print("Loading dataset using 'huggingface_hub' library...")
            from huggingface_hub import hf_hub_download, list_repo_files
            
            repo_id = "anonymous152311/darkbench"
            # Try as dataset first
            try:
                files = list_repo_files(repo_id, repo_type="dataset")
                repo_type = "dataset"
            except:
                # Try as model
                try:
                    files = list_repo_files(repo_id, repo_type="model")
                    repo_type = "model"
                except:
                    # Try without specifying (defaults to model)
                    files = list_repo_files(repo_id)
                    repo_type = "model"
            
            print(f"Available files: {files}")
            
            # Try to find data files (JSON, JSONL, TSV, CSV)
            data_files = [f for f in files if f.endswith(('.json', '.jsonl', '.tsv', '.csv')) and not f.endswith('README.md')]
            if data_files:
                print(f"Downloading: {data_files[0]}")
                local_file = hf_hub_download(repo_id=repo_id, filename=data_files[0], repo_type=repo_type)
                
                # Load the file based on extension
                if local_file.endswith('.jsonl'):
                    data_list = []
                    with open(local_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                data_list.append(json.loads(line))
                    data = data_list
                elif local_file.endswith('.json'):
                    with open(local_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        # Try to find the actual data
                        data = data.get('data', data.get('queries', list(data.values())[0] if data else []))
                elif local_file.endswith(('.tsv', '.csv')):
                    # Load TSV/CSV
                    import csv
                    delimiter = '\t' if local_file.endswith('.tsv') else ','
                    data_list = []
                    with open(local_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f, delimiter=delimiter)
                        for row in reader:
                            data_list.append(row)
                    data = data_list
            else:
                raise ValueError("No data files (JSON/JSONL/TSV/CSV) found in repository")
        
        else:
            raise ImportError("Please install either 'datasets' or 'huggingface_hub': pip install datasets huggingface_hub")
        
        if data is None:
            raise ValueError("Failed to load data")
        
        # Convert list if needed
        if not isinstance(data, list):
            if hasattr(data, '__iter__') and not isinstance(data, (str, dict)):
                data = list(data)
            elif isinstance(data, dict):
                data = [data]
            else:
                raise ValueError(f"Unexpected data type: {type(data)}")
        
        print(f"Loaded {len(data)} queries")
        print()
        
        # Inspect structure
        if len(data) > 0:
            print("Sample query structure:")
            sample = data[0] if isinstance(data[0], dict) else dict(data[0])
            for key in list(sample.keys())[:10]:
                val = sample[key]
                print(f"  {key}: {str(val)[:100]}...")
            print()
        
        # Convert to JSON format
        print("Converting to JSON format...")
        queries = []
        
        for i, item in enumerate(data):
            # Handle both dict and object types
            if not isinstance(item, dict):
                if hasattr(item, '__dict__'):
                    item = item.__dict__
                else:
                    item = dict(item)
            # Extract query text (try different field names)
            # DarkBench TSV has "Example" as the actual query
            query_text = (
                item.get('Example') or  # DarkBench format (capital E)
                item.get('example') or  # lowercase
                item.get('query') or 
                item.get('text') or 
                item.get('prompt') or 
                item.get('input') or
                item.get('question') or
                item.get('message') or
                item.get('instruction') or
                str(item)  # Fallback
            )
            
            # Extract other fields
            query_id = (
                item.get('id') or 
                item.get('query_id') or 
                item.get('_id') or
                f"db_{i+1:04d}"
            )
            
            # DarkBench uses "Deceptive Pattern" field (capital D, capital P)
            dark_pattern = (
                item.get('Deceptive Pattern') or  # DarkBench format
                item.get('deceptive_pattern') or
                item.get('dark_pattern') or 
                item.get('pattern') or 
                item.get('dark_design_pattern')
            )
            
            category = (
                item.get('category') or 
                item.get('type') or 
                item.get('class') or
                dark_pattern  # Use dark pattern as category if no category
            )
            
            # Include all other fields as metadata
            metadata = {k: v for k, v in item.items() 
                       if k not in ['query', 'text', 'prompt', 'input', 'question', 'message', 'instruction',
                                   'id', 'query_id', '_id', 'category', 'type', 'class',
                                   'dark_pattern', 'pattern', 'dark_design_pattern',
                                   'Example', 'example', 'Deceptive Pattern', 'deceptive_pattern']}
            
            query_obj = {
                "id": str(query_id),
                "query": str(query_text),
            }
            
            if category:
                query_obj["category"] = str(category)
            if dark_pattern:
                query_obj["dark_pattern"] = str(dark_pattern)
            if metadata:
                query_obj["metadata"] = metadata
            
            queries.append(query_obj)
        
        # Save to JSON file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(queries, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(queries)} queries to: {output_path}")
        print()
        
        # Show statistics
        print("Dataset Statistics:")
        print(f"  Total queries: {len(queries)}")
        
        # Count by category
        categories = {}
        dark_patterns = {}
        for q in queries:
            cat = q.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            pattern = q.get('dark_pattern', 'unknown')
            dark_patterns[pattern] = dark_patterns.get(pattern, 0) + 1
        
        if len(categories) > 1:
            print(f"  Categories: {len(categories)}")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"    {cat}: {count}")
        
        if len(dark_patterns) > 1:
            print(f"  Dark Patterns: {len(dark_patterns)}")
            for pattern, count in sorted(dark_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"    {pattern}: {count}")
        
        print()
        print("✓ DarkBench dataset ready!")
        print(f"\nYou can now run experiments with:")
        print(f"  python experiments/run_darkbench_experiment.py --source {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"✗ Error downloading DarkBench: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download DarkBench dataset from Hugging Face")
    parser.add_argument(
        "--output",
        type=str,
        default="data/darkbench/darkbench.json",
        help="Output path for JSON file (default: data/darkbench/darkbench.json)"
    )
    
    args = parser.parse_args()
    
    download_darkbench(args.output)

