import os
from datetime import datetime
from typing import Optional, List


def save_analysis_report(
    report_content: str,
    output_dir: str = "outputs",
    filename: str = "legal_analysis.txt",
    save_timestamped_copy: bool = True
) -> str:
    """
    Part E - Q6: Saves the generated legal analysis or summary to a file.
    Default destination: outputs/legal_analysis.txt
    """
    os.makedirs(output_dir, exist_ok=True)
    
    primary_path = os.path.join(output_dir, filename)
    with open(primary_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    # Also save a timestamped copy so multiple analyses are preserved
    if save_timestamped_copy:
        base_name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_filename = f"{base_name}_{timestamp}{ext}"
        timestamped_path = os.path.join(output_dir, timestamped_filename)
        with open(timestamped_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
    return primary_path


def list_saved_reports(output_dir: str = "outputs") -> List[str]:
    """Lists all saved report files in outputs directory."""
    if not os.path.exists(output_dir):
        return []
    return [
        f for f in os.listdir(output_dir)
        if f.endswith(".txt") or f.endswith(".md")
    ]


def read_saved_report(file_path: str) -> str:
    """Reads a previously saved report file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Report not found at {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
