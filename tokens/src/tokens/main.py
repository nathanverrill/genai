#!/usr/bin/env python
"""
Tokens - Model Performance Comparison Tool
Compares response quality and speed across multiple LLM models
"""

import os
import yaml
import time
from pathlib import Path
from tokens.crew import TokensCrew


def load_models_config():
    """Load models from config/models.yaml relative to project root"""
    # Get the directory this script is in (e.g., src/tokens/)
    script_dir = Path(__file__).resolve().parent

    # Resolve to project root (assumes 2 levels up: src/tokens/ → project root)
    project_root = script_dir.parent.parent

    # Final path to config/models.yaml
    config_path = project_root / 'src/tokens/config' / 'models.yaml'

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config['models']


def get_env_value(value: str) -> str:
    """Replace environment variable placeholders with actual values"""
    if value.startswith('${') and value.endswith('}'):
        env_var = value[2:-1]
        env_value = os.getenv(env_var)
        
        if not env_value:
            raise ValueError(f"Environment variable {env_var} is not set")
        
        return env_value
    
    return value


def print_separator(char='=', length=80):
    """Print a separator line"""
    print(f"\n{char * length}")


def print_header(text, char='='):
    """Print a formatted header"""
    print_separator(char)
    print(text)
    print_separator(char)


def main():
    """Run the crew for each model and compare performance"""
    
    # Load models configuration
    try:
        models = load_models_config()
    except Exception as e:
        print(f"Error loading models configuration: {e}")
        return
    
    # Test prompt - adjust this as needed
    test_prompt = "Explain quantum computing in 2-3 sentences."
    
    print_header(f"Testing {len(models)} models with prompt: {test_prompt}")
    print(f"\nPrompt: \"{test_prompt}\"\n")
    
    results = []
    
    # Test each model
    for idx, model_config in enumerate(models, 1):
        model_name = model_config['name']
        model_id = model_config['model']
        
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(models)}] Testing Model: {model_name}")
        print(f"Model ID: {model_id}")
        print(f"{'='*80}\n")
        
        try:
            # Get environment values
            base_url = get_env_value(model_config['base_url'])
            api_key = get_env_value(model_config['api_key'])
            
            # Start timing
            start_time = time.time()
            
            # Initialize crew with specific model
            crew = TokensCrew(
                model_name=model_name,
                model_id=model_id,
                base_url=base_url,
                api_key=api_key
            )
            
            # Run the crew
            result = crew.crew().kickoff(inputs={'prompt': test_prompt})
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Store results
            results.append({
                'model': model_name,
                'model_id': model_id,
                'time': elapsed_time,
                'response': str(result),
                'success': True,
                'error': None
            })
            
            print(f"\n{'─'*80}")
            print(f"✓ Completed in {elapsed_time:.2f}s")
            print(f"{'─'*80}")
            print(f"Response:\n{result}")
            print(f"{'─'*80}\n")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            
            results.append({
                'model': model_name,
                'model_id': model_id,
                'time': elapsed_time,
                'response': None,
                'success': False,
                'error': str(e)
            })
            
            print(f"\n{'─'*80}")
            print(f"✗ Failed after {elapsed_time:.2f}s")
            print(f"{'─'*80}")
            print(f"Error: {e}")
            print(f"{'─'*80}\n")
    
    # Print summary
    print_header("PERFORMANCE SUMMARY")
    
    # Sort by time (successful models first, then by time)
    results.sort(key=lambda x: (not x['success'], x['time']))
    
    # Print table header
    print(f"\n{'Model':<45} {'Status':<12} {'Time (s)':<10}")
    print(f"{'-'*70}")
    
    # Print results
    for result in results:
        status = "✓ Success" if result['success'] else "✗ Failed"
        print(f"{result['model']:<45} {status:<12} {result['time']:>8.2f}")
    
    # Calculate statistics
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n{'-'*70}")
    print(f"Total Models: {len(results)} | Successful: {len(successful)} | Failed: {len(failed)}")
    
    # Print fastest successful model
    if successful:
        fastest = successful[0]
        slowest = successful[-1]
        avg_time = sum(r['time'] for r in successful) / len(successful)
        
        print(f"\n🏆 Fastest Model: {fastest['model']} ({fastest['time']:.2f}s)")
        print(f"🐌 Slowest Model: {slowest['model']} ({slowest['time']:.2f}s)")
        print(f"📊 Average Time: {avg_time:.2f}s")
    
    # Print failed models with errors
    if failed:
        print(f"\n{'='*80}")
        print("FAILED MODELS")
        print(f"{'='*80}")
        
        for result in failed:
            print(f"\n❌ {result['model']}")
            print(f"   Model ID: {result['model_id']}")
            print(f"   Error: {result['error']}")
    
    print_separator()


# For crewai run compatibility
def run():
    run_safe()


# For manual CLI execution
def run_safe():
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        raise


if __name__ == '__main__':
    run_safe()
