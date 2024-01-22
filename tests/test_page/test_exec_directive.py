from pathlib import Path

from mokuwiki.page import Page

from utils import Markdown


def test_process_exec_command(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = source / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   %% ls -1 -d "$PWD"/READ* %%
                   """)

    page = Page(file1, None)
    page.process_directives()
        
    page.save(target / 'page_one.md')

    actual1 = target / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = f"""
    ---
    title: Page One
    ...
    {Path('.').absolute() / 'README.md'}
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_exec_command_pipe(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = source / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   %% find "$PWD" -name READ*  | grep -v cache %%
                   """)

    page = Page(file1, None)
    page.process_directives()
        
    page.save(target / 'page_one.md')

    actual1 = target / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = f"""
    ---
    title: Page One
    ...
    {Path('.').absolute() / 'README.md'}
    """
    
    assert Markdown.compare(expect1, actual1)
