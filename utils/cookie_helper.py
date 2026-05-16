import os
import logging

logger = logging.getLogger(__name__)

def clean_cookies(file_path: str):
    """
    Cleans the cookies file to keep only YouTube and related domains.
    This helps in reducing the size and improving stability.
    """
    if not os.path.exists(file_path):
        return

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # YouTube related domains
        valid_domains = [
            ".youtube.com",
            "www.youtube.com",
            "youtube.com",
            ".google.com",
            "www.google.com",
            "google.com"
        ]

        cleaned_lines = []
        for line in lines:
            if line.startswith('#') or not line.strip():
                cleaned_lines.append(line)
                continue

            parts = line.split('\t')
            if len(parts) >= 1:
                domain = parts[0]
                if any(domain.endswith(vd) for vd in valid_domains):
                    cleaned_lines.append(line)

        with open(file_path, 'w') as f:
            f.writelines(cleaned_lines)

        logger.info(f"Cleaned cookies file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning cookies: {e}")

if __name__ == "__main__":
    clean_cookies("cookies.txt")
