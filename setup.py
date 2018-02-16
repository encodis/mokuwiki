from distutils.core import setup

setup(name='mokuwiki',
      version='${version.number}',
      description='Convert a folder of Markdown documents, replacing inter-page link and tag markup with Markdown links and lists',
      author='Philip Hodder',
      author_email='philip.hodder@encodis.com',
      url='https://github.com/encodis/mokuwiki',
      py_modules=['mokuwiki'],
      )