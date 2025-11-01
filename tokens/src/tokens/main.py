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
    if str(value).startswith('${') and str(value).endswith('}'):
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
    test_prompt = "Write compelling, structured lyrics about quantum physics, formula one, and indian food. Delineate song sections like this: <verse1>, <chorus> etc with lyrics in between."
    
    print_header(f"Testing {len(models)} models with prompt:")
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
        
        # Start timing
        start_time = time.time()
            
        try:
            # Get environment values
            base_url = get_env_value(model_config['base_url'])
            api_key = get_env_value(model_config['api_key'])
            
            # Initialize crew with specific model
            crew = TokensCrew(
                model_name=model_name,
                model_id=model_id,
                base_url=base_url,
                api_key=api_key
            )
            
            # Run the crew and get the CrewOutput object
            # ❌ Removed the ': CrewOutput' type hint to fix the ModuleNotFoundError
            crew_output = crew.crew().kickoff(inputs={'prompt': test_prompt})
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Extract data directly from the CrewOutput object
            response_text = crew_output.raw
            
            # ✅ FIX: Access attributes directly from the UsageMetrics object
            token_stats = crew_output.token_usage  # This is a UsageMetrics object
            
            token_in = 0
            token_out = 0
            total_tokens = 0

            if token_stats:
                token_in = token_stats.prompt_tokens
                token_out = token_stats.completion_tokens
                total_tokens = token_stats.total_tokens
            
            # Build the report
            report = {
                'model': model_name,
                'model_id': model_id,
                'execution_time_sec': elapsed_time,
                'response': response_text,
                'success': True,
                'error': None,
                'token_in': token_in,
                'token_out': token_out,
                'total_tokens': total_tokens
            }
            results.append(report)
            
            # Print a clean, parsed summary
            print(f"\n{'─'*80}")
            print(f"✓ Completed in {report['execution_time_sec']:.2f}s")
            print(f"  Tokens: In: {report['token_in']} | Out: {report['token_out']} | Total: {report['total_tokens']}")
            print(f"{'─'*80}")
            print(f"Response:\n{report['response']}")
            print(f"{'─'*80}\n")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            
            results.append({
                'model': model_name,
                'model_id': model_id,
                'execution_time_sec': elapsed_time,
                'response': None,
                'success': False,
                'error': str(e),
                'token_in': 'N/A', # Add keys for consistent table
                'token_out': 'N/A',
                'total_tokens': 'N/A'
            })
            
            print(f"\n{'─'*80}")
            print(f"✗ Failed after {elapsed_time:.2f}s")
            print(f"{'─'*80}")
            print(f"Error: {e}")
            print(f"{'─'*80}\n")
    
    # Print summary
    print_header("PERFORMANCE SUMMARY")
    
    # Sort by time (successful models first, then by time)
    results.sort(key=lambda x: (not x['success'], x['execution_time_sec']))
    
    # Print enhanced table header
    print(f"\n{'Model':<35} {'Status':<10} {'Time (s)':<10} {'In':<8} {'Out':<8} {'Total':<8}")
    print(f"{'-'*80}")
    
    # Print results with token stats
    for result in results:
        status = "✓ Success" if result['success'] else "✗ Failed"
        time_val = result.get('execution_time_sec', 0.0)
        token_in = result.get('token_in', 'N/A')
        token_out = result.get('token_out', 'N/A')
        total_tok = result.get('total_tokens', 'N/A')

        print(f"{result['model']:<35} {status:<10} {time_val:>8.2f} {token_in:>8} {token_out:>8} {total_tok:>8}")
    
    # Calculate statistics
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n{'-'*80}")
    print(f"Total Models: {len(results)} | Successful: {len(successful)} | Failed: {len(failed)}")
    
    # Print fastest successful model
    if successful:
        fastest = successful[0]
        slowest = successful[-1]
        avg_time = sum(r['execution_time_sec'] for r in successful) / len(successful)
        
        print(f"\n🏆 Fastest Model: {fastest['model']} ({fastest['execution_time_sec']:.2f}s)")
        print(f"🐌 Slowest Model: {slowest['model']} ({slowest['execution_time_sec']:.2f}s)")
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

