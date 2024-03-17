# Compilers Course Project

Project work for the course Compilers.

## Running the compiler

The compiler is designed to produce x86-64 Linux assembly code. To run it on other kind of systems, the project uses a Dockerfile.

Assuming Docker is installed, the interactive linux shell can be started with:

`docker build -t compilers-dev:latest . && docker run -it --rm -v .:/project compilers-dev:latest`

In case there is a warning about incompatible image's platform, try the following command instead (running the Dockerfile on MacBook with M-chip requires defining the platform, although app still shows warning):

`docker build --platform linux/amd64 -t compilers-dev:latest . && docker run --platform linux/amd64 -it --rm -v .:/project compilers-dev:latest`

Make sure Docker does not try to load old build from cache. For making a fresh build, remove old image, containers, and builds (e.g. from app) and run `docker builder prune`to clean up build cache (WARNING: removes all builds from cache).

To exit the session, press `ctrl+d`.

### Compile and run the test assembly program

Compile asmprogram.s with `gcc -g -no-pie -o asmprogram asmprogram.s`.

Run the asmprogram with `./asmprogram`. Input a number, and the program doubles it and prints out the result.

### Running code on the compiler

Write code into the file test_code, and run command `./compiler.sh compile test_file && ./compiled_program`
