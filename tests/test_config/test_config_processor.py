import yaml

from mokuwiki.wiki import Wiki

from utils import Markdown


def test_config_replace(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()
    
    wiki_config = f"""
        name: test
        target: dummy
        preprocessing:
          - converter:
              label: 'This is ${{namespace}}'
              vars: ['$namespace A', '$namespace B']
              maps:
                key1: ${{namespace}}/1
                key2: ${{namespace}}/2 $broken_css
        namespaces:
          ns1:
              preprocessing:
                - copy content/$namespace/$media_dir/ my_site/$namespace/$media_dir
              content: {ns1}
              toc: 1
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    
    ns1 = wiki.namespaces['ns1']

    expect = yaml.safe_load("""
          - converter:
              label: 'This is ns1'
              vars: ['ns1 A', 'ns1 B']
              maps:
                key1: ns1/1
                key2: ns1/2 .broken
          - copy content/ns1/images/ my_site/ns1/images
          """)
    
    actual = ns1.config.preprocessing
    
    assert expect == actual
