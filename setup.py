import os
from setuptools import setup, find_packages


def long_desc():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root_dir, 'README.md')
    with open(path, 'r') as file:
        return file.read()


setup(
    name='microtest-framework',
    version='1.0.0',
    
    author='Valtteri Rajalainen',
    author_email='rajalainen.valtteri@gmail.com',
    
    description='Simple but powerful testing framework for Python',
    long_description=long_desc(),
    long_description_content_type='text/markdown',
    
    url='https://github.com/varajala/microtest',
    project_urls={
        "Documentation": "https://varajala.github.io/microtest/docs/",
    },
    
    python_requires='>=3.7',
    packages=find_packages(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Unit",
        "Topic :: Utilities",
    ],
)
