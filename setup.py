from setuptools import setup, find_packages

setup(
    name="notefy_ia",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'pdfminer.six',
        'PyPDF2',
        'pytesseract',
        'google-cloud-vision'
    ]
)
