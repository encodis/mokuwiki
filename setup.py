from distutils.core import setup

setup(name='mokuwiki',
      version='1.0.0',
      description='Convert a folder of Markdown documents, replacing inter-page link and tag markup with Markdown links and lists',
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
      keywords='markdown wiki converter'
      py_modules=['mokuwiki'],
      )