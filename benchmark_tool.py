import time
import tracemalloc
import sys
from PyQt5.QtWidgets import QApplication
from Automate import CodeAnalyzerApp

def benchmark_phase(phase_name, func, *args, **kwargs):
    tracemalloc.start()
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{phase_name} - Execution Time: {end_time - start_time:.2f} seconds")
    print(f"{phase_name} - Current Memory Usage: {current / 10**6:.2f} MB")
    print(f"{phase_name} - Peak Memory Usage: {peak / 10**6:.2f} MB")
    return result

def run_benchmark():
    app = QApplication(sys.argv)
    analyzer = CodeAnalyzerApp()
    analyzer.show()

    # Simulate loading a file into the application
    # Here, you should provide a path to a test file
    test_file_path = 'test2.c'  # Replace with a valid path to a test file
    with open(test_file_path, 'r') as file:
        source_code = file.read()

    analyzer.sourceText.setPlainText(source_code)
    analyzer.sourceFile = test_file_path

    # Ensure the UI is ready before starting the benchmark
    # Wait for the application to finish initializing
    QApplication.processEvents()

    # Benchmark the analyze and optimize phase
    benchmark_phase("Analyze and Optimize", analyzer.analyzeAndOptimize)

    # Clean up if necessary

if __name__ == "__main__":
    run_benchmark()
