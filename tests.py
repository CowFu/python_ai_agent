# tests.py

import unittest
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content

# class TestGetFilesInfo(unittest.TestCase):
#     def test_valid_directory(self):
#         print(get_files_info("calculator", "."))
#         print(get_files_info("calculator", "pkg"))
#         print(get_files_info("calculator", "/bin"))
#         print(get_files_info("calculator", "../"))


# class TestGetFileContent(unittest.TestCase):
# def test_valid_file(self):
# print(get_file_content("calculator", "lorem.txt"))
# print(get_file_content("calculator", "main.py"))
# print(get_file_content("calculator", "pkg/calculator.py"))
# print(get_file_content("calculator", "/bin/cat"))
# print(get_file_content("calculator", "pkg/does_not_exist.py"))


# class TestWriteFile(unittest.TestCase):
#     def test_write_file(self):
#         from functions.write_file import write_file
#         print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
#         print(write_file("calculator", "pkg/morelorem.txt",
#                    "lorem ipsum dolor sit amet"))
#         print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))

class TestRunPythonFile(unittest.TestCase):
    def test_run_python_file(self):
        from functions.run_python_file import run_python_file
        print("========= main.py ==========")
        print(run_python_file("calculator", "main.py"))
        print("========= main.py ==========")
        print(run_python_file("calculator", "main.py", ["3 + 5"]))
        print("========= tests.py ==========")
        print(run_python_file("calculator", "tests.py"))
        print("========= ../main.py ==========")
        print(run_python_file("calculator", "../main.py"))
        print("========= nonexistent.py ==========")
        print(run_python_file("calculator", "nonexistent.py"))


if __name__ == "__main__":
    unittest.main()
