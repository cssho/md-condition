from setuptools import setup, find_packages

setup(
    name='md-condition',
    version='0.1.5',
    packages=find_packages(),
    url='https://github.com/cssho/md-condition',
    license='MIT',
    install_requires=['Markdown'],
    author='Sho Sato',
    author_email='rizeupbass@gmail.com',
    description='Python-Markdown extension to use conditional compilations',
    classifiers = [
        "License :: OSI Approved :: MIT License"
  ]
)