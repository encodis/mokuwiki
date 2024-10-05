import shutil
import subprocess

from pathlib import Path

from mokuwiki.config import NamespaceConfig



class Processor:
    # will have abstract process()?

    def __init__(self, config: NamespaceConfig) -> None:
        
        # config is ns_config.preprocessing or .postprocessing
        self.config = config
        
        self.built_in = {
            'copy_support_files': self.copy_support_files,
        }

    def preprocess(self):
        self.process(self.config.preprocessing)
        
    def postprocess(self):
        self.process(self.config.postprocessing)
        
    def process(self, config: list[dict]):
        """config is local, either pre or post
        """
        
        for processor in config:
            
            exec = list(processor.keys())[0]
            args = list(processor.values())[0]
            
            if processor in self.built_in.keys():
                self.built_in[processor](args)
                continue

            # assemble string then use shlex.split() or assemble list of args? for subprocess?
            args, paths = self._build_args(args)
            
            command = [exec]
            command.extend(args)
            
            if paths:
                for file in Path(paths).glob('*.md'):
                    subprocess.run(command.extend([file]), shell=True, universal_newlines=True, encoding='utf-8')     
            else:
                subprocess.run(command, shell=True, universal_newlines=True, encoding='utf-8')
    
    def copy_support_files(self, args):
        """Copies indicated files to site_dir/namespace, use values in NS config
        In this case the args are lists of path specs so don't need to build_args
        
        e.g.
        copy_files: 
            source: ['images/*', '*.css', '*.js']
            target: $site_dir/$namespace
            
            which will have been expanded
        
        """
        
        source = args['source']
        target = args['target']
        
        # NOTE as content_dirs is looped over, may overwrite support files
        
        for content_dir in self.config.content_dirs:
            for path in source:
                path = content_dir / path
            
                shutil.copytree(path, target, dirs_exist_ok=True)

    def _build_args(self, config: dict) -> list:
        """Convert a configuration dictionary into into list of arguments suitable for
        use by `subprocess`. The conversion is fairly straightforward, but there are
        some caveats:
        
        -  A key with the value '@' is treated as a path specification to be iterated over and is not included
        as an argument, see XXX()
        -  A key that starts with '_' just has the value included
        -  Values that are lists are repeated
        -  Values that are dictionaries are repeated as key=value pairs
        -  Arguments with no values are indicated with a 'null' or '~' value
        
        For example, the config (for pandoc):
        
            @: build/NS/pages
            output: home/sites/wiki
            template: ./template.html
            table-of-contents: true
            standalone: ~
            include-in-header: ['file1', 'file2']
            variable: 
                site-name: My site
                site-icon: icon.png
  
        will be converted into the list:
        
            ["--output=home/sites/wiki",
             "--template=./template.html',
             "--table-of-contents=true',
             "--standalone",
             "--include-in-header=file1",
             "--include-in-header=file2",
             "--variable=site-name:"My site"",
             "--variable=site-icon:icon.png"
        
        """
        
        def _escape(string: str) -> str:
            if ' ' in string:
                return f'"{string}"'
            
            return string
        
        args = []
        paths = None
        
        for key, val in config.items():
            
            # path spec
            if key == '@':
                paths = val 

            # add value without argument
            if key.startswith('_'):
                args.append(_escape(val))
                continue

            if isinstance(val, str):
                # TODO if val is "true" then lower case
                if val in ['null', '~']:
                    args.append(f"--{key}")
                else:
                    args.append(f"--{key}={_escape(val)}")
                
            if isinstance(val, list):
                args.extend([f"--{key}={_escape(v)}" for v in val])
        
            if isinstance(val, dict):
                args.extend([f"--{key}={_escape(v)}:{_escape(k)}" for v, k in val.items()])

        return args, paths
