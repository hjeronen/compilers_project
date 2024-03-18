# Compilers Course Project

Project work for the course [Compilers spring 2024](https://hy-compilers.github.io/spring-2024/).

## Running the project

The compiler is designed to produce x86-64 Linux assembly code. To run it on other kind of systems, the project uses a Dockerfile. Note that there are separate dockerfiles for development and for running the container without volumes.

### For development

Assuming Docker is installed and project files are downloaded, the interactive linux shell can be started from the root directory with:

`docker build -f Dockerfile.dev -t compilers-dev:latest . && docker run -it --rm -v .:/compilers-project compilers-dev:latest`

In case there is a warning about incompatible image's platform, try the following command instead (running the Dockerfile on MacBook with M-chip requires defining the platform, although app still shows warning):

`docker build --platform linux/amd64 -f Dockerfile.dev -t compilers-dev:latest . && docker run --platform linux/amd64 -it --rm -v .:/compilers-project compilers-dev:latest`

Make sure Docker does not try to load old build from cache. For making a fresh build, remove old image, containers, and builds (e.g. from app) and use flag `--no-cache` or run `docker builder prune` to clean up build cache (WARNING: removes all builds from cache).

For more trouble shooting check Notes below.

To exit the session, press `ctrl+d`.

### For standalone container

To run without volume binding, build image with:

`docker build --platform linux/amd64 -f Dockerfile.compiler -t compilers-project:latest .`

And run an interactive container with:

`docker run --platform linux/amd64 -it --rm compilers-project:latest`

## Running code on the compiler

If running the compiler with Docker, once the interactive shell is open and working, use nano for text editing.

Write code into the file `test_code`, and run command `./compiler.sh compile test_file && ./compiled_program`

Available commands:

- `test_prints` prints out the results from each compiler stage for given test code
- `interpret`runs the interpreter and the typechecker, and prints out results from both
- `ir`runs the IR generator and prints out the commands
- `asm`runs the assembly generator and prints out the assembly instructions
- `compile`compiles the given test code into file 'compiled_program'
- `end`runs the end-to-end test cases, defined in directory 'test_programs'

Check language syntax from [the course page](https://hy-compilers.github.io/spring-2024/language-spec/).

To run unit tests (for tokenizer, parser, interpreter and typechecker), use command `./check.sh`.

## Notes

- Poetry does not know how to run the project if the source directory does not match the name given in pyproject.toml - the root directory should be 'compilers-project' in pyproject.toml, Dockerfile and docker run command (given above)

- Above error will still exist if PYTHONPATH is not set to '/compilers-project/src'

- To check and set PYTHONPATH run:

  - `echo $PYTHONPATH`
  - `export PYTHONPATH="/compilers-project/src"`

- For some reason, during manual testing variables are saved in symtab, but in end-to-end tests they are saved to root_types - not sure why, fixed by copying root_types separately for each test case
