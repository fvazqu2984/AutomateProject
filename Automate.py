import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit,
    QFileDialog, QMessageBox, QInputDialog
)
import subprocess
from openai import OpenAI

class CodeAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = None
        self.client = None
        self.initUI()
        self.get_api_key()

    def initUI(self):
        self.setWindowTitle('Code Analyzer and Optimizer')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.openButton = QPushButton('Open C/C++ Source File')
        self.openButton.clicked.connect(self.openFileDialog)
        layout.addWidget(self.openButton)

        self.sourceLabel = QLabel('Source Code:')
        layout.addWidget(self.sourceLabel)

        self.sourceText = QTextEdit()
        self.sourceText.setReadOnly(True)
        layout.addWidget(self.sourceText)

        self.analyzeButton = QPushButton('Analyze and Optimize')
        self.analyzeButton.clicked.connect(self.analyzeAndOptimize)
        layout.addWidget(self.analyzeButton)

        self.resultLabel = QLabel('Results:')
        layout.addWidget(self.resultLabel)

        self.resultText = QTextEdit()
        self.resultText.setReadOnly(True)
        layout.addWidget(self.resultText)

        self.setLayout(layout)

    def get_api_key(self):

        # If not set, prompt the user to enter their API key
        if not self.api_key:
            self.api_key, ok = QInputDialog.getText(self, 'OpenAI API Key', 'Enter your OpenAI API key:')
            if not ok or not self.api_key:
                QMessageBox.critical(self, "Error", "OpenAI API key is required to run the application.")
                sys.exit(1)

        # Initialize OpenAI client with the provided API key
        self.client = OpenAI(api_key=self.api_key)

    def openFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open C/C++ Source File", "", "C/C++ Files (*.c *.cpp)", options=options)
        if fileName:
            with open(fileName, 'r') as file:
                self.sourceText.setPlainText(file.read())
            self.sourceFile = fileName

    def analyzeAndOptimize(self):
        try:
            #Paths for temporary files
            clang_output_file = 'clang_output.txt'
            asan_output_file = 'asan_output.txt'
            fixed_code_file = 'fixed_memory_safety_code.c'
            optimized_code_file = 'optimized_code.c'
            final_summary_file = 'final_summary.txt'
            executable_file = 'a.out'

            #Reads source code
            source_code = self.sourceText.toPlainText()

            #Determines if the file is C or C++ based on the extension
            file_extension = os.path.splitext(self.sourceFile)[1]

            if file_extension in ['.c']:
                compiler = 'clang'
                compiler_flags = ''
                fixed_code_file = 'fixed_memory_safety_code.c'
            elif file_extension in ['.cpp']:
                compiler = 'clang++'
                compiler_flags = '-std=c++11'
                fixed_code_file = 'fixed_memory_safety_code.cpp'
            else:
                raise ValueError("Unsupported file type. Please select a .c or .cpp file.")

            #Runs Clang Static Analyzer
            self.run_clang_static_analyzer(self.sourceFile, clang_output_file, compiler)

            #Runs AddressSanitizer
            self.run_address_sanitizer(self.sourceFile, asan_output_file, compiler)

            #Reads Clang Static Analyzer and AddressSanitizer outputs
            with open(clang_output_file, 'r') as file:
                clang_output = file.read()

            with open(asan_output_file, 'r') as file:
                asan_output = file.read()

            #Detects and fixes memory safety vulnerabilities
            memory_safety_output = self.detect_and_fix_memory_vulnerabilities(source_code, clang_output, asan_output)

            #Outputs the fixed code
            with open(fixed_code_file, 'w') as file:
                file.write(memory_safety_output)

            # Compiles the fixed code
            self.compile_code_with_clang(fixed_code_file, executable_file, compiler, compiler_flags)

            # Gets optimized code and optimization details from ChatGPT
            optimization_output = self.get_optimized_code(memory_safety_output)

            #Outputs the optimized code
            with open(optimized_code_file, 'w') as file:
                file.write(optimization_output)

            #Merges memory safety and optimization summaries into final summary file
            with open(final_summary_file, 'w') as file:
                file.write("// Memory Safety Summary:\n\n")
                file.write(memory_safety_output)
                file.write("\n\n// Optimization Summary:\n\n")
                file.write(optimization_output)

            #Displays results
            with open(final_summary_file, 'r') as file:
                self.resultText.setPlainText(file.read())

            #Clean up
            os.remove(executable_file)
            os.remove(clang_output_file)
            os.remove(asan_output_file)

            QMessageBox.information(self, "Success", "Analysis and Optimization Completed Successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def run_clang_static_analyzer(self, source_file, output_file, compiler):
        analyze_command = [compiler, '--analyze', source_file, '-o', output_file]
        subprocess.run(analyze_command, check=True)

    def run_address_sanitizer(self, source_file, output_file, compiler):
        compile_command = [compiler, '-fsanitize=address', '-o', 'a.out', source_file]
        subprocess.run(compile_command, check=True)
        run_command = ['./a.out']
        with open(output_file, 'w') as output:
            result = subprocess.run(run_command, capture_output=True, text=True)
            output.write(result.stdout + result.stderr)
        os.remove('a.out')

    def compile_code_with_clang(self, source_file, output_file, compiler, flags):
        compile_command = [compiler, flags, '-O2', '-o', output_file, source_file]
        subprocess.run(compile_command, check=True)

    def get_optimized_code(self, source_code):
        prompt = (
            "/*\n"
            "Optimize the following C/C++ code:\n\n"
            "Code:\n"
            f"{source_code}\n\n"
            "Please provide the optimized code followed by a brief summary of the optimizations performed. "
            "Use the following format:\n\n"
            "// Optimized Code:\n\n"
            "<optimized code here>\n\n"
            "// Optimization Summary:\n\n"
            "<1. (Optimization name here): (explanation of what was done)>\n"
            "<2. (Optimization name here): (explanation of what was done)>\n"
            "*/"
        )

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        response_content = response.choices[0].message.content.strip()
        return response_content

    def detect_and_fix_memory_vulnerabilities(self, source_code, clang_output, asan_output):
        prompt = (
            "/*\n"
            "Identify and fix any memory safety vulnerabilities in the following C/C++ code. Use the output from Clang Static Analyzer and AddressSanitizer to help identify issues.\n\n"
            "Code:\n"
            f"{source_code}\n\n"
            "Clang Static Analyzer Output:\n"
            f"{clang_output}\n\n"
            "AddressSanitizer Output:\n"
            f"{asan_output}\n\n"
            "Please provide the fixed code followed by a brief summary of the memory safety vulnerabilities found and fixed. "
            "Use the following format:\n\n"
            "// Fixed Code:\n\n"
            "<fixed code here>\n\n"
            "// Memory Safety Summary:\n\n"
            "<1. (Vulnerability fixed name here): (explanation of what was done)>\n"
            "<2. (Vulnerability fixed name here): (explanation of what was done)>\n"
            "*/"
        )

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        response_content = response.choices[0].message.content.strip()
        return response_content

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CodeAnalyzerApp()
    ex.show()
    sys.exit(app.exec_())
