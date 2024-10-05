import yaml
from pathlib import Path

from mokuwiki.wiki import Wiki

def test_ns_processor_replace(tmp_path):
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
            """)
    
    actual = ns1.config.preprocessing
    
    assert expect == actual
    