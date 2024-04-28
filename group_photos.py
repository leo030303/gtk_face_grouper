import face_recognition
import os
from pathlib import Path
from shutil import copyfile




def process_file(filepath, results_path, encodings):
    current_image = face_recognition.load_image_file(filepath)
    current_face_encodings = face_recognition.face_encodings(current_image)
    if current_face_encodings:
        current_face_encodings = current_face_encodings[0]
    else: return
    action_taken = False
    current_image_cluster_id = None
    for cluster_id, cluster_encodings in encodings.items():
        results = face_recognition.compare_faces(cluster_encodings, current_face_encodings)
        print("results %s %s" % (results, cluster_id))
        if all(results):
            print("cluster_id %s" % cluster_id)
            current_image_cluster_id = cluster_id
            action_taken = True

    if not action_taken:
        current_image_cluster_id = "cluster_%s" % (len(encodings.keys()) + 1)
        print("creating new cluster %s" % current_image_cluster_id)
        encodings[current_image_cluster_id] = [current_face_encodings]
    
    curr_cluster = os.path.join(results_path, current_image_cluster_id)
    curr_cluster_dir = Path(curr_cluster)
    curr_cluster_dir.mkdir(parents=True, exist_ok=True)
    file_name = os.path.basename(filepath)
    copyfile(filepath, os.path.join(curr_cluster_dir, file_name))

def process_folder(folder_path, update_progress):
    curr = 0
    encodings = {}
    results_path = os.path.join(folder_path, 'results')
    for subdir, dirs, files in os.walk(folder_path):
        total = len(files)
        for file in files:
            filepath = os.path.join(subdir, file)
            print("File: %s" % filepath)
            process_file(filepath, results_path, encodings)
            curr += 1
            update_progress(curr/total)
            print("file %s/%s - %s encodings" % (curr, total, len(encodings)))


