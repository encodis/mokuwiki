"""Convert a folder of Markdown documents, replacing inter-page link and tag markup with Markdown links and lists

"""

from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='mokuwiki',
      version='1.0.1',
      description='Convert a folder of Markdown documents, replacing inter-page link and tag markup with Markdown links and lists',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/encodis/mokuwiki',
      author='Philip Hodder',
      author_email='philip.hodder@encodis.com',
      license='MIT',
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Markup',
        'Topic :: Utilities'
      ],
      keywords='markdown wiki converter',
      py_modules=['mokuwiki'],
      install_requires=[
        'pyyaml>=5.1'
      ],
      entry_points={
        'console_scripts': [
            'mokuwiki = mokuwiki:main',
        ],
      }
      )
