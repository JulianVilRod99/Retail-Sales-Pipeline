import os
import tarfile
from dotenv import load_dotenv

load_dotenv()


class WebLogProcessor:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.filtered_ip = os.getenv('AIRFLOW_FILTERED_IP', '198.46.149.143')

    def extract_data(self):
        input_path = os.path.join(self.data_dir, "data.txt")
        output_path = os.path.join(self.data_dir, "extracted_data.txt")
        with open(input_path, "r") as infile, open(output_path, "w") as outfile:
            for line in infile:
                ip_address = line.split()[0]
                outfile.write(ip_address + "\n")

    def transform_data(self):
        input_path = os.path.join(self.data_dir, "extracted_data.txt")
        output_path = os.path.join(self.data_dir, "transformed_data.txt")
        with open(input_path, "r") as infile, open(output_path, "w") as outfile:
            for line in infile:
                if line.strip() != self.filtered_ip:
                    outfile.write(line)

    def load_data(self):
        input_file = os.path.join(self.data_dir, "transformed_data.txt")
        output_file = os.path.join(self.data_dir, "weblog.tar")
        with tarfile.open(output_file, "w") as tar:
            tar.add(input_file, arcname="transformed_data.txt")

