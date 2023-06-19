import os
from django.conf import settings

def create_file_in_project_root(file_size_kb, file_name):
    """
    file_name =  file name + extension, e.g., large_file.txt
    """
    full_file_path = os.path.join(settings.BASE_DIR,file_name)

    # Calculate the number of bytes needed for the desired file size
    file_size_bytes = file_size_kb * 1024

    # Create a file and write data to it until the desired file size is reached
    with open(full_file_path, 'w') as file:
        while os.path.getsize(full_file_path) < file_size_bytes:
            file.write('test') 
            
    return full_file_path


def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def flush_database():
        from django.db import connections
        for conn in connections.all():
            conn.cursor().execute("SET CONSTRAINTS ALL DEFERRED;")
            conn.cursor().execute("ALTER Sequence jobs_job_id_seq RESTART with 1;")
            conn.cursor().execute("ALTER Sequence jobs_task_task_id_seq RESTART with 1;")
            conn.cursor().execute("TRUNCATE TABLE {};".format(
                ", ".join('"{}"'.format(table) for table in conn.introspection.table_names())
            ))