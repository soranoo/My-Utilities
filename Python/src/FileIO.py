import json
import os
import tempfile

def find_project_directory() -> str:
    """
    ### Description ###
    Find the directory of the project.
    
    ### Returns ###
        - (str): The directory of the project.
    """
    THIS_DIRECTORY = project_dir = os.path.dirname(__file__)
    if __name__ == "__main__":
        return THIS_DIRECTORY
    import_abs_path = __name__.split(".")[:-1][::-1]
    for folder_name in import_abs_path:
        p_dir = project_dir.split(os.sep)
        if p_dir[-1] == folder_name:
            project_dir = os.path.dirname(project_dir)
        else:
            Warning(f"Cannot find the project directory, the logger will use <{THIS_DIRECTORY}> as the project directory")
            project_dir = THIS_DIRECTORY
            break
    return project_dir

def save_to_json_file(data:dict, file_path:str, append:bool=False):
    """
    ### Description ###
    Saves data to JSON file.
    
    ### Parameters ###
        - `data` (dict): Data to save.
        - `file_path` (str): Path to file. The file must be included file extension.
        - `append` (bool): If True, data will be appended to file. If False, file will be overwritten.
    """
    def _create_folder_if_not_exists(folder_path: str):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
    temp_file_path = os.path.join(find_project_directory(), "temp", next(tempfile._get_candidate_names()))
    
    _create_folder_if_not_exists(os.path.dirname(temp_file_path))
    _create_folder_if_not_exists(os.path.dirname(file_path))
        
    # if the file should be appended, append the data
    # otherwise, overwrite the file with the data
    if append:
        file_data = load_from_json_file(file_path)
        if isinstance(file_data, list):
            file_data.append(data)
        elif isinstance(file_data, dict) and file_data:
            file_data = [file_data, data]
        else:
            file_data = [data]
    else:
        file_data = data
      
    # write the data to the temporary file
    with open(temp_file_path, "w") as outfile:
        json.dump(file_data, outfile) 
    
    # replace the target file with the temporary file
    if os.path.exists(file_path):
        os.remove(file_path)
    os.rename(temp_file_path, file_path)
        
def load_from_json_file(file_path:str) -> dict | list[dict,]:
    """
    ### Description ###
    Loads data from JSON file.
    
    ### Parameters ###
        - `file_path` (str): Path to file. The file must be included file extension.
    
    ### Returns ###
        - (dict | list[dict,]): Data from file.
    """
    # tf the file doesn't exist, return an empty dictionary
    if not os.path.exists(file_path):
        return {}
    
    # load the data from the file as JSON
    with open(file_path, "r") as f:
        return json.load(f)

def get_all_files_in_folder(folder_path:str) -> list[str,]:
    """
    ### Description ###
    Gets all files in folder.
    
    ### Parameters ###
        - `folder_path` (str): Path to folder.
        
    ### Returns ###
        - (list[str,]): List of files in folder (files full path).
    """
    return (
        [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]
        if os.path.exists(folder_path)
        else []
    )