# file_transformer

A utility function for creating Python scripts that expect to turn one file
into another, or use stdin/stdout as part of a pipeline. The basic arguments 
allow the program to be called in the following ways:

```
prog [-i input_file] [-o output_file]
prog input_file [-o output_file]
prog input_file output_file
```

The latter two formats can be disabled by specifying positional_args=False

If there is no input or output file given, it will read from stdin or write
to stdout, respectively.

If the processing to be done can operate on the entire contents of the files,
`file_transformer.main` is the way to go. It takes a callable, which takes the
input bytestring and the parsed args object, and returns the bytestring to be
written to the output. The loading and dumping can be customized by providing
callables for loader and dumper (for example, to read in a JSON file to a Python
dict).

If the processing should take place on the file-like streams themselves,
`file_transformer.streaming_main` takes a callable that takes the input stream,
output stream, and parsed args object.

An argparse.ArgumentParser can be provided, as can the arguments to be parsed.
When doing this, it can be useful to also provide a `post_parse_hook` callable
(that takes the parser and parsed args object) to interpet the args, take action
on them, perhaps adding to the args object, and error out if needed before
reaching the I/O part.

By default, the files are opened in text mode. If binary is desired,
the module field DEFAULT_TO_BINARY_MODE can be set to true. If processor,
loader, or dumper have an attribute named binary, that will be used instead.

Errors are printed to stdout unless the -q flag is given.