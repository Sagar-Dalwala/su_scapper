from setuptools import setup, find_packages

setup(
    name="enhanced-pdf-to-docx",
    version="1.0.0",
    description="Convert PDF to DOCX with preserved formatting, similar to ilovepdf",
    author="PDF Tools Team",
    packages=find_packages(),
    install_requires=[
        "PyPDF2>=3.0.1",
        "python-docx>=1.0.1",
        "pdf2docx>=0.5.6",
        "pandas>=2.0.3",
    ],
    entry_points={
        "console_scripts": [
            "pdf-to-docx=enhanced_pdf_to_docx:main",
            "batch-pdf-to-docx=enhanced_pdf_to_docx.batch:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
) 