import os
import yaml

from pathlib import Path
from typing import Optional

class QuiltWorkspace():
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir

        # Find .quilt file
        quilt_file = os.path.join(self.workspace_dir, '.quilt')
        if not os.path.exists(quilt_file):
            raise FileNotFoundError(f"No .quilt file found in {self.workspace_dir}")
        
        with open(quilt_file, 'r') as file:
            # Assuming the .quilt file is in YAML format
            try:
                self.workspace_data = yaml.safe_load(file)
                self.workspace_name = self.workspace_data.get('name', 'Untitled Workspace')

                # Load files
                markdown_entries = list(Path(self.workspace_dir).rglob('**/*.md'))
                pdf_entries = list(Path(self.workspace_dir).rglob('**/*.pdf'))
                image_entries = list(Path(self.workspace_dir).rglob('**/*.{png,jpg,jpeg,gif}'))

                self.markdown_metadata = self.extract_file_metadata(markdown_entries)
                self.pdf_metadata = self.extract_file_metadata(pdf_entries)
                self.image_metadata = self.extract_file_metadata(image_entries)
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing .quilt file: {e}")
            

    def extract_file_metadata(self, files):
        metadata = {}
        for file in files:
            # Generate unique identifier for the file
            file_id = os.path.relpath(file, self.workspace_dir)
            metadata[file_id] = {
                'name': os.path.basename(file),
                'path': file,
                'size': os.path.getsize(file),
                'last_modified': os.path.getmtime(file)
            }

        return metadata
    
    def find_pdf_from_name(self, file_id: str) -> Optional[dict]:
        """Find PDF metadata by file name."""

        for pdf_id, pdf_data in self.pdf_metadata.items():
            if pdf_data['name'] == file_id:
                return pdf_data
        return None