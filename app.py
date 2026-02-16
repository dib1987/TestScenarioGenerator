"""
PR Test Scenario Generator - Web Application
A web interface for generating test scenarios from pull requests.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import traceback
import markdown
from datetime import datetime

from src.git_analyzer import GitHubPRAnalyzer, GitAnalyzer
from src.code_analyzer import CodeAnalyzer
from src.test_generator import TestScenarioGenerator

# Load environment variables
# Get the directory of this file
import pathlib
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure app
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/analyze-pr', methods=['POST'])
def analyze_pr():
    """
    API endpoint to analyze a pull request and generate test scenarios.

    Expected JSON payload:
    {
        "pr_url": "https://github.com/owner/repo/pull/123",
        "generate_code": false  # optional
    }
    """
    try:
        data = request.get_json()

        if not data or 'pr_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing PR URL'
            }), 400

        pr_url = data['pr_url'].strip()
        generate_code = data.get('generate_code', False)

        # Parse the GitHub PR URL
        if 'github.com' not in pr_url:
            return jsonify({
                'success': False,
                'error': 'Invalid GitHub PR URL. Must contain github.com'
            }), 400

        parts = pr_url.split('/')
        if len(parts) < 7:
            return jsonify({
                'success': False,
                'error': 'Invalid GitHub PR URL format'
            }), 400

        owner = parts[-4]
        repo = parts[-3]

        try:
            pr_number = int(parts[-1])
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid PR number'
            }), 400

        # Step 1: Fetch PR data from GitHub
        github_token = os.getenv('GITHUB_TOKEN')
        gh_analyzer = GitHubPRAnalyzer(github_token)

        try:
            diff_text = gh_analyzer.get_pr_diff(owner, repo, pr_number)
            pr_info = gh_analyzer.get_pr_info(owner, repo, pr_number)
        except Exception as e:
            error_msg = str(e)
            if '401' in error_msg:
                return jsonify({
                    'success': False,
                    'error': 'GitHub authentication failed. Please add GITHUB_TOKEN to .env file'
                }), 401
            elif '404' in error_msg:
                return jsonify({
                    'success': False,
                    'error': 'PR not found. Check the URL and make sure the repository is accessible'
                }), 404
            else:
                return jsonify({
                    'success': False,
                    'error': f'GitHub API error: {error_msg}'
                }), 500

        # Step 2: Analyze the code changes
        code_analyzer = CodeAnalyzer()
        parsed_diff = code_analyzer.parse_diff(diff_text)
        change_types = code_analyzer.identify_change_types(parsed_diff)
        diff_summary = code_analyzer.generate_summary(parsed_diff)

        # Step 3: Generate test scenarios with Claude AI
        try:
            test_generator = TestScenarioGenerator()
            test_scenarios = test_generator.generate_test_scenarios(
                diff_summary=diff_summary,
                parsed_diff=parsed_diff,
                change_types=change_types,
                pr_context=pr_info
            )
        except Exception as e:
            error_msg = str(e)
            if 'credit balance' in error_msg.lower():
                return jsonify({
                    'success': False,
                    'error': 'Anthropic API credits exhausted. Please add credits at console.anthropic.com'
                }), 402
            elif 'invalid_request_error' in error_msg:
                return jsonify({
                    'success': False,
                    'error': 'Invalid API request. Check your Anthropic API key'
                }), 401
            else:
                return jsonify({
                    'success': False,
                    'error': f'AI generation error: {error_msg}'
                }), 500

        # Step 4: Optionally generate test code
        test_code = None
        if generate_code:
            try:
                test_code = test_generator.generate_automated_test_code(
                    test_scenarios=test_scenarios,
                    language="python",
                    framework="pytest"
                )
            except Exception as e:
                # Don't fail the whole request if code generation fails
                test_code = f"Error generating test code: {str(e)}"

        # Step 5: Prepare file-by-file analysis
        file_analyses = []
        for file_change in parsed_diff[:10]:  # Limit to 10 files for UI
            file_analyses.append({
                'file_path': file_change['file_path'],
                'additions': len(file_change['additions']),
                'deletions': len(file_change['deletions']),
                'has_additions': len(file_change['additions']) > 0,
                'has_deletions': len(file_change['deletions']) > 0
            })

        # Step 6: Convert markdown to HTML for better display
        test_scenarios_html = markdown.markdown(
            test_scenarios,
            extensions=['fenced_code', 'tables', 'nl2br']
        )

        # Return success response
        return jsonify({
            'success': True,
            'data': {
                'pr_info': {
                    'title': pr_info['title'],
                    'author': pr_info['author'],
                    'base_branch': pr_info['base_branch'],
                    'head_branch': pr_info['head_branch'],
                    'state': pr_info['state']
                },
                'summary': {
                    'total_files': len(parsed_diff),
                    'total_additions': sum(len(f['additions']) for f in parsed_diff),
                    'total_deletions': sum(len(f['deletions']) for f in parsed_diff)
                },
                'file_analyses': file_analyses,
                'change_types': change_types,
                'test_scenarios': test_scenarios,
                'test_scenarios_html': test_scenarios_html,
                'test_code': test_code,
                'generated_at': datetime.now().isoformat()
            }
        })

    except Exception as e:
        # Catch-all error handler
        app.logger.error(f"Unexpected error: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500


@app.route('/api/analyze-diff', methods=['POST'])
def analyze_diff():
    """
    API endpoint to analyze a manual git diff.

    Expected JSON payload:
    {
        "diff_text": "git diff content...",
        "generate_code": false  # optional
    }
    """
    try:
        data = request.get_json()

        if not data or 'diff_text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing diff text'
            }), 400

        diff_text = data['diff_text'].strip()
        generate_code = data.get('generate_code', False)

        if not diff_text:
            return jsonify({
                'success': False,
                'error': 'Diff text is empty'
            }), 400

        # Analyze the code changes
        code_analyzer = CodeAnalyzer()
        parsed_diff = code_analyzer.parse_diff(diff_text)
        change_types = code_analyzer.identify_change_types(parsed_diff)
        diff_summary = code_analyzer.generate_summary(parsed_diff)

        # Generate test scenarios
        test_generator = TestScenarioGenerator()
        test_scenarios = test_generator.generate_test_scenarios(
            diff_summary=diff_summary,
            parsed_diff=parsed_diff,
            change_types=change_types,
            pr_context=None
        )

        # Optionally generate test code
        test_code = None
        if generate_code:
            test_code = test_generator.generate_automated_test_code(
                test_scenarios=test_scenarios,
                language="python",
                framework="pytest"
            )

        # Prepare response
        file_analyses = []
        for file_change in parsed_diff[:10]:
            file_analyses.append({
                'file_path': file_change['file_path'],
                'additions': len(file_change['additions']),
                'deletions': len(file_change['deletions'])
            })

        test_scenarios_html = markdown.markdown(
            test_scenarios,
            extensions=['fenced_code', 'tables', 'nl2br']
        )

        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'total_files': len(parsed_diff),
                    'total_additions': sum(len(f['additions']) for f in parsed_diff),
                    'total_deletions': sum(len(f['deletions']) for f in parsed_diff)
                },
                'file_analyses': file_analyses,
                'change_types': change_types,
                'test_scenarios': test_scenarios,
                'test_scenarios_html': test_scenarios_html,
                'test_code': test_code,
                'generated_at': datetime.now().isoformat()
            }
        })

    except Exception as e:
        app.logger.error(f"Error: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print("=" * 70)
    print("PR Test Scenario Generator - Web Application")
    print("=" * 70)
    print(f"\nServer starting on http://localhost:{port}")
    print("\nOpen your browser and navigate to the URL above")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)

    app.run(host='0.0.0.0', port=port, debug=debug)
