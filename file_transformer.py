import argparse
import sys

DEFAULT_TO_BINARY_MODE = False

class _FileTransformer(object):
    
    def __init__(self,
            parser=None,
            args_to_parse=None,
            pre_parse_hook=None,
            post_parse_hook=None,
            positional_args=True
            ):
        self.parser = parser or argparse.ArgumentParser()

        self.args_to_parse = args_to_parse
        
        if positional_args:
            self.parser.add_argument('files', nargs=argparse.REMAINDER)
        
        self.parser.add_argument('-i', '--input', metavar='FILE')
        self.parser.add_argument('-o', '--output', metavar='FILE')
        self.parser.add_argument('-q', '--quiet', action='store_true')
        
        if pre_parse_hook:
            pre_parse_hook(self.parser)
        
        self.args = self.parser.parse_args(args=args_to_parse)
        if not positional_args:
            self.args.files = []
        
        if post_parse_hook:
            post_parse_hook(self.parser, self.args)
        
        self.verbose = not self.args.quiet
        
        if len(self.args.files) >= 3:
            self.exit(1, "Too many inputs!")
        
        if self.args.files and (self.args.input or self.args.output):
            self.exit(1, "Can't specify both args and options")
        
    def exit(self, code, message=None):
            if not self.verbose or not message:
                message = None
            else:
                message = message + '\n'
            self.parser.exit(code, message)
    
    def _open_file(self, name, mode):
        try:
            return open(name, mode, 1)
        except Exception as e:
            self.exit(2, "Could not open file {}: {}".format(name, e))
    
    def _open_input_stream(self, binary=None):
        if binary is None:
            binary = DEFAULT_TO_BINARY_MODE
        mode = 'rb' if binary else 'r'
        if self.args.input:
            input_stream = self._open_file(self.args.input, mode)
        elif len(self.args.files) >= 1:
            input_stream = self._open_file(self.args.files[0],mode)
        else:
            input_stream = sys.stdin
        return input_stream
    
    def _open_output_stream(self, binary=None):
        if binary is None:
            binary = DEFAULT_TO_BINARY_MODE
        mode = 'wb' if binary else 'w'
        if self.args.output:
            output_stream = self._open_file(self.args.output, mode)
        elif len(self.args.files) == 2:
            output_stream = self._open_file(self.args.files[1], mode)
        else:
            output_stream = sys.stdout
        return output_stream
    
    def run(self,
            processor,
            loader=None,
            dumper=None):

        input_binary = DEFAULT_TO_BINARY_MODE
        output_binary = DEFAULT_TO_BINARY_MODE
        if hasattr(processor, 'binary'):
            input_binary = getattr(processor, 'binary')
            output_binary = getattr(processor, 'binary')
        if hasattr(loader, 'binary'):
            input_binary = getattr(loader, 'binary')
        if hasattr(dumper, 'binary'):
            output_binary = getattr(dumper, 'binary')

        try:
            with self._open_input_stream(binary=input_binary) as input_stream:
                if loader:
                    input = loader(input_stream, self.args)
                else:
                    input = input_stream.read()
            
            output = processor(input, self.args)
                    
            with self._open_output_stream(binary=output_binary) as output_stream:
                if dumper:
                    dumper(output, output_stream, self.args)
                else:
                    output_stream.write(output)
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exception(*sys.exc_info())
            self.exit(3, str(e))

        self.exit(0)

    def stream(self, processor):
        binary = getattr(processor, 'binary', DEFAULT_TO_BINARY_MODE)
        try:
            with self._open_input_stream(binary=binary) as input_stream, self._open_output_stream(binary=binary) as output_stream:
                processor(input_stream, output_stream, self.args)
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exception(*sys.exc_info())
            self.exit(3, str(e))

        self.exit(0)

def main(processor,
        loader=None,
        dumper=None,
        parser=None,
        args=None,
        pre_parse_hook=None,
        post_parse_hook=None,
        positional_args=True):
    """Setup the appropriate input and output based on the command line args and
    run the given callable processor. The basic arguments allow the program to be
    called in the following ways:
    
    prog [-i input_file] [-o output_file]
    prog input_file [-o output_file]
    prog input_file output_file
    
    The latter two formats can be disabled by specifying positional_args=False
    
    If there is no input or output file given, it will read from stdin or write
    to stdout, respectively.
    
    An argparse.ArgumentParser can be provided, as can the arguments to be parsed.
    
    By default, the input is read into a bytestring. If a callable loader is
    provided, it is called with the file-like input stream and the parsed args
    object and should return the input to pass to the processor.
    
    The processor is called with the input (bytestring or output from loader) and
    the parsed args object, and should return the output to write to the file,
    normally a bytestring.
    
    If the output of the processor can't be directly written to the output stream,
    a callable dumper can be provided, which takes the output from processor, the
    output stream, and the parsed args object.
    
    By default, the files are opened in text mode. If binary is desired,
    the module field DEFAULT_TO_BINARY_MODE can be set to true. If processor,
    loader, or dumper have an attribute named binary, that will be used instead.

    Errors are printed to stdout unless the -q flag is given.
    """ 
    
    xformer = _FileTransformer(
        parser=parser,
        args_to_parse=args,
        pre_parse_hook=pre_parse_hook,
        post_parse_hook=post_parse_hook,
        positional_args=positional_args)
    
    return xformer.run(processor, loader=loader, dumper=dumper)

def streaming_main(processor,
        parser=None,
        args=None,
        pre_parse_hook=None,
        post_parse_hook=None,
        positional_args=True):
    """Identical to main(), but the processor takes as input the file-like
    input stream and output stream, and the parsed args object."""
    
    xformer = _FileTransformer(
        parser=parser,
        args_to_parse=args,
        pre_parse_hook=pre_parse_hook,
        post_parse_hook=post_parse_hook,
        positional_args=positional_args)
    
    return xformer.stream(processor)

def _get_lib(lib, default_lib_name):
    if lib:
        return lib
    import importlib
    return importlib.import_module(default_lib_name)

def get_io_functions_from_lib(lib, load_func_name='load', dump_func_name='dump', load_kwargs={}, dump_kwargs={}):
    """Helper to create loader and dumper functions for libraries"""
    def loader(input_stream, args):
        return getattr(lib, load_func_name)(input_stream, **load_kwargs)
    def dumper(output, output_stream, args):
        return getattr(lib, dump_func_name)(output, output_stream, **dump_kwargs)
    return loader, dumper

def get_pickle_io(load_kwargs={}, dump_kwargs={}, picklelib=None):
    """Returns a loader and dumper for Pickle files"""
    return get_io_functions_from_lib(_get_lib(picklelib, 'pickle'), 'load', 'dump', load_kwargs=load_kwargs, dump_kwargs=dump_kwargs)

def get_json_io(load_kwargs={}, dump_kwargs={}, jsonlib=None):
    """Returns a loader and dumper for JSON"""
    return get_io_functions_from_lib(_get_lib(jsonlib, 'json'), 'load', 'dump', load_kwargs=load_kwargs, dump_kwargs=dump_kwargs)

def get_yaml_io(load_kwargs={}, dump_kwargs={}, safe=False, yamllib=None):
    """Returns a loader and dumper for YAML"""
    load_func_name = 'safe_load' if safe else 'load'
    dump_func_name = 'safe_dump' if safe else 'dump'

    loader, dumper = get_io_functions_from_lib(_get_lib(yamllib, 'yaml'), load_func_name, dump_func_name, load_kwargs=load_kwargs, dump_kwargs=dump_kwargs)
    dumper.binary = False
    return loader, dumper
