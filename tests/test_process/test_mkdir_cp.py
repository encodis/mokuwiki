import yaml
from pathlib import Path

from mokuwiki.wiki import Wiki

from utils import Markdown


def test_copy_support_files(tmp_path):
    
    content = tmp_path / 'content'
    content.mkdir()
    
    ns1 = content / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   Body text 1
                   """)
    
    images = ns1 / 'images'
    images.mkdir()
    
    png1 = images / 'fake.png'
    Markdown.write(png1,
                   """
                   FAKE IMAGE
                   """)

    css1 = ns1 / 'local.css'
    Markdown.write(css1,
                   """
                   html {
                     box-sizing: border-box;
                     font-size: 62.5%;
                     height: 100%;
                   }
                   """)
    
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    
    wiki_config = f"""
        name: test
        site_dir: {site_dir}
        build_dir: {tmp_path}/build
        preprocessing:
          - mkdir -p $site_dir/$namespace/images
          - cp -R {images}/ $site_dir/$namespace/images/
          - cp {tmp_path}/content/$namespace/local.css $site_dir/$namespace/
        namespaces:
          ns1:
              content: {ns1}
        """
    
    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()
    
    image1 = site_dir / 'ns1' / 'images' / 'fake.png'
    assert image1.exists()
    
    actual1 = site_dir / 'ns1' / 'local.css'
    assert actual1.exists()
    
def test_copy_support_files_glob(tmp_path):
    
    content = tmp_path / 'content'
    content.mkdir()
    
    ns1 = content / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   Body text 1
                   """)
    
    images = ns1 / 'images'
    images.mkdir()
    
    png1 = images / 'fake.png'
    Markdown.write(png1,
                   """
                   FAKE IMAGE
                   """)

    css1 = ns1 / 'local.css'
    Markdown.write(css1,
                   """
                   html {
                     box-sizing: border-box;
                     font-size: 62.5%;
                     height: 100%;
                   }
                   """)
    
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    
    wiki_config = f"""
        name: test
        site_dir: {site_dir}
        build_dir: {tmp_path}/build
        preprocessing:
          - mkdir -p $site_dir/$namespace/images
          - cp {images}/* $site_dir/$namespace/images/
          - cp {tmp_path}/content/$namespace/local.css $site_dir/$namespace/
        namespaces:
          ns1:
              content: {ns1}
        """
    
    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()
    
    image1 = site_dir / 'ns1' / 'images' / 'fake.png'
    assert image1.exists()