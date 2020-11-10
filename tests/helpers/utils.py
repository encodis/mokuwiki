import yaml
import configparser


def create_wiki_config(file_handle, default, *namespaces):
    """Create wiki config file for tests

    Args:
        file_handle ([type]): [description]
        default (dict): [description]
    """
    config = configparser.ConfigParser()

    if default:
        config['DEFAULT'] = default
    else:
        config['DEFAULT'] = {'name': 'test wiki',
                             'target': '.',
                             'media_dir': 'images',
                             'broken_css': '.broken',
                             'tags_css': '.tags',
                             'custom_css': '.smallcaps',
                             'search_index': False,
                             'search_fields': 'title,alias,tags,summary,keywords',
                             'search_prefix': '',
                             'meta_links': True,
                             'meta_fields': 'tags',
                             'noise_words': ''}

    if len(namespaces) == 0:
        config['ns1'] = {'name': 'ns1',
                         'alias': 'ns1',
                         'path': 'ns1'}
    else:
        for namespace in namespaces:
            if 'name' not in namespace:
                continue

            config[namespace['name']] = namespace

    file_handle.write(config)


def create_markdown_file(file_handle, meta, body):
    contents = create_markdown_string(meta, body)

    file_handle.write(contents)


def create_markdown_string(meta, body):

    contents = '---\n'

    for k, v in meta.items():
        contents += f'{k}: {v}\n'

    contents += '...\n' + body + '\n'

    return contents


def compare_markdown_content(file1, file2, compare='both'):
    """Compare Markdown file metadata

    Args:
        file1 (str): first file contents
        file2 (str): second file contents
        compare (str): compare 'meta', 'body' or 'both'

    Returns:
        True if metadata are logically the same, False otherwise
    """

    if '...' in file1:
        meta1, _, body1 = file1.partition('...\n')
    else:
        return False

    if '...' in file2:
        meta2, _, body2 = file2.partition('...\n')
    else:
        return False

    if compare in ['meta', 'both']:
        try:
            meta1 = yaml.safe_load(meta1)
        except yaml.YAMLError:
            print(f'Error in metadata for file 1')
            return False

        try:
            meta2 = yaml.safe_load(meta2)
        except yaml.YAMLError:
            print(f'Error in metadata for file 2')
            return False

        if meta1 != meta2:
            return False

    if compare in ['body', 'both']:
        if body1 != body2:
            return False

    return True
