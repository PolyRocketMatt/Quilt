import os

class WorkspaceFile():
    def __init__(self, filepath, type=None):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)

class Workspace():
    def __init__(self, directory):
        self.directory = directory
        self.name = os.path.basename(directory)
        self.workspace_files = []

        self.load_workspace()

    def get_workspace_files(self):
        # Get all PDF files in the directory
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.isfile(filepath):
                    # Create a WorkspaceFile object and add it to the list
                    workspace_file = WorkspaceFile(filepath)
                    self.workspace_files.append(workspace_file)


    def load_workspace(self):
        self.get_workspace_files()

        # Create sidebar
