import os
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# === CONFIGURATION ===
# Root folder that contains Git repositories (Windows path)
GITHUB_REPOS_ROOT = r"C:\Users\demet\OneDrive\Documents\GitHub\github_repo_importer\projects"

SOURCE_EXTENSIONS = {'.py', '.cpp', '.c', '.java', '.asm', '.ipynb', '.js', '.ts', '.rs'}
EXCLUDE_DIRS = {'docs', 'textbooks', 'slides', '__pycache__', '.git'}
MAX_LINES_PER_FILE = 20
MAX_TOTAL_SNIPPETS_PER_PROJECT = 10

# Each repository will get its own JSON summary under this directory
OUTPUT_DIR = 'project_summaries_jsons'


def setup_logging(level: str = 'INFO', log_file: str | None = None) -> None:
    """Configure root logger with console and optional file handler."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                                                    '%Y-%m-%d %H:%M:%S'))
        logging.getLogger().addHandler(file_handler)
    logging.getLogger(__name__).debug('Logging initialised (level=%s, log_file=%s)', level.upper(), log_file)


def is_source_file(filename: str) -> bool:
    """Return True if *filename* has one of the allowed source extensions."""
    return any(filename.endswith(ext) for ext in SOURCE_EXTENSIONS)


def gather_code_snippets(project_path: str, logger: logging.Logger):
    """Collect up to MAX_TOTAL_SNIPPETS_PER_PROJECT snippets from source files in *project_path*."""
    logger.debug('Scanning project path: %s', project_path)
    snippets = []
    count = 0
    for root, _, files in os.walk(project_path):
        for file in files:
            if is_source_file(file):
                filepath = os.path.join(root, file)
                logger.debug('Reading file: %s', filepath)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[:MAX_LINES_PER_FILE]
                    if lines:
                        relative_path = os.path.relpath(filepath, GITHUB_REPOS_ROOT)
                        snippets.append({
                            'file': relative_path,
                            'snippet': ''.join(lines).strip()
                        })
                        count += 1
                        logger.debug('Added snippet from %s (%d/%d)', relative_path,
                                     count, MAX_TOTAL_SNIPPETS_PER_PROJECT)
                        if count >= MAX_TOTAL_SNIPPETS_PER_PROJECT:
                            logger.info('Reached snippet limit for project %s', project_path)
                            return snippets
                except Exception as exc:
                    logger.exception('Error processing file %s: %s', filepath, exc)
    return snippets


def process_repos(root_folder: str, logger: logging.Logger):
    """Walk through *root_folder* and return a mapping {repo_name: [project_summaries]}"""
    logger.info('Starting repository scan in %s', root_folder)
    repo_summaries: dict[str, list] = {}

    # First‑level iteration: each directory directly under root is treated as a repo
    for repo_name in os.listdir(root_folder):
        repo_path = os.path.join(root_folder, repo_name)
        if not os.path.isdir(repo_path):
            logger.debug('Skipping non-directory entry: %s', repo_path)
            continue

        logger.debug('Processing repository: %s', repo_name)
        summaries_for_repo: list[dict] = []
        for root, dirs, files in os.walk(repo_path):
            # Skip excluded sub‑directories in‑place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            relevant_files = [f for f in files if is_source_file(f)]
            if relevant_files:
                rel_path = os.path.relpath(root, repo_path)
                full_project_path = os.path.join(repo_path, rel_path)
                logger.debug('Found project folder with source files: %s', full_project_path)
                snippets = gather_code_snippets(full_project_path, logger)
                if snippets:
                    project_summary = {
                        'repo': repo_name,
                        'folder': rel_path,
                        'code_files': [os.path.join(rel_path, f) for f in relevant_files],
                        'snippets': snippets
                    }
                    summaries_for_repo.append(project_summary)
                    logger.info('Added summary for project %s/%s (snippets=%d)',
                                repo_name, rel_path, len(snippets))
        if summaries_for_repo:
            repo_summaries[repo_name] = summaries_for_repo
            logger.info('Finished repository %s: %d project folder(s)', repo_name, len(summaries_for_repo))
        else:
            logger.info('No relevant source files found in repository %s', repo_name)

    logger.info('Repository scan completed. Total repositories summarised: %d', len(repo_summaries))
    return repo_summaries


def write_repo_json(repo_name: str, summaries: list[dict], out_dir: Path, logger: logging.Logger) -> None:
    """Write the *summaries* list to <out_dir>/<repo_name>.json"""
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{repo_name}.json"
    with open(file_path, 'w', encoding='utf-8') as fp:
        json.dump(summaries, fp, indent=2)
    logger.info('🔸 Wrote %d project summary(ies) to %s', len(summaries), file_path)


def main() -> None:
    # Configure logging
    setup_logging(level=os.getenv('LOG_LEVEL', 'INFO'),
                  log_file=os.getenv('LOG_FILE'))
    logger = logging.getLogger(__name__)

    try:
        logger.info('===== Project summarisation started =====')

        repo_summaries = process_repos(GITHUB_REPOS_ROOT, logger)
        output_path = Path(OUTPUT_DIR)
        for repo_name, summaries in repo_summaries.items():
            write_repo_json(repo_name, summaries, output_path, logger)

        logger.info('===== Project summarisation finished (repositories written: %d) =====',
                    len(repo_summaries))

    except Exception as exc:
        logger.exception('Unhandled exception: %s', exc)
        raise


if __name__ == '__main__':
    main()
