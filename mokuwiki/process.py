import logging
import shutil
import subprocess

from pathlib import Path

# TODO how do we report on errors?

class Processor:
    # will have abstract process()?

    def __init__(self) -> None:        
        pass
        
    def process(self, config: list[dict]):
        """config is local, either pre or post
        """
        
        for processor in config:
            logging.debug(f"running processor: {processor}")

            input = files = None

            if isinstance(processor, str):
                # if any args has a space this will fail, use list method instead
                command = processor.split(' ')
                                
                try:
                    command = self._glob_args(command)
                except ValueError:
                    logging.error(f"processing '{processor}': had no files to process")
                    continue
                    
            elif isinstance(processor, list):
                # by pre-splitting the command this can handle spaces in args
                command = processor

                try:
                    command = self._glob_args(command)
                except ValueError:
                    logging.error(f"processing '{processor}': had no files to process")
                    continue                
                
            elif isinstance(processor, dict):
                # breakpoint()
                exec = list(processor.keys())[0]
                args = list(processor.values())[0]
            
                # assemble string then use shlex.split() or assemble list of args? for subprocess?
                input, files, args = self._build_args(args)
            
                command = [exec]
                command.extend(args)
            else:
                logging.error(f"unknown type for processing: '{processor}'")
                continue
            
            # NOTE at this point could have list of command string
            # that are all globbed etc, and just execute one by one
            # i.e. one "command" per file    
            
            # TODO catch exceptions here and print as errors, print cmd output as debug/info
            if files:
                # asumes foo/bar/*.md
                # TODO now dynamically extend command for each input path and do param subst on args
                for file in Path(files).parent.glob(Path(files).name):
                                        
                    # replace output file marker
                    cmd = [c.replace('@', file.stem) if '@' in c else c for c in command]

                    if not input:
                        cmd.append(str(file))
                    elif input.endswith('='):
                        cmd.append(f"{input}{file}")
                    else:
                        cmd.extend([input, str(file)])
                    
                    output = subprocess.run(cmd, shell=False, universal_newlines=True, encoding='utf-8')     
            else:
                # if not specified a path the glob command line                
                output = subprocess.run(command, shell=False, universal_newlines=True, encoding='utf-8')
    
    def _glob_args(self, command):
        cmd = []
        
        for c in command:
            if '*' in c:
                files = list(Path(c).parent.glob(Path(c).name))
                
                if not files:
                    raise ValueError
                
                cmd.extend(files)
            else:
                cmd.append(c)
        
        return cmd

    def _build_args(self, config: dict) -> tuple:
        """Convert a configuration dictionary into into list of arguments suitable for
        use by `subprocess`. The conversion is fairly straightforward, but there are
        some caveats:
        
        -  A key that ends in '=' is assumed to be an argument is assumed to be one of the type "--arg=val",
        otherwise "--arg val".
        -  A key that starts with '<' is treated as an "input" path specification to be iterated
        over and separated out of the returned argument list to be returned as `input_arg`; the value of 
        that argument is returned as `input_path` (the value '>' is removed from the argument, which is
        then processed as  descibed below). It is assumed that the  `input_path` is of the 
        form "path/to/files/*.md". 
        -  Any value that contains the string '${@}' (or "$@") will have it interpreted as the 
        basename of the input file (as determined by the iteration over the input arguments)
        -  Keys can start with '-' or '--' as required by the argument.
        -  A key that starts with '_' just has the value included, i.e. the underscore is a way
        of adding multiple positional arguments.
        -  Values that are lists are repeated for each element of the list.
        -  Values that are dictionaries are repeated as key=value pairs.
        -  Arguments with no values are indicated with a 'null' or '~' value.
        
        For example, the config (for pandoc):
        
            <: build/NS/mokuwiki/*.md
            --output=: home/sites/wiki/NS/${@}.html
            --template=: ./template.html
            --table-of-contents=: true
            --standalone: null
            --include-in-header=: ['file1', 'file2']
            -V: 
                site-name: My site
                site-icon: icon.png
            -M:
                processed: yes
  
        will be converted into the returned varaibles:
        
            input_path: build/NS/mokuwiki/*.md
            input_arg: ''
            args:
                ["--output=home/sites/wiki/NS/@.html",
                 "--template=./template.html',
                 "--table-of-contents=true',
                 "--standalone",
                 "--include-in-header=file1",
                 "--include-in-header=file2",
                 "-V site-name="My site"",
                 "-V site-icon=icon.png"
                 "-M processed=yes"]
        
        Do NOT change the ORDER of the returned `args` array.
        """
        
        args = []
        input_path = None
        input_arg = None
        
        for key, val in config.items():
            sep1, sep2 = ('', ':') if key.endswith('=') else (' ', '=')
            
            if key.startswith('<'):
                if input_arg:
                    logging.error(f"multiple input paths specified in process config, '{key}'")
                
                input_arg = key[1:]
                input_path = val
                continue

            # add value without argument
            if key.startswith('_'):
                args.append(val)
                continue

            if val is None:
                # e.g. --standalone
                args.append(f"{key}")
            
            elif isinstance(val, str):
                # e.g. --template=./template.html
                args.append(f"{key}{sep1}{val}")
            
            elif isinstance(val, bool):
                # e.g. --table-of-contents=true
                args.append(f"{key}{sep1}{str(val)}")
            
            elif isinstance(val, list):
                args.extend([f"{key}{sep1}{v}" for v in val])
        
            elif isinstance(val, dict):
                args.extend([f"{key}{sep1}{k}{sep2}{v}" for k, v in val.items()])

            else:
                pass

        return input_arg, input_path, args
